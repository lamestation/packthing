# -*- coding: utf-8 -*-

import os, platform
from .. import util
import shutil
import logging

class Packager(object):
    def __init__(self, info, version, files):
        self.info = info
        self.VERSION = version
        self.CPU = platform.machine()
        if self.CPU == 'x86_64':
            self.CPU = 'amd64'

        self.DIR         = os.getcwd()
        self.DIR_STAGING = os.path.join(self.DIR, 'staging')
        self.PREFIX      = 'lib'

        self.DIR_OUT     = self.DIR_STAGING
        self.OUT = {}

        self.files = files

    def clean(self):
        if os.path.exists(self.DIR_STAGING) and os.path.isdir(self.DIR_STAGING):
            shutil.rmtree(self.DIR_STAGING)

    def packagename(self):
        n = self.info['package']
        n += '-'+self.VERSION
        n += '-'+self.CPU
        return n.lower()


    def library(self, target):
        f = self.PREFIX+os.path.basename(target)+'.'+self.EXT_LIB
        return os.path.join(os.path.dirname(target),f)

    def executable(self, target):
        return target+'.'+self.EXT_BIN

    def copy(self):
        try:
            for outdir in self.files:
                OUTDIR = os.path.join(self.DIR_OUT,self.OUT[outdir])

                logging.info("OUT['"+outdir+"']:"+self.OUT[outdir])

                util.mkdir(OUTDIR)

                for f in self.files[outdir]:
                    if outdir == 'bin' and self.EXT_BIN:
                        f = self.executable(f)
                    elif outdir == 'lib':
                        f = self.library(f)
                        
                    if outdir == 'share':
                        outf = os.path.join(OUTDIR,f)
                        util.mkdir(os.path.dirname(outf))
                    else:
                        outf = OUTDIR

                    shutil.copy(f,outf)
                    logging.info('  '+f+' => '+outf)
        except KeyError:
            raise KeyError("Target doesn't have self.OUT['"+outdir+"'] defined")


    def make(self):
        util.mkdir(self.DIR_STAGING)
        util.mkdir(self.DIR_OUT)
        self.copy()

    def finish(self):
        print "Creating",self.packagename()
