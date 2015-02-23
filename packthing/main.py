#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import importer
import logging
import util
import json
import pkgutil, importlib
import target, vcs, builder

import argparse

class Packthing:
    def __init__(self, repofile):
        try:
            self.config = json.load(open(repofile))
        except IOError:
            util.error("'"+repofile+"' not found; please specify a valid packman file")
            sys.exit(1)

        if not 'package' in self.config['info']:
            self.config['info']['package'] = self.config['info']['name'].lower()

        master = None
        for r in self.config['repo']:
            if u'master' in r:
                if master == None:
                    master = r['path']
                else:
                    raise KeyError("Master repository defined twice!")

        if master == None:
            raise KeyError("No master repository defined!")

        self.config['info'][u'master'] = master


    @util.headline
    def checkout(self, refresh):
        v = importer.get_module(vcs, 'git')
        importer.require(v)

        self.repos = {}
        for a in self.config['repo']:
            repo = v.Repo(a['url'],a['path'])
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
        packagelist = importer.get_modulelist(builder)
        packagelist.remove('base')

        self.builders = {}
        self.projects = {}
        for p in packagelist:
            self.builders[p] = importer.get_module(builder,p)
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
                print r['type']
                self.projects[r['path']] = self.builders[r['type']].Builder(path,
                        self.repos[r['path']].get_version())

                outfiles = self.projects[r['path']].build(jobs, r['exclude'])
                for f in self.files:
                    outfiles[f] = [x for x in outfiles[f] if x]
                    self.files[f].extend(outfiles[f])

            else:
                util.warning("No type declared for",r['path'],"; skipping")

                 
    @util.headline
    def package(self, targetname):
        try:
            self.target = importer.get_module(target,targetname)
        except ImportError:
            self.target = importer.get_module(target,'base')

        importer.require(self.target)

        if 'target' in self.config:
            if targetname in self.config['target']:
                self.config['info'].update(self.config['target'][targetname])

        self.packager = self.target.Packager(self.config['info'], 
                self.repos[self.config['info']['master']].get_version(),
                files=self.files,
                )

        logging.debug('target = '+targetname)
        self.packager.clean()
        self.packager.make()

        for r in self.config['repo']:
            if 'icon' in r:
                print r['icon']
                self.packager.icon(os.path.join(r['path'],
                            r['icon']),r['path'])

        for p in self.projects:
            try:
                method = getattr(self.projects[p], targetname)
                method(self.packager.get_path())
            except AttributeError:
                pass

        self.packager.finish()
    

def console():

    packagelist = []
#    print target, vcs, builder
#    print importer.get_modulelist(target)
#    print importer.get_modulelist(vcs)
#    print importer.get_modulelist(target)

#    if 'base' in packagelist:
#        packagelist.remove('base')

    parser = argparse.ArgumentParser(description=os.path.basename(__file__)+' - make working with your project more complicated')
    defaultrepo = 'packthing.json'
    parser.add_argument('-r','--repo',      nargs=1, metavar='REPO',    default=[defaultrepo], help="Project repository config file (default: "+defaultrepo+")")
    parser.add_argument('-c',               nargs=1, metavar='DIR',     help="Change to DIR before running")
    parser.add_argument('-l','--log',       nargs=1, metavar='LEVEL',   help="Log level of debug output (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument('-a','--archive',   nargs=1, metavar='NAME',    help="Create tar archive from super-repository")
    parser.add_argument('--list-src',       action='store_true',        help="List all files in super-repository")
    parser.add_argument('--list-build',     action='store_true',        help="List all files to be included in package")
    parser.add_argument('-j','--jobs',      nargs=1, metavar='JOBS',default='1',    help="Number of jobs to pass to child builds")
    parser.add_argument('--refresh',        action='store_true',        help="Force update of all checkouts")
    parser.add_argument('target',           nargs='?', metavar='TARGET',help="Target platform to build ("+', '.join(packagelist)+")")

    args = parser.parse_args()

    if args.log:
        logging.basicConfig(level=args.log[0])

    if args.c:
        os.chdir(args.c[0])

    pm = Packthing(args.repo[0])

    pm.checkout(args.refresh)
    pm.build(args.jobs[0])

    if not args.target == None:
        pm.package(args.target)

    if args.list_src:
        for l in pm.filelist():
            print l

    if args.archive:
        pm.archive(args.archive[0])
