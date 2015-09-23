# -*- coding: utf-8 -*-

import os
import subprocess

import packthing.util as util
from . import build

class Packager(build.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'run'

    def setup_script(self):
        d = {
            'APPLICATION' : self.info['package'],
            'VERSION'     : self.VERSION,
            'DEFAULT_DIR' : '/opt/',
        }
        return util.get_template('run/setup.sh').safe_substitute(d)

    def self_extracting(self):
        d = {
            'PACKAGENAME' : self.packagename(),
            'SETUP_SCRIPT': 'setup.sh',
        }
        return util.get_template('run/self_extracting.sh').safe_substitute(d)

    def make(self):
        self.install()
        extract_script = os.path.join(self.DIR_STAGING,self.packagename()+'.'+self.EXT)
        util.create(self.setup_script(), os.path.join(self.DIR_OUT,'setup.sh'), executable=True)
        util.create(self.self_extracting(), extract_script)

        subprocess.check_call(  "cd "+self.DIR_STAGING+"; "
                                "tar czf - "+self.packagename()+" >> "+extract_script+"; "
                                "cd -",
                                shell=True)

    def finish(self):
        super(Packager,self).finish()
