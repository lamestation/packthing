# -*- coding: utf-8 -*-

import os, sys
import platform
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



_platforms = importer.get_modulelist(packagers)

# detect platform
_platform = platform.system().lower()
try:
    targets = importer.get_module(packagers, _platform)
except ImportError:
    util.error("Packthing has no package targets for the '"+_platform+"' operating system.",
               "\nSupported systems:",', '.join(_platforms))

packagelist = importer.get_modulelist(targets)
packagelist.append("src")
packagelist.append("clean")

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

        self.build_config(config)

        # package
        if not 'package' in self.config:
            self.config['package'] = config['name'].lower()

        # master
        if not 'master' in self.config:
            for r in self.config['repo']:
                if r['path'] == self.config['name'] or r['path'] == self.config['package']:
                    self.config['master'] = r['path']
                    print "Using",self.config['master'],"as master project."
                    break

            if not 'master' in self.config:
                util.error("No master repository defined in",repofile)

        self.target = importer.get_module(targets,self.targetname)
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
                if self.targetname in config['target']:
                    self.build_config(config['target'][self.targetname])
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
        for a in self.config['repo']:

            ref = None
            if 'branch' in a:
                ref = a['branch']
            if 'tag' in a:
                ref = a['tag']

            repo = v.Repo(a['url'],a['path'], ref)

            self.repos[a['path']] = repo

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

        if _platform == "windows":
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

        for r in self.config['repo']:
            if 'root' in r:
                path = os.path.join(r['path'],r['root'])
            else:
                path = r['path']

            if not 'exclude' in r:
                r['exclude'] = []

            if 'type' in r:
                util.subtitle(r['path']+" ("+r['type']+")")

                self.projects[r['path']] = self.builders[r['type']].Builder(path,
                        self.repos[r['path']].get_version())

                outfiles = self.projects[r['path']].build(jobs, r['exclude'])
                for f in self.files:
                    outfiles[f] = [x for x in outfiles[f] if x]
                    self.files[f].extend(outfiles[f])

            else:
                util.error("No type declared for",r['path'],"; skipping")

                 
    @util.headline
    def package(self):


        self.packager = self.target.Packager(self.config, 
                self.repos[self.config['master']].get_version(),
                files=self.files,
                )

        self.packager.clean()
        self.packager.make()

        self.buildtypes = []
        for r in self.config['repo']:

            # get list of build types
            if 'type' in r:
                if not r['type'] in self.buildtypes:
                    self.buildtypes.append(r['type'])

            # check if icon and build, don't care if it fails
            if 'icon' in r:
                try:
                    method = getattr(self.packager, 'icon')
                    method(os.path.join(r['path'],r['icon']),r['path'])
                except AttributeError:
                    util.warning("Icon not supported for current platform")
            else:
                util.warning("No icon for ",r['path'])

        for p in self.projects:
            try:
                method = getattr(self.projects[p], self.targetname)
                method(self.packager.get_path())
            except AttributeError:
                util.warning("No build specific targets found for",self.targetname,"in",p)
                pass

        self.packager.finish()
    

def console():
    parser = argparse.ArgumentParser(description='write once, package everywhere')
    defaultrepo = 'packthing.yml'
    parser.add_argument('-f',               nargs=1, metavar='FILE',default=[defaultrepo],  help="packthing.yml file name (default: "+defaultrepo+")")
    parser.add_argument('-C',               nargs=1, metavar='DIR',                         help="Change to DIR before running")
    parser.add_argument('-j','--jobs',      nargs=1, metavar='JOBS',default='1',            help="Number of jobs to pass to child builds")
    parser.add_argument('-r','--refresh',   action='store_true',                            help="Refresh the repository checkout")
    parser.add_argument('--no-build',       action='store_true',                            help="Don't build project; just show configuration.")

    overrides = parser.add_argument_group('overrides', 'manually override settings in the packthing config')
    overrides.add_argument('--platform',    nargs=1, metavar='PLATFORM',                    help="Use this platform configuration")

    parser.add_argument('target',           nargs='?', metavar='TARGET',                    help="Target platform to build ("+', '.join(packagelist)+")")

    args = parser.parse_args()

    if args.C:
        os.chdir(args.c[0])

    if not args.target:
        util.error("Must pass a target to packthing.",
                    "\nAvailable",_platform.capitalize(),"packagers:",', '.join(packagelist))
    else:
        if not args.target in packagelist:
            util.error("'"+args.target+"' does not exist on this platform.",
                    "\nAvailable",_platform.capitalize(),"packagers:",', '.join(packagelist))


    pm = Packthing(args.f[0], args.target)

    if args.no_build:
        sys.exit(0)

    util.mkdir('build')
    with util.pushd('build'):
        if args.target == "clean":
            try:
                shutil.rmtree('staging')
            except OSError:
                pass
            print("Staging area deleted.")
            sys.exit(0)


        pm.checkout(args.refresh)

        if args.target == "src":
            pm.archive()
            sys.exit(0)

        pm.build(args.jobs[0])
        pm.package()


