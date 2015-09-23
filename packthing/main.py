# -*- coding: utf-8 -*-

import os, sys
import platform
import importer
import util
import yaml
import pkgutil, importlib
import targets, vcs, builders

import argparse

_platforms = importer.get_modulelist(targets)

# detect platform
_platform = platform.system().lower()
try:
    target = importer.get_module(targets, _platform)
except ImportError:
    util.error("Packthing has no install targets for the '"+_platform+"' operating system.",
               "\nSupported systems:",', '.join(_platforms))

packagelist = importer.get_modulelist(target)

class Packthing:
    def __init__(self, repofile):
        try:
            self.config = yaml.load(open(repofile))
        except IOError:
            util.error("'"+repofile+"' not found; please specify a valid packthing file")
            sys.exit(1)

        if not 'package' in self.config:
            self.config['package'] = self.config['name'].lower()

        master = None
        for r in self.config['repo']:
            if u'master' in r:
                if master == None:
                    master = r['path']
                else:
                    raise KeyError("Master repository defined twice!")

        if master == None:
            raise KeyError("No master repository defined!")

        self.config[u'master'] = master


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

    @util.headline
    def filelist(self):
        fl = []
        for r in self.repos.values():
            fl.extend(r.list_files())

        return fl

    @util.headline
    def archive(self, archivename):
        util.archive(archivename,self.filelist())


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
    def package(self, targetname):
        self.target = importer.get_module(target,targetname)

        importer.require(self.target)

        if 'target' in self.config:
            if targetname in self.config['target']:
                self.config.update(self.config['target'][targetname])

        self.packager = self.target.Packager(self.config, 
                self.repos[self.config['master']].get_version(),
                files=self.files,
                )

        self.packager.clean()
        self.packager.make()

        self.buildtypes = []
        for r in self.config['repo']:
            if 'type' in r:
                if not r['type'] in self.buildtypes:
                    self.buildtypes.append(r['type'])

            if 'icon' in r:
                try:
                    method = getattr(self.packager, 'icon')
                    method(os.path.join(r['path'],r['icon']),r['path'])
                except AttributeError:
                    pass

        for p in self.projects:
            try:
                method = getattr(self.projects[p], targetname)
                method(self.packager.get_path())
            except AttributeError:
                pass

        self.packager.finish()
    

def console():
    parser = argparse.ArgumentParser(description='write once, package everywhere')
    defaultrepo = 'packthing.yml'
    parser.add_argument('-f',               nargs=1, metavar='REPO',default=[defaultrepo],  help="packthing.yml file name (default: "+defaultrepo+")")
    parser.add_argument('-C',               nargs=1, metavar='DIR',                         help="Change to DIR before running")
    parser.add_argument('-a','--archive',   nargs=1, metavar='NAME',                        help="Create tar archive from super-repository")
    parser.add_argument('-j','--jobs',      nargs=1, metavar='JOBS',default='1',            help="Number of jobs to pass to child builds")
    parser.add_argument('-r','--refresh',   action='store_true',                            help="Refresh the repository checkout")
    parser.add_argument('target',           nargs='?', metavar='TARGET',                    help="Target platform to build ("+', '.join(packagelist)+")")

    args = parser.parse_args()

    if args.C:
        os.chdir(args.c[0])

    if not args.target:
        util.error("Must pass a target to packthing.",
                    "\nAvailable",_platform.capitalize(),"targets:",', '.join(packagelist))
    else:
        if not args.target in packagelist:
            util.error("'"+args.target+"' does not exist on this platform.",
                    "\nAvailable",_platform.capitalize(),"targets:",', '.join(packagelist))


    pm = Packthing(args.f[0])

    util.mkdir('build')
    with util.pushd('build'):
        pm.checkout(args.refresh)

        if args.archive:
            pm.archive(args.archive[0])
            sys.exit(0)

        pm.build(args.jobs[0])
        pm.package(args.target)
