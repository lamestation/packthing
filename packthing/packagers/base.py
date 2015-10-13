# -*- coding: utf-8 -*-

import os, platform
from .. import util
import shutil
import subprocess

KEYS = [
        'name',
        'package',
        'org',
        'url',
        'maintainer',
        'email',
        'copyright',
        'license',
        'tagline',
        'description',
        ]

class Packager(object):
    def __init__(self, info, version, files):
        self.info = info
        self.VERSION = version
        self.SYSTEM = platform.system().lower()
        self.CPU = platform.machine()
        if self.CPU == 'x86_64':
            self.CPU = 'amd64'

        self.PREFIX = ''

        self.EXT = ''
        self.EXT_BIN = ''
        self.EXT_LIB = ''
        self.LIB_PREFIX = 'lib'

        self.DIR         = os.getcwd()
        self.DIR_STAGING = os.path.join(self.DIR, 'staging')

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
        f = self.LIB_PREFIX+os.path.basename(target)+'.'+self.EXT_LIB
        return os.path.join(os.path.dirname(target),f)

    def executable(self, target):
        return target+'.'+self.EXT_BIN

    def copy(self):
        for outdir in self.files:
            OUTDIR = os.path.join(self.DIR_OUT,self.OUT[outdir])

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

    def install_files(self):
        for outdir in self.files:
            OUTDIR = os.path.join(self.DIR_OUT,self.OUT[outdir])

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

                perm  = '644'
                if outdir == 'bin':
                    perm = '755'

                if outdir == 'bin' or outdir == 'lib':
                    try:
                        util.command(['install','-m',perm,'-s',f,outf])
                    except subprocess.CalledProcessError as e:
                        util.command(['install','-m',perm,f,outf])
                    except subprocess.CalledProcessError as e:
                        raise Exception
                else:
                    try:
                        util.command(['install','-m',perm,f,outf])
                    except subprocess.CalledProcessError as e:
                        raise Exception

    def make(self):
        util.mkdir(self.DIR_STAGING)
        util.mkdir(self.DIR_OUT)
        self.copy()

    def finish(self):
        text = self.packagename()
        if not self.EXT == '':
            text += "."+self.EXT
        print "Creating",text
