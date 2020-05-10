# -*- coding: utf-8 -*-
import glob
import os
import plistlib
import re
import shutil
import subprocess
import sys
import time

import packthing.util as util

from . import _base

REQUIRE = ["dmgbuild", "macdeployqt"]

KEYS = ["category", "background", "bundle"]


class Packager(_base.Packager):
    def __init__(self, config, files):
        super(Packager, self).__init__(config, files)

        self.volumename = self.packagename()

        self.EXT = "dmg"
        self.EXT_BIN = ""
        self.EXT_LIB = "dylib"
        self.DIR_PACKAGE = os.path.join(self.DIR_STAGING, "mac")
        self.DIR_BUNDLE = os.path.join(self.DIR_PACKAGE, self.config["name"] + ".app")
        self.DIR_OUT = os.path.join(self.DIR_BUNDLE, "Contents")
        self.DIR_RESOURCES = os.path.join(self.DIR_OUT, "Resources")

        self.OUT["bin"] = "MacOS"
        self.OUT["lib"] = "MacOS"
        self.OUT["share"] = "Resources"

    def get_path(self):
        return self.DIR_BUNDLE

    def bundle_identifier(self):
        return (
            "com."
            + self.config["org"].lower().split(" ")[0]
            + "."
            + self.config["package"].lower()
        )

    def build_plist(self, config, target):
        pl = dict(
            CFBundleDevelopmentRegion="English",
            CFBundleDisplayName=self.config["name"],
            CFBundleExecutable=self.config["package"],
            CFBundleIdentifier=self.bundle_identifier(),
            CFBundleInfoDictionaryVersion="6.0",
            CFBundleName=self.config["name"],
            CFBundlePackageType="APPL",
            CFBundleShortVersionString=self.config["version"],
            CFBundleVersion="1",
            LSApplicationCategoryType=self.config["category"],
            LSMinimumSystemVersion="10.7",
            NSHumanReadableCopyright="Copyright © "
            + self.config["copyright"]
            + ", "
            + self.config["org"]
            + ". "
            + self.config["name"]
            + " is released under the "
            + self.config["license"]
            + " license.",
            NSPrincipalClass="NSApplication",
            NSSupportsSuddenTermination="YES",
        )
        return pl

    def mac_installer(self):
        d = {
            "VOLUME": self.volumename,
            "BACKGROUND": os.path.basename(self.config["background"]),
            "BUNDLE": os.path.basename(self.DIR_BUNDLE),
        }
        return util.get_template("dmg/installer.AppleScript").substitute(d)

    def mac_install(self):
        d = {
            "VOLUME": self.volumename,
        }
        return util.get_template("dmg/install.AppleScript").substitute(d)

    def make(self):
        super(Packager, self).make()

        self.plist = self.build_plist(self.config, None)

    def generate_icon(self, icon, size, targetdir, addition=False):
        iconname = "icon_"
        if addition == True:
            iconname += str(int(size) / 2) + "x" + str(int(size) / 2)
            iconname += "@2x"
        else:
            iconname += size + "x" + size
        iconname += ".png"
        util.command(
            ["sips", "-z", size, size, icon, "--out", os.path.join(targetdir, iconname)]
        )

    def icon(self, icon, executable):
        icon = os.path.join(executable, icon)
        if os.path.exists(icon):
            self.plist.update(dict(CFBundleIconFile="mac.icns"))

            if executable == self.config["bundle"]:
                DIR_ICNS = os.path.join(self.DIR_STAGING, "mac.iconset")
                util.mkdir(DIR_ICNS)
                self.generate_icon(icon, "16", DIR_ICNS, False)
                self.generate_icon(icon, "32", DIR_ICNS, True)
                self.generate_icon(icon, "32", DIR_ICNS, False)
                self.generate_icon(icon, "64", DIR_ICNS, True)
                self.generate_icon(icon, "64", DIR_ICNS, False)
                self.generate_icon(icon, "128", DIR_ICNS, False)
                self.generate_icon(icon, "256", DIR_ICNS, True)
                self.generate_icon(icon, "256", DIR_ICNS, False)
                self.generate_icon(icon, "512", DIR_ICNS, True)
                self.generate_icon(icon, "512", DIR_ICNS, False)
                util.command(
                    [
                        "iconutil",
                        "-c",
                        "icns",
                        "--output",
                        os.path.join(self.DIR_OUT, self.OUT["share"], "mac.icns"),
                        DIR_ICNS,
                    ]
                )
                shutil.rmtree(DIR_ICNS)
        else:
            util.error("Icon does not exist:", icon)

    def mimetypes(self, mimetypes, executable, reponame):
        documenttypes = []

        for mimetype in mimetypes:
            # self.+= self.iss_mime(mimetype, executable, reponame)
            documenttypes.append(
                dict(
                    CFBundleTypeName=mimetype["description"],
                    CFBundleTypeExtensions=[mimetype["extension"],],
                    CFBundleTypeIconFile="mac",
                    CFBundleTypeRole="Editor",
                    LSItemContentTypes=[
                        self.bundle_identifier() + "." + mimetype["extension"]
                    ],
                    LSIsAppleDefaultForType=True,
                    LSHandlerRank="Owner",
                )
            )

        self.plist.update(dict(CFBundleDocumentTypes=documenttypes))

    def finish(self):
        super(Packager, self).finish()

        # create plist file
        with util.pushd(self.DIR_OUT):
            plistlib.writePlist(self.plist, os.path.join(self.DIR_OUT, "Info.plist"))

        background_path = os.path.abspath(
            os.path.join(self.config["master"], self.config["background"])
        )
        icon_path = os.path.join(self.DIR_RESOURCES, "mac.icns")
        app_name = self.config["name"]
        bundle_name = f"{app_name}.app"
        dmg_name = f"{app_name}.dmg"

        dmgbuild_settings_file = os.path.join(self.DIR_PACKAGE, "settings.py")
        dmgbuild_settings = util.get_template(
            os.path.join("dmg", "dmgbuild.py")
        ).substitute(
            dict(
                bundle_name=bundle_name,
                icon_path=icon_path,
                background_path=background_path,
            )
        )

        with open(dmgbuild_settings_file, "w") as handle:
            handle.write(dmgbuild_settings)

        with util.pushd(self.DIR_PACKAGE):
            cmd = [
                "dmgbuild",
                "-s",
                dmgbuild_settings_file,
                app_name,
                dmg_name,
            ]
            print(cmd)
            subprocess.check_call(cmd)
