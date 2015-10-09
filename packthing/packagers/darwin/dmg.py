# -*- coding: utf-8 -*-
import os, re, sys
import plistlib
import subprocess
import shutil
import glob

import packthing.util as util
from .. import base

REQUIRE = [ 'macdeployqt',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.volumename = self.packagename()

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
            CFBundleName = self.info['name'],
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

    def mac_installer(self):
        script = util.get_template('mac/installer.AppleScript')
        rendering = script.substitute(
                        title = self.volumename,
                        background = os.path.basename(self.background),
                        applicationName = os.path.basename(self.DIR_BUNDLE)
                    )
        return rendering


    def make(self):
        super(Packager,self).make()
        with util.pushd(self.DIR_OUT):
            plistlib.writePlist(self.build_plist(self.info, None), 
                    os.path.join(self.DIR_OUT,'Info.plist'))

    def generate_icon(self,icon,size,targetdir,addition=False):
        iconname = 'icon_'
        if addition == True:
            iconname += str(int(size)/2)+'x'+str(int(size)/2)
            iconname += '@2x'
        else:
            iconname += size+'x'+size
        iconname += '.png'
        util.command(['sips','-z',size,size,icon,
                '--out',os.path.join(targetdir,iconname)])

    def icon(self,icon,target):
        if os.path.exists(icon):
            DIR_ICNS = os.path.join(self.DIR_STAGING,'mac.iconset')
            util.mkdir(DIR_ICNS)
            self.generate_icon(icon,'16',DIR_ICNS,False)
            self.generate_icon(icon,'32',DIR_ICNS,True)
            self.generate_icon(icon,'32',DIR_ICNS,False)
            self.generate_icon(icon,'64',DIR_ICNS,True)
            self.generate_icon(icon,'64',DIR_ICNS,False)
            self.generate_icon(icon,'128',DIR_ICNS,False)
            self.generate_icon(icon,'256',DIR_ICNS,True)
            self.generate_icon(icon,'256',DIR_ICNS,False)
            self.generate_icon(icon,'512',DIR_ICNS,True)
            self.generate_icon(icon,'512',DIR_ICNS,False)
            util.command(['iconutil','-c','icns',
                '--output',os.path.join(self.DIR_OUT,self.OUT['share'],'mac.icns'),DIR_ICNS])
            shutil.rmtree(DIR_ICNS)

#    def build_volume(self, name):

    def finish(self):
        target = os.path.join(self.DIR_STAGING, self.packagename()+'.dmg')

        # this is hacky and needs to be changed
        self.background = '../icons/mac-dmg.png'

        size = util.command(['du','-s',self.DIR_BUNDLE])[0].split()[0]
        size = str(int(size)+1000)
        tmpdevice = os.path.join(self.DIR_PACKAGE, 'pack.temp.dmg')

        existingdevices = glob.glob("/Volumes/"+self.volumename+"*")
        for d in existingdevices:
            try:
                util.command(['hdiutil','detach',d])
            except subprocess.CalledProcessError as e:
                util.error("Couldn't unmount "+d+"; close all programs using this Volume and try again.")

        util.command(['hdiutil','create',
            '-format','UDRW',
            '-srcfolder',self.DIR_BUNDLE,
            '-volname',self.volumename,
            '-size',size+'k',
            tmpdevice])

        devices = util.command(['hdiutil','attach',
            '-readwrite',
            tmpdevice])

        device = glob.glob("/Volumes/"+self.volumename+"*")[0]

        DIR_VOLUME = os.path.join(os.sep,'Volumes',self.volumename,'.background')
        util.copy(self.background, DIR_VOLUME)

        util.command(['sync'])

        print self.mac_installer()
        util.command(['osascript'], stdinput=self.mac_installer())

        util.command(['chmod','-Rf','go-w',DIR_VOLUME])
        util.command(['chmod','-Rf','go-w',
                        os.path.join(os.path.dirname(DIR_VOLUME),
                        self.info['name']+'.app')])
        util.command(['chmod','-Rf','go-w',
                        os.path.join(os.path.dirname(DIR_VOLUME),
                        'Applications')])

        util.command(['sync'])
        util.command(['hdiutil','detach',device])
        util.command(['hdiutil','convert',tmpdevice,'-format','UDZO',
            '-imagekey','zlib-level=9','-o',target])

        os.remove(tmpdevice)
