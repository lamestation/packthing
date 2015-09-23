# -*- coding: utf-8 -*-

import os
import uuid, subprocess

import packthing.util as util
from .. import base

try:
    from PIL import Image
except:
    util.error("Failed to import Python Imaging Library; is it installed?")

REQUIRE = [ 'iscc',
            'windeployqt',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        #self.EXT = 'exe'
        self.EXT_BIN = 'exe'
        self.EXT_LIB = 'dll'
        self.PREFIX = ''
        self.DIR_OUT = os.path.join(self.DIR_STAGING,'win')

        self.OUT['bin'] = ''
        self.OUT['lib'] = ''
        self.OUT['share'] = ''

    def get_path(self):
        return self.DIR_OUT

    # Taken from innosetup module (https://pypi.python.org/pypi/innosetup/0.6.6)
    def AppID(self):
        src = self.info['url'].encode('ascii')
        appid = uuid.uuid5(uuid.NAMESPACE_URL, src).urn.rsplit(':', 1)[1]
        return '{{%s}' % appid

    def iss(self):
        banner = os.path.join(self.DIR_STAGING,'..\\..\\icons\\win-banner.bmp')
        d = {
            "APPID"           : self.AppID(),
            "ORGANIZATION"    : self.info['org'],
            "NAME"            : self.info['name'],
            "PACKAGENAME"     : self.packagename(),
            "WEBSITE"         : self.info['url'],
            "VERSION"         : self.VERSION,
            "BANNER"          : banner,
            "SOURCEDIR"       : self.DIR_OUT,
            "OUTDIR"          : self.DIR_STAGING,
            "SHORTNAME"       : self.info['package'],
        }
        return util.get_template(os.path.join('win','installer.iss')).substitute(d)

    def icon(self,icon,target):
        if os.path.exists(icon):
            print "Generating icon",icon
            img = Image.open(icon)
            img.thumbnail((256,256),Image.ANTIALIAS)
            img.save(os.path.join(self.DIR_OUT,'win.ico'))

    def make(self):
        super(Packager,self).make()

    def finish(self):
        with util.pushd(self.DIR_STAGING):
            util.write(self.iss(), 'installer.iss')

            print "-----------------------------------------------------"
            print "Current directory:",os.getcwd()
            for f in os.listdir('.'):
                print "  File",f

            print "InnoSetup dir:"
            for f in os.listdir('C:\\Program Files (x86)\\Inno Setup 5\\'):
                print "  File",f

            print "Running iscc"

            subprocess.check_call(['C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe','installer.iss'])
            print "-----------------------------------------------------"
