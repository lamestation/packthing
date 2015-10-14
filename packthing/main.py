# -*- coding: utf-8 -*-

import os, sys
import importer
import util, shutil
import yaml
import pkgutil, importlib
import packagers, vcs, builders

import argparse
import pprint


# intercept CTRL+C
import signal
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
            util.error("'"+self.repofile+"' not found; please specify a valid packthing file")

        # build tree of included targets
        self.target = importer.get_module(packagers,self.targetname)
        self.targetnames = []
        for t in importer.list_module_hierarchy(self.target):
            self.targetnames.append(t.__module__.split('.')[-1])
        self.targetnames = [x for x in self.targetnames if not x.startswith('_')]

        self.build_config(config)

        # package
        if not 'package' in self.config:
            self.config['package'] = config['name'].lower()

        # master
        if not 'master' in self.config:
            for path in self.config['repo'].keys():
                r = self.config['repo'][path]

                if path == self.config['name'] or path == self.config['package']:
                    self.config['master'] = path
                    print "Using",self.config['master'],"as master project."
                    break

            if not 'master' in self.config:
                util.error("No master repository defined in",repofile)


        for k in _platform.keys():
            self.add_value(_platform,k)

        importer.require(self.target)

        for k in importer.required_keys(self.target):
            self.add_value(self.config, k)
            print "%20s: %s" % (k,self.config[k])


#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(self.config)


    def build_config(self, config):
        try:
            config.keys()
        except AttributeError as e:
            return
            
        for key in config.keys():
            if key == 'target':
                for t in self.targetnames:
                    if t in config['target']:
                        self.build_config(config['target'][t])
            else:
                self.add_value(config, key)


    def add_value(self, config, key):
        if key in config:
            self.config[key] = config[key]
            if self.config[key] is None:
                self.config[key] = ""
        else:
            util.error("This build requires the '"+key+"' key; see docs for details.")


    @util.headline
    def checkout(self, refresh=False):
        v = importer.get_module(vcs, 'git')
        importer.require(v)

        self.repos = {}
        for path in self.config['repo'].keys():
            a = self.config['repo'][path]

            ref = None
            if 'branch' in a:
                ref = a['branch']
            if 'tag' in a:
                ref = a['tag']

            repo = v.Repo(a['url'],path, ref)

            self.repos[path] = repo

            if refresh:
                repo.update()

    def filelist(self):
        fl = []
        for r in self.repos.values():
            fl.extend(r.list_files())

        return fl

    @util.headline
    def archive(self):
        version = self.repos[self.config['master']].get_version()
        archivename = self.config['name']+"-"+version

        if _platform['system'] == "windows":
            util.zip_archive(archivename,self.filelist())
        else:
            util.tar_archive(archivename,self.filelist())


    @util.headline
    def build(self,jobs='1'):
        packagelist = importer.get_modulelist(builders)

        self.builders = {}
        self.projects = {}
        for p in packagelist:
            self.builders[p] = importer.get_module(builders,p)
            importer.require(p)

        self.files = {}
        self.files['bin'] = []
        self.files['lib'] = []
        self.files['share'] = []

        for path in self.config['repo'].keys():
            r = self.config['repo'][path]

            if 'root' in r:
                root = os.path.join(path,r['root'])
            else:
                root = path

            if not 'exclude' in r:
                r['exclude'] = []

            if 'type' in r:
                util.subtitle(path+" ("+r['type']+")")

                self.projects[path] = self.builders[r['type']].Builder(root,
                        self.repos[path].get_version())

                outfiles = self.projects[path].build(jobs, r['exclude'])
                for f in self.files:
                    outfiles[f] = [x for x in outfiles[f] if x]
                    self.files[f].extend(outfiles[f])

            else:
                util.error("No type declared for",path,"; skipping")

                 
    @util.headline
    def package(self):

        self.packager = self.target.Packager(
                self.config, 
                self.repos[self.config['master']].get_version(),
                files=self.files,
                )

        self.packager.clean()
        self.packager.make()

        self.buildtypes = []

        # icon generators
        if not 'icon' in dir(self.packager):
            util.warning("No icon generator configured for this target")
        else:
            for path in self.config['repo'].keys():
                r = self.config['repo'][path]

                if 'icon' in r:
                    self.packager.icon(
                            os.path.join(path,r['icon']),
                            path)
                else:
                    util.warning("No icon for",path)


        # get list of build types
        for path in self.config['repo'].keys():
            r = self.config['repo'][path]

            if 'type' in r:
                if not r['type'] in self.buildtypes:
                    self.buildtypes.append(r['type'])
