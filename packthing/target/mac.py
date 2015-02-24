# -*- coding: utf-8 -*-
import os, re
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
        self.DIR_BUNDLE = os.path.join(self.DIR_PACKAGE,self.info['name']+'.app')
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

    def infofile(self):
        script = util.get_template('deb/desktop')
        rendering = script.substitute(
                        title = self.info['name'],
                        background = 'icons/mac-dmg.png',
                        applicationName = os.path.basename(self.DIR_BUNDLE)
                    )
        return rendering


    def make(self):
        super(Packager,self).make()
        with util.pushd(self.DIR_OUT):
            plistlib.writePlist(self.build_plist(self.info, None), 
                    os.path.join(self.DIR_OUT,'Info.plist'))

#	util.command(['macdeployqt',self.DIR_BUNDLE])

        source = self.DIR_BUNDLE
        title = self.info['name']
        target = os.path.join(self.DIR_STAGING, self.packagename())
        background = 'icons/mac-dmg.png'

        size = util.command(['du','-s',self.DIR_BUNDLE])[0].split()[0]
        size = str(int(size)+1000)
        print size
        tmpdevice = os.path.join(self.DIR_PACKAGE, 'pack.temp.dmg')

        util.command(['hdiutil','create','-srcfolder',self.DIR_BUNDLE,'-volname',
                self.info['name'],'-fs','HFS+','-fsargs','"-c c=64,a=16,e=16"',
                '-format','UDRW','-size',size+'k',tmpdevice])

        devices = util.command(['hdiutil','attach','-readwrite','-noverify','-noautoopen',
            tmpdevice])[0].splitlines()

        r = re.compile('^/dev/')
        devices = filter(r.match, devices)
        device = devices[0].split()[0]

        DIR_VOLUME = os.path.join(os.sep,'Volumes',self.info['name'],'.background')
        util.mkdir(DIR_VOLUME)
        shutil.copyfile(background, DIR_VOLUME)

        util.command(['osascript','-'],stdinput=self.infofile())

        util.command(['chmod','-Rf','go-w',os.path.dirname(DIR_VOLUME)])
        util.command(['sync'])
        util.command(['sync'])
        util.command(['hdiutil','detach',device])
        util.command(['hdiutil','convert',tmpdevice,'-format','UDZO',
            '-imagekey','zlib-level=9','-o',target])
        os.remove(tmpdevice)

    def finish(self):
        pass
