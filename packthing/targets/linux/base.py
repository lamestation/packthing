# -*- coding: utf-8 -*-

from .. import base

class Packager(base.Packager):
    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'deb'
        self.EXT_BIN = ''
        self.EXT_LIB = 'so'
