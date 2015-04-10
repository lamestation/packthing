import os, sys
from .. import util

class Repo:

    @util.log
    def __init__(self, url, path, ref=None):
        self.url = url
        self.path = path
        self.ref = 'master'

        if not ref == None:
            self.ref = ref

        self.version = self.set_version()

        sys.stdout.write("  ( {:>10} ) {:<30} {}\n".format(self.version,self.path,self.url))

    @util.log
    def get_version(self):
        return self.version

    @util.log
    def update(self):
        if os.path.exists(self.path):
            if self.path == '.':
                raise OSError("Repository must be child of current directory")
            else:
                self.pull()
        else:
            self.clone()

        self.checkout(self.ref)
        self.update_externals()

    @util.log
    def list_files(self):
        out, err = self.filelist()
        out = out.split('\n')
        out.pop() # remove empty last element
        output = []
        for o in out:
            o = os.path.join(self.path,o)
            output.append(o)
        return output

