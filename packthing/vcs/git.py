import subprocess

from .. import util
from . import base

REQUIRE = ["git"]


class Repo(base.Repo):

    default_ref = "master"

    def set_version(self):
        try:
            out, err = util.command_in_dir(
                ["git", "describe", "--tags", "--long"],
                self.path,
                verbose=False,
                strict=False,
            )
        except OSError:
            self.update()
            out, err = util.command_in_dir(
                ["git", "describe", "--tags", "--long"],
                self.path,
                verbose=False,
                strict=False,
            )

        if not out == "":
            self.version = out.split("-")[0]
        else:
            self.version = "0.0.0"

        return self.version

    def clone(self):
        subprocess.check_call(["git", "clone", self.url, self.path])

    def pull(self):
        with util.pushd(self.path):
            subprocess.check_call(["git", "remote", "set-url", "origin", self.url])
        self.checkout()
        with util.pushd(self.path):
            subprocess.check_call(["git", "pull"])

    def update_externals(self):
        with util.pushd(self.path):
            subprocess.check_call(
                ["git", "submodule", "update", "--init", "--recursive"]
            )

    def checkout(self, ref="master"):
        with util.pushd(self.path):
            subprocess.check_call(["git", "checkout", ref])

    def filelist(self):
        out, err = util.command_in_dir(["git", "ls-files"], self.path)
        return out, err
