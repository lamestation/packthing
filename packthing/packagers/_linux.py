# -*- coding: utf-8 -*-

import os

from . import _base

class Packager(_base.Packager):

    def __init__(self, info, files):
        super(Packager,self).__init__(info, files)

        self.EXT_BIN = ''
        self.EXT_LIB = 'so'

        self.OUT['bin'] = os.path.join('bin')
        self.OUT['lib'] = os.path.join('lib')
        self.OUT['share'] = os.path.join('share',self.info['package'])

        self.DIR_OUT = os.path.join(self.DIR_OUT,self.packagename())

    def make(self):
        self.install_files()

    def finish(self):
        super(Packager,self).finish()
