from . import base
from .. import util
import subprocess

REQUIRE = ['git']

class Repo(base.Repo):

    default_ref = "master"

    @util.log
    def set_version(self):
        try:
            out, err = util.command_in_dir(['git','describe','--tags','--long'],self.path, strict=False)
        except OSError:
            self.update()
            out, err = util.command_in_dir(['git','describe','--tags','--long'],self.path, strict=False)

        if not out == '':
            self.version = out.split('-')[0]
        else:
            self.version = '0.0.0'

        return self.version

    @util.log
    def clone(self):
        subprocess.check_call(['git','clone',self.url,self.path])
    
    @util.log
    def pull(self):
        with util.pushd(self.path):
            subprocess.check_call(['git','remote','set-url','origin',self.url])
        self.checkout()
        with util.pushd(self.path):
            subprocess.check_call(['git','pull'])

    @util.log
    def update_externals(self):
        with util.pushd(self.path):
            subprocess.check_call(['git','submodule','update','--init','--recursive'])

    @util.log
    def checkout(self, ref='master'):
        with util.pushd(self.path):
            subprocess.check_call(['git','checkout',ref])

    @util.log
    def filelist(self):
        out, err = util.command_in_dir(['git','ls-files'], self.path)
        return out, err
