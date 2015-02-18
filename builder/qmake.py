import os, sys, re, fnmatch
import glob
import util
import shutil
import pprint

from . import base

class ProjectNode(object):
    def __init__(self, path, values={}):
        self.values = values
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder,self).__init__(path, version)

        root = self.build_project(self.path)

    def build_project(self, path):
        with util.pushd(path):

            p = glob.glob('*.pro')

            if len(p) < 1:
                return

            if len(p) > 1:
                raise KeyError("There are more than two project files in "+path)
            p = p[0]

            tmppro = '.'+os.path.basename(p)+'.tmp'
            shutil.copyfile(os.path.basename(p), tmppro)

            valuelist = ['TEMPLATE','TARGET','DESTDIR','SUBDIRS','CONFIG']
            self.output_values(tmppro, valuelist)
            self.insert_value(tmppro, 'CONFIG -= debug_and_release app_bundle')

            output = util.command(['qmake',tmppro])[1]
            os.remove(tmppro)

            values = self.get_values(output, valuelist)
            values['FILE'] = p

            for v in values:
                if v == 'DESTDIR' and len(values[v]) > 0:
                    values[v] = [os.path.relpath(values[v][0])]

            node = ProjectNode(path,values)

            print node.values

            if values['TEMPLATE'] == ['subdirs']:
                for v in values['SUBDIRS']:
                    node.add_child(self.build_project(v))

        return node 

    def get_all_files(self, directory, expression):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, expression):
                matches.append(os.path.join(root, filename))
        return matches

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

    def build(self):
        return self.files
