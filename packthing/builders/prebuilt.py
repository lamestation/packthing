import os
import shutil
from .. import util
import glob
import subprocess
import platform

from . import base

class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder,self).__init__(path, version)

    def get_all_files(self, directory):
        matches = []
        for root, dirnames, filenames in os.walk(directory, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_PATTERNS]
            for filename in filenames:
                matches.append(os.path.join(root, filename))
        return matches


    def build(self,jobs='1',exclude=None):
        self.IGNORE_PATTERNS = ('CVS','.git','.svn')


        dir = os.path.join(self.path, platform.system())
        for k in self.files.keys():
            
            kdir = os.path.join(dir, k)
            
            if os.path.isdir(kdir):
                self.files[k] = self.get_all_files(kdir)

                if platform.system() == "Windows":
                    self.files['bin'] = [os.path.splitext(f)[0] for f in self.files['bin']]
                    self.files['lib'] = [os.path.splitext(f)[0] for f in self.files['lib']]
        
        return self.files

