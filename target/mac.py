# -*- coding: utf-8 -*-
import os, util
import plistlib

from . import base

REQUIRE = [ 'macdeployqt',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'dmg'
        self.EXT_BIN = ''
        self.EXT_LIB = 'dylib'
        self.DIR_OUT = os.path.join(self.DIR_STAGING,self.NAME+'.app','Contents')

        self.OUT['bin'] = 'MacOS'
        self.OUT['lib'] = 'MacOS'
        self.OUT['share'] = 'Resources'

    def bundle_identifier(self):
        return 'com.'+self.info.attrib['organization'].lower()+self.info.attrib['application']

    def build_plist(self, info, target):
        pl = dict(
            CFBundleDevelopmentRegion = "English",
            CFBundleDisplayName = self.info.attrib['application'],
            CFBundleExecutable = self.NAME,
            CFBundleIconFile = "mac.icns",
            CFBundleIdentifier = self.bundle_identifier(),
            CFBundleInfoDictionaryVersion = "6.0",
            CFBundleName = self.NAME,
            CFBundlePackageType = "APPL",
            CFBundleShortVersionString = self.VERSION,
            CFBundleVersion = "1",
            LSApplicationCategoryType = 'public.app-category.developer-tools',
            LSMinimumSystemVersion = "10.7",
            NSHumanReadableCopyright = u"Copyright © "+self.info.attrib['copyright']
                    +", "+self.info.attrib['organization']+". "
                    +self.info.attrib['application']
                    +" is released under the "
                    +self.info.attrib['license']+" license.",
            NSPrincipalClass = "NSApplication",
            NSSupportsSuddenTermination = "YES",
        )
        return pl

    def make(self):
        super(Packager,self).make()
        with util.pushd(self.DIR_OUT):
            plistlib.writePlist(self.build_plist(self.info, None), 
                    os.path.join(self.DIR_OUT,'Info.plist'))
            for f in self.files['bin']:
                util.command(['macdeployqt',os.path.join(self.OUT['bin'],f)])
