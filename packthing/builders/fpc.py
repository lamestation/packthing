# -*- coding: utf-8 -*-

import os
import re
from .. import util
import subprocess

from . import base

REQUIRE = [ 'fpc' ]

_platform = util.get_platform()

class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder,self).__init__(path, version)


    def get_program(self):
        for f in os.listdir('.'):
            matches = re.findall('^[ \t]*program[ \t]*([a-z_][a-z0-9_]*)[ \t]*;', 
                                 open(f).read(),
                                 flags=re.IGNORECASE)
            if len(matches):
                return f, matches[0]

    def get_target_os_flag(self):
        if _platform["system"] in ["linux", "darwin"]:
            return "-T"+_platform["system"]
        elif _platform["system"] == "windows" and _platform["machine"] == "amd64":
            return "-Twin64"
        else:
            return ""

    def build(self,jobs='1',exclude=None):
        with util.pushd(self.path):
            pfile, pname = self.get_program()
            pname = pname.lower()
            print "Found program", pname, "in", pfile

            args = [
                    'fpc',
                    '-O3',
                    self.get_target_os_flag(),
                    "-o"+pname,
                    pfile
                   ]
            print "- "+' '.join(args)

            try:
                subprocess.check_call(args)
            except subprocess.CalledProcessError:
                util.error("Failed to build:",pfile)

            self.files['bin'] = [os.path.abspath(pname)]

        return self.files