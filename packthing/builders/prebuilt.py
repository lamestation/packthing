import os
import subprocess

from .. import util
from . import base

_platform = util.get_platform()


class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder, self).__init__(path, version)

    def get_all_files(self, directory):
        matches = []
        for root, dirnames, filenames in os.walk(directory, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_PATTERNS]
            for filename in filenames:
                matches.append(os.path.abspath(os.path.join(root, filename)))

        return matches

    def build(self, jobs="1", exclude=None):
        self.IGNORE_PATTERNS = ("CVS", ".git", ".svn")

        directory = os.path.join(self.path, _platform["system"])
        for k in list(self.files.keys()):

            kdir = os.path.join(directory, k)

            if os.path.isdir(kdir):
                self.files[k] = self.get_all_files(kdir)

                if _platform["system"] == "windows":
                    self.files["bin"] = [
                        os.path.splitext(f)[0] for f in self.files["bin"]
                    ]
                    self.files["lib"] = [
                        os.path.splitext(f)[0] for f in self.files["lib"]
                    ]

        return self.files
