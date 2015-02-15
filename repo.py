import os

class Repo:
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.version = self.set_version()

    def get_version(self):
        return self.version

    def update(self):
        if os.path.exists(self.path):
            if self.path == '.':
                raise OSError("Repository must be child of current directory")
            else:
                self.pull()
        else:
            self.clone()

        self.update_externals()

    def list_files(self):
        out, err = self.filelist()
        out = out.split('\n')
        out.pop() # remove empty last element
        output = []
        for o in out:
            o = os.path.join(self.path,o)
            output.append(o)
        return output

