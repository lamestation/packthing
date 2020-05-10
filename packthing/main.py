import argparse
import importlib
import os
import pkgutil
import pprint
import shutil
import signal
import sys

import yaml

from . import __version__
from . import builders
from . import importer
from . import packagers
from . import util
from . import vcs


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

packagelist = importer.get_modulelist(packagers)
packagelist.append("src")
packagelist.append("clean")

_platform = util.get_platform()


class Packthing:
    def __init__(self, repofile, targetname):
        self.configure(repofile, targetname)

    @util.headline
    def configure(self, repofile, targetname):
        self.repofile = repofile
        self.targetname = targetname
        self.config = dict()

        try:
            config = yaml.load(open(self.repofile))
        except IOError:
            util.error(
                "'"
                + self.repofile
                + "' not found; please specify a valid packthing file"
            )

        # build tree of included targets
        self.target = importer.get_module(packagers, self.targetname)
        self.targetnames = []
        for t in importer.list_module_hierarchy(self.target):
            self.targetnames.append(t.__module__.split(".")[-1])
        self.targetnames = [x for x in self.targetnames if not x.startswith("_")]

        self.config.update(self.build_config(config))

        # package
        if not "package" in self.config:
            self.config["package"] = config["name"].lower()

        # master
        if not "master" in self.config:
            for path in list(self.config["repos"].keys()):
                r = self.config["repos"][path]

                if path == self.config["name"] or path == self.config["package"]:
                    self.config["master"] = path
                    print("Using", self.config["master"], "as master project.")
                    break

            if not "master" in self.config:
                util.error("No master repository defined in", repofile)

        # repo specific stuff

        if not "repos" in self.config:
            util.error("No repository configured in", repofile)

        # add platform and overrides

        for k in list(_platform.keys()):
            self.config.update(self.add_key(_platform, k))

        importer.require(self.target)

        # ensure required keys are present

        for k in importer.required_keys(self.target):
            self.config.update(self.add_key(self.config, k))

        # add optional keys

        for k in list(config.keys()):
            if not k in ["repos", "files", "target"]:
                self.config[k] = config[k]

        # print final keys

        for k in list(self.config.keys()):
            if not k in ["repos", "files"]:
                print("%20s: %s" % (k, self.config[k]))

    #        pp = pprint.PrettyPrinter(indent=4)
    #        pp.pprint(self.config)

    def get_repo_from_executable_name(self, executable):
        for r in list(self.config["repos"].keys()):
            if "files" in list(self.config["repos"][r].keys()):
                if executable in list(self.config["repos"][r]["files"].keys()):
                    return r

    def build_config(self, config):
        try:
            list(config.keys())
        except AttributeError as e:
            util.error("No keys defined in '" + config + "' key")

        newconfig = dict()
        for key in list(config.keys()):

            if key == "target":
                for t in self.targetnames:
                    if t in config["target"]:
                        self.config.update(self.build_config(config["target"][t]))

            elif key == "repos":
                if not "repos" in self.config:
                    self.config["repos"] = dict()

                for r in list(config["repos"].keys()):

                    if not r in list(self.config["repos"].keys()):
                        self.config["repos"][r] = dict()

                    for i in ["url", "builder"]:
                        if not i in list(config["repos"][r].keys()):
                            util.error(
                                "Missing required '"
                                + i
                                + "' key in '"
                                + r
                                + "' repository"
                            )

                    for i in list(config["repos"][r].keys()):

                        if i == "files":
                            fconfig = config["repos"][r]["files"]
                            for f in list(fconfig.keys()):
                                for k in list(fconfig[f].keys()):

                                    if not k in [
                                        "name",
                                        "icon",
                                        "help2man",
                                        "mimetypes",
                                    ]:
                                        util.error(
                                            "Invalid key '"
                                            + k
                                            + "' found in 'files/"
                                            + f
                                            + "'"
                                        )
                                    else:
                                        if k == "mimetypes":
                                            for l in fconfig[f][k]:
                                                for m in l:
                                                    if not m in [
                                                        "extension",
                                                        "type",
                                                        "icon",
                                                        "description",
                                                    ]:
                                                        util.error(
                                                            "Invalid key '"
                                                            + m
                                                            + "' found in 'files/"
                                                            + f
                                                            + "/"
                                                            + k
                                                            + "'"
                                                        )

                            try:
                                self.config["files"].update(fconfig)
                            except KeyError:
                                self.config["files"] = fconfig

                            self.config["repos"][r].update(
                                self.add_key(config["repos"][r], i, required=False)
                            )
                        else:
                            self.config["repos"][r].update(
                                self.add_key(config["repos"][r], i, required=False)
                            )

            else:
                newconfig.update(self.add_key(config, key))

        return newconfig

    def add_key(self, config, key, required=True):
        try:
            if config[key] is None:
                config[key] = ""
            return dict({key: config[key]})
        except KeyError as e:
            util.error(
                "This build requires the '" + e.message + "' key; see docs for details."
            )

    def add_keys(self, config, keys, required=True):
        newconfig = dict()
        for k in keys:
            newconfig.update(self.add_key(config, key, required))
        return newconfig

    @util.headline
    def checkout(self, refresh=False):
        v = importer.get_module(vcs, "git")
        importer.require(v)

        self.repos = {}
        for path in list(self.config["repos"].keys()):
            a = self.config["repos"][path]

            ref = None
            if "branch" in a:
                ref = a["branch"]
            if "tag" in a:
                ref = a["tag"]

            repo = v.Repo(a["url"], path, ref)

            self.repos[path] = repo

            if refresh:
                repo.update()

        if not "version" in self.config:
            self.config["version"] = self.repos[self.config["master"]].get_version()

        print("\nMaster version: ", self.config["version"])

    def filelist(self):
        fl = []
        for r in list(self.repos.values()):
            fl.extend(r.list_files())

        return fl

    @util.headline
    def archive(self):
        archivename = self.config["name"] + "-" + self.config["version"]

        if _platform["system"] == "windows":
            util.zip_archive(archivename, self.filelist())
        else:
            util.tar_archive(archivename, self.filelist())

    @util.headline
    def build(self, jobs="1"):
        packagelist = importer.get_modulelist(builders)

        self.builders = {}
        self.projects = {}
        for p in packagelist:
            self.builders[p] = importer.get_module(builders, p)
            importer.require(p)

        self.files = {}
        self.files["bin"] = []
        self.files["lib"] = []
        self.files["share"] = []

        for path in list(self.config["repos"].keys()):
            r = self.config["repos"][path]

            if "root" in r:
                root = os.path.join(path, r["root"])

                if not os.path.realpath(root).startswith(
                    os.getcwd() + os.sep + path + os.sep
                ):
                    util.error(
                        "root key specifies a directory outside of the project root: ",
                        root,
                    )

            else:
                root = path

            if not "exclude" in r:
                r["exclude"] = []

            if "builder" in r:
                util.subtitle(path + " (" + r["builder"] + ")")

                self.projects[path] = self.builders[r["builder"]].Builder(
                    root, self.repos[path].get_version()
                )

                outfiles = self.projects[path].build(jobs, r["exclude"])

                # verify all absolute paths (after prebuilt incident)

                for key in ["bin", "lib"]:
                    for f in outfiles[key]:
                        if os.path.isabs(f) == False:
                            util.error(
                                "Path returned from "
                                + path
                                + " ("
                                + r["builder"]
                                + ") is not absolute!"
                            )

                for key in self.files:
                    outfiles[key] = [x for x in outfiles[key] if x]
                    self.files[key].extend(outfiles[key])

            else:
                util.error("No builder declared for", path, "; skipping")

            util.cksum(self.files["bin"])

    @util.headline
    def package(self):

        self.packager = self.target.Packager(self.config, files=self.files)

        self.packager.clean()
        self.packager.make()

        self.buildtypes = []

        util.subtitle("Running file-specific commands")

        # generate icons

        if not "icon" in dir(self.packager):
            util.warning("No icon generator for this target")
        else:
            if "files" in self.config:
                for f in list(self.config["files"].keys()):
                    if "icon" in self.config["files"][f]:
                        self.packager.icon(self.config["files"][f]["icon"], f)

        # generate file associations

        if not "mimetypes" in dir(self.packager):
            util.warning("No filetype association generator for this target")
        else:
            if "files" in self.config:
                for f in list(self.config["files"].keys()):
                    if "mimetypes" in self.config["files"][f]:
                        self.packager.mimetypes(
                            self.config["files"][f]["mimetypes"],
                            f,
                            self.get_repo_from_executable_name(f),
                        )

        # get list of build types
        for path in list(self.config["repos"].keys()):
            r = self.config["repos"][path]

            if "builder" in r:
                if not r["builder"] in self.buildtypes:
                    self.buildtypes.append(r["builder"])
        #        print "Build systems used by this project:",', '.join(self.buildtypes)

        for p in self.projects:
            util.subtitle(p + " (" + self.config["repos"][p]["builder"] + ")")
            try:
                method = getattr(self.projects[p], self.targetname)
                method(self.packager.get_path())
            except AttributeError:
                print(
                    "No '" + self.targetname + "'-specific packaging for",
                    p,
                    "(" + self.config["repos"][p]["builder"] + ")",
                )

        self.packager.finish()

        util.title("Build complete")

    @util.headline
    def install(self):
        if "install" in dir(self.packager):
            self.packager.install()
        else:
            util.error("No installation procedure defined for this target")