#        print "Build systems used by this project:",', '.join(self.buildtypes)


        for p in self.projects:
            try:
                method = getattr(self.projects[p], self.targetname)
                method(self.packager.get_path())
            except AttributeError:
                util.warning("No '"+self.targetname+"'-specific packaging for",p,"("+self.config['repo'][p]['type']+")")

        self.packager.finish()


    @util.headline
    def install(self):
        if 'install' in dir(self.packager):
            self.packager.install()
        else:
            util.error("No installation procedure defined for this target")


def console():
    parser = argparse.ArgumentParser(description='write once, package everywhere')
    defaultrepo = 'packthing.yml'
    parser.add_argument('-f',               nargs=1, metavar='FILE',default=[defaultrepo],  help="packthing.yml file name (default: "+defaultrepo+")")
    parser.add_argument('-C',               nargs=1, metavar='DIR',                         help="change to DIR before running")
    parser.add_argument('-j','--jobs',      nargs=1, metavar='JOBS',default='1',            help="number of jobs to pass to child builds")
    parser.add_argument('-r','--refresh',   action='store_true',                            help="refresh the repository checkout")


    stages = parser.add_mutually_exclusive_group()
    stages.add_argument('--configure',      action='store_true', help="stop packthing at configure stage")
    stages.add_argument('--checkout',       action='store_true', help="stop packthing at checkout stage")
    stages.add_argument('--build',          action='store_true', help="stop packthing at build stage")
    stages.add_argument('--install',        action='store_true', help="install newly built package to OS")

    overrides = parser.add_argument_group('overrides', 'manually override auto-generated settings (use at own risk!)')
    overrides.add_argument('--system',      nargs=1, metavar='SYSTEM',  help="Override platform system (linux, windows, ...)")
    overrides.add_argument('--arch',        nargs=1, metavar='ARCH',    help="Override platform machine (i686, amd64, ...)")

    parser.add_argument('target',           nargs='?', metavar='TARGET',help="Target package to build ("+', '.join(packagelist)+")")

    args = parser.parse_args()

    if args.system: _platform['system']     = args.system[0]
    if args.arch:   _platform['machine']    = args.arch[0]

    if args.C:
        os.chdir(args.c[0])

    if not args.target:
        if not args.checkout and not args.configure and not args.build:
            util.error("Must select a packaging target.",
                        "\nAvailable packagers:",', '.join(packagelist))
        else:
            args.target = '_base'
    else:
        if not args.target in packagelist:
            util.error("The '"+args.target+"' packager does not exist.",
                    "\nAvailable packagers:",', '.join(packagelist))

    if args.target == "clean":
        try:
            shutil.rmtree('build')
        except OSError as e:
            if e.errno == 2:
                pass
            elif e.errno == 13:
                util.error("You don't have permissions to delete '"+e.filename+"'; try running as root?")
            else:
                util.error(e.strerror+":","'"+e.filename+"'")

        print("Staging area deleted.")
        sys.exit(0)


    pm = Packthing(args.f[0], args.target)

    if args.configure: sys.exit(0)

    util.mkdir('build')
    with util.pushd('build'):

        pm.checkout(args.refresh)

        if args.checkout: sys.exit(0)

        if args.target == "src":
            pm.archive()
            sys.exit(0)

        pm.build(args.jobs[0])

        if args.build: sys.exit(0)

        pm.package()

        if args.install:
            pm.install()

