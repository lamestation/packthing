# -*- coding: utf-8 -*-

import os
import glob
from .. import util
import shutil
import logging
import subprocess

from . import base

REQUIRE = [ 'qmake',
            ]


class ProjectNode(object):
    def __init__(self, path, values={}):
        self.values = values
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder,self).__init__(path, version)

        self.root = self.build_project_tree(self.path)

    def build_project_tree(self, path):
        with util.pushd(path):

            p = glob.glob('*.pro')

            if len(p) < 1:
                raise KeyError("Project file not found in "+path)

            if len(p) > 1:
                raise KeyError("There are more than two project files in "+path)
            p = p[0]

            tmppro = '.'+os.path.basename(p)+'.tmp'
            shutil.copyfile(os.path.basename(p), tmppro)

            valuelist = ['TEMPLATE','TARGET','DESTDIR','SUBDIRS','CONFIG']
            self.output_values(tmppro, valuelist)
            self.insert_value(tmppro, r"""CONFIG -= debug_and_release app_bundle""")
            self.insert_value(tmppro, r"""isEmpty(VERSION_ARG):VERSION_ARG = 0.0.0""")
            self.insert_value(tmppro, r"""VERSION_ARG = '\\"$${VERSION_ARG}\\"'""")
            self.insert_value(tmppro, r"""DEFINES += VERSION=\"$${VERSION_ARG}\"""")

            output = util.command(['qmake','VERSION_ARG='+self.VERSION,tmppro])[1]

            values = self.get_values(output, valuelist)
            values['FILE'] = p
            values['PATH'] = os.getcwd()

            for v in values:
                if v == 'DESTDIR' and len(values[v]) > 0:
                    values[v] = [os.path.realpath(values[v][0])]

            node = ProjectNode(path,values)

            logging.debug(node.values)

            if values['TEMPLATE'] == ['subdirs']:
                for v in values['SUBDIRS']:
                    node.add_child(self.build_project_tree(v))

        return node 

    def output_values(self, filename, values):
        for v in values:
            self.output_value(filename, v)

    def output_value(self, filename, value):
        with open(filename, "a") as f:
            f.write('\nmessage("'+value+'=$$'+value+'")')

    def insert_value(self, filename, value):
        with open(filename, "a") as f:
            f.write('\n'+value)

    def get_values(self, text, values):
        outputlist = {}
        for v in values:
            outputlist[v] = self.get_value(text, v)
        return outputlist

    def get_value(self, text, value):
        for line in text.split('\n'):
            if 'Project MESSAGE' in line:
                if value in line:
                    return line.split('=')[1].strip().split()


    def collect_targets(self,node,template,exclude=None):
        files = []
        if exclude is None: exclude = []

        t = node.values['TEMPLATE'][0]

        if t == template:
            if not node.values['TARGET'] == []:
                filename = node.values['TARGET'][0]

                if not filename in exclude:
                    if not node.values['DESTDIR'] == []:
                        filename = os.path.join(node.values['DESTDIR'][0],filename)

                    if not 'staticlib' in node.values['CONFIG']:
                        filename = os.path.join(node.values['PATH'],filename)
                        filename = os.path.realpath(filename)

                        files.append(filename)

        elif t == 'subdirs':
            for c in node.children:
                files.extend(self.collect_targets(c,template,exclude))

        return files

    def call_make(self,args):
        args.insert(0,'make')
        for m in ['make','mingw32-make']:
            args[0] = m
            failed = 0

            try:
                subprocess.check_call(args)
            except OSError:
                failed = 1

            if not failed:
                return
    
    def build(self,jobs='1',exclude=None):
        with util.pushd(self.path):
            self.call_make(['-j'+jobs])

        self.files['bin'] = self.collect_targets(self.root,'app',exclude)
        self.files['lib'] = self.collect_targets(self.root,'lib',exclude)

        return self.files

    def win(self, path):
        for f in self.files['bin']:
            try:
                subprocess.check_call([
                    'windeployqt',
                    '--dir',path,
                    '--no-translations',
                    '--release',
                    f+'.exe',
                    ])
            except subprocess.CalledProcessError:
                pass

    def mac(self, path):
        print self.files['bin']
        for f in self.files['bin']:
            fn = os.path.basename(f)
            subprocess.check_call([
                'macdeployqt',
                path,
                '-executable='+os.path.join(path,"Contents","MacOS",fn)
                ])

