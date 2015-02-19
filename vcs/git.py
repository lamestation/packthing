import util
import base

REQUIRE = ['git']

class Repo(base.Repo):

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

    def clone(self):
        util.command(['git','clone',self.url,self.path])
    
    def pull(self):
        util.command_in_dir(['git','remote','set-url','origin',self.url],self.path)
        self.checkout()
        util.command_in_dir(['git','pull'],self.path)

    def update_externals(self):
        util.command_in_dir(['git','submodule','init'], self.path)
        util.command_in_dir(['git','submodule','update','--recursive'], self.path)

    def checkout(self, ref='master'):
        util.command_in_dir(['git','checkout',ref], self.path)

    def filelist(self):
        out, err = util.command_in_dir(['git','ls-files'], self.path)
        return out, err
