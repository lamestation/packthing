# -*- coding: utf-8 -*-

import os
import uuid, subprocess

import packthing.util as util

try:
    from PIL import Image
except:
    util.error("Failed to import Python Imaging Library; is it installed?")

REQUIRE = [ 'iscc',
            'windeployqt',
            ]

KEYS = [ 'banner' ]

from . import _base

class Packager(_base.Packager):

    def __init__(self, config, files):
        super(Packager,self).__init__(config, files)

        self.EXT_BIN = 'exe'
        self.EXT_LIB = 'dll'
        self.LIB_PREFIX = ''
        self.DIR_OUT = os.path.join(self.DIR_STAGING,'win')

        self.OUT['bin'] = ''
        self.OUT['lib'] = ''
        self.OUT['share'] = ''

    def get_path(self):
        return self.DIR_OUT

    # Taken from innosetup module (https://pypi.python.org/pypi/innosetup/0.6.6)
    def AppID(self):
        src = self.config['url'].encode('ascii')
        appid = uuid.uuid5(uuid.NAMESPACE_URL, src).urn.rsplit(':', 1)[1]
        return '{{%s}' % appid

    def iss_setup(self):
        bannerpath = os.path.join(self.DIR,
                              self.config['master'],
                              self.config['banner'].replace('/','\\'))
        d = {
            "APPID"         : self.AppID(),
            "ORGANIZATION"  : self.config['org'],
            "NAME"          : self.config['name'],
            "PACKAGENAME"   : self.packagename(),
            "WEBSITE"       : self.config['url'],
            "VERSION"       : self.config['version'],
            "BANNER"        : bannerpath,
            "SOURCEDIR"     : self.DIR_OUT,
            "OUTDIR"        : self.DIR_STAGING,
        }
        return util.get_template('inno/setup.iss').substitute(d)

    def iss_file(self, target):
        d = {
            "NAME"          : self.config['files'][target]['name'],
            "FILENAME"      : target,
        }
        return util.get_template('inno/file.iss').substitute(d)

    def iss_run(self, target):
        d = {
            "NAME"          : self.config['files'][target]['name'],
            "FILENAME"      : target,
        }
        return util.get_template('inno/run.iss').substitute(d)

    def icon(self,icon,target):
        print "Generating icon for",target+'.exe'
        icon = icon.replace('/','\\')
        if os.path.exists(icon):
            img = Image.open(icon)
            img.thumbnail((256,256),Image.ANTIALIAS)
            img.save(os.path.join(self.DIR_OUT,target+'.ico'))

            self.iss += self.iss_file(target)

            if 'run' in self.config and target in self.config['run']:
                self.iss += self.iss_run(target)
        else:
            util.error("Icon does not exist:", icon)

    def make(self):
        super(Packager,self).make()

        self.iss = self.iss_setup()+'\n'

    def finish(self):
        super(Packager,self).finish()

        with util.pushd(self.DIR_STAGING):
            util.write(self.iss, 'installer.iss')
            subprocess.check_call(['C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe','installer.iss'])

    def install(self):
        with util.pushd(self.DIR_STAGING):
            try:
                util.command(['.\\'+self.packagename()+'.exe'])
            except:
                util.error("Installation failed! Oh, well.")