def console():
    parser = argparse.ArgumentParser(description="write once, package everywhere")
    defaultrepo = "packthing.yml"
    parser.add_argument(
        "-f",
        nargs=1,
        metavar="FILE",
        default=[defaultrepo],
        help="packthing.yml file name (default: " + defaultrepo + ")",
    )
    parser.add_argument(
        "-C", nargs=1, metavar="DIR", help="change to DIR before running"
    )
    parser.add_argument(
        "-j",
        "--jobs",
        nargs=1,
        metavar="JOBS",
        default="1",
        help="number of jobs to pass to child builds",
    )
    parser.add_argument(
        "-r", "--refresh", action="store_true", help="refresh the repository checkout"
    )

    stages = parser.add_mutually_exclusive_group()
    stages.add_argument(
        "--configure", action="store_true", help="stop packthing at configure stage"
    )
    stages.add_argument(
        "--checkout", action="store_true", help="stop packthing at checkout stage"
    )
    stages.add_argument(
        "--build", action="store_true", help="stop packthing at build stage"
    )
    stages.add_argument(
        "--install", action="store_true", help="Attempt to run newly-built installer"
    )

    overrides = parser.add_argument_group("overrides", "manually override settings")
    overrides.add_argument(
        "--override-system",
        metavar="SYSTEM",
        help="Set platform system (linux, windows, ...)",
    )
    overrides.add_argument(
        "--override-arch",
        metavar="ARCH",
        help="Set platform machine (i686, amd64, ...)",
    )
    overrides.add_argument(
        "--override-version",
        metavar="VERSION",
        help="Set application version (e.g. 1.2.3)",
    )

    parser.add_argument(
        "target",
        nargs="?",
        metavar="TARGET",
        help="Target package to build (" + ", ".join(packagelist) + ")",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if args.override_system:
        _platform["system"] = args.override_system
    if args.override_arch:
        _platform["machine"] = args.override_arch
    if args.override_version:
        _platform["version"] = args.override_version

    if args.C:
        os.chdir(args.c[0])

    if not args.target:
        if not args.checkout and not args.configure and not args.build:
            util.error(
                "Must select a packaging target.",
                "\nAvailable packagers:",
                ", ".join(packagelist),
            )
        else:
            args.target = "_base"
    else:
        if not args.target in packagelist:
            util.error(
                "The '" + args.target + "' packager does not exist.",
                "\nAvailable packagers:",
                ", ".join(packagelist),
            )

    if args.target == "clean":
        try:
            shutil.rmtree("build")
        except OSError as e:
            if e.errno == 2:
                pass
            elif e.errno == 13:
                util.error(
                    "You don't have permissions to delete '"
                    + e.filename
                    + "'; try running as root?"
                )
            else:
                util.error(e.strerror + ":", "'" + e.filename + "'")

        print("Staging area deleted.")
        sys.exit(0)

    pm = Packthing(args.f[0], args.target)

    if args.configure:
        sys.exit(0)

    util.mkdir("build")
    with util.pushd("build"):

        pm.checkout(args.refresh)

        if args.checkout:
            sys.exit(0)

        if args.target == "src":
            pm.archive()
            sys.exit(0)

        pm.build(args.jobs[0])

        if args.build:
            sys.exit(0)

        pm.package()

        if args.install:
            pm.install()
