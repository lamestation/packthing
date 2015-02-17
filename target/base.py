import os, platform
import util, shutil
import logging

class Packager(object):
    def __init__(self, info, version, files):
        self.info = info
        self.VERSION = version
        self.CPU = platform.machine()
        if self.CPU == 'x86_64':
            self.CPU = 'amd64'

        self.NAME        = self.info.attrib['application'].lower()
        self.DIR         = os.getcwd()
        self.DIR_STAGING = os.path.join(self.DIR, 'staging')

        self.DIR_OUT     = self.DIR_STAGING
        self.OUT = {}

        self.files = files

    def clean(self):
        if os.path.exists(self.DIR_STAGING) and os.path.isdir(self.DIR_STAGING):
            shutil.rmtree(self.DIR_STAGING)

    def packagename(self):
        n = self.NAME
        n += '-'+self.VERSION
        n += '-'+self.CPU
        if hasattr(self, 'EXT'):
            n += '.'+self.EXT
        return n

    def copy(self):
        try:
            for outdir in self.files:
                OUTDIR = os.path.join(self.DIR_OUT,self.OUT[outdir])

                logging.info("OUT['"+outdir+"']:"+self.OUT[outdir])

                util.mkdir(OUTDIR)

                for f in self.files[outdir]:
                    shutil.copy(f, OUTDIR)
                    logging.info('  '+f)
        except KeyError:
            raise KeyError("Target doesn't have self.OUT['"+outdir+"'] defined")


    def make(self):
        util.mkdir(self.DIR_STAGING)
        self.copy()
        print self.files
