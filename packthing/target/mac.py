# -*- coding: utf-8 -*-
import os
from .. import util
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
        self.DIR_PACKAGE = os.path.join(self.DIR_STAGING,'mac')
        self.DIR_BUNDLE = os.path.join(self.DIR_PACKAGE,self.info['package']+'.app')
        self.DIR_OUT = os.path.join(self.DIR_BUNDLE,'Contents')

        self.OUT['bin'] = 'MacOS'
        self.OUT['lib'] = 'MacOS'
        self.OUT['share'] = 'Resources'

    def get_path(self):
        return self.DIR_BUNDLE

    def bundle_identifier(self):
        return 'com.'+self.info['org'].lower()+self.info['name']

    def build_plist(self, info, target):
        pl = dict(
            CFBundleDevelopmentRegion = "English",
            CFBundleDisplayName = self.info['name'],
            CFBundleExecutable = self.info['package'],
            CFBundleIconFile = "mac.icns",
            CFBundleIdentifier = self.bundle_identifier(),
            CFBundleInfoDictionaryVersion = "6.0",
            CFBundleName = self.info['package'],
            CFBundlePackageType = "APPL",
            CFBundleShortVersionString = self.VERSION,
            CFBundleVersion = "1",
            LSApplicationCategoryType = 'public.app-category.developer-tools',
            LSMinimumSystemVersion = "10.7",
            NSHumanReadableCopyright = u"Copyright © "+self.info['copyright']
                    +", "+self.info['org']+". "
                    +self.info['name']
                    +" is released under the "
                    +self.info['license']+" license.",
            NSPrincipalClass = "NSApplication",
            NSSupportsSuddenTermination = "YES",
        )
        return pl

    def make(self):
        super(Packager,self).make()
        with util.pushd(self.DIR_OUT):
            plistlib.writePlist(self.build_plist(self.info, None), 
                    os.path.join(self.DIR_OUT,'Info.plist'))

        util.command(['dmg','/usr/bin/propelleride'])
	    $(DIR_DIST)/dmg.sh \
			$(DIR_STAGING)/$(TITLE).app \
			$(TITLE) \
			$(DIR_STAGING)/$(NAME)-$(VERSION)-$(CPU).dmg \
			$(shell $(REPO) --gfx)/mac-dmg.png

    def finish(self):
        pass
