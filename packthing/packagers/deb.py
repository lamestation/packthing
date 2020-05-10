# -*- coding: utf-8 -*-

import datetime
import os
import shutil
import sys
import textwrap
import time
from email import utils

import packthing.icons as icons
import packthing.util as util

from . import _linux

REQUIRE = [
    "dpkg-deb",
    "dh_fixperms",
    "dpkg-shlibdeps",
    "dpkg-gencontrol",
    "dh_installmanpages",
    "convert",
]

KEYS = [
    "depends",
    "section",
    "categories",
]

util.root()


class Packager(_linux.Packager):
    def __init__(self, config, files):
        super(Packager, self).__init__(config, files)

        self.PREFIX = "usr"
        self.EXT = "deb"

        self.DIR_DEBIAN = os.path.join(self.DIR_STAGING, "debian")
        self.DIR_DEBIAN2 = os.path.join(
            self.DIR_DEBIAN, self.config["package"], "DEBIAN"
        )
        self.DIR_OUT = os.path.join(self.DIR_DEBIAN, self.config["package"])

        self.OUT["bin"] = os.path.join("usr", "bin")
        self.OUT["lib"] = os.path.join("usr", "lib")
        self.OUT["share"] = os.path.join("usr", "share", self.config["package"])

        self.DIR_MENU = os.path.join(self.DIR_OUT, "usr", "share", "menu")
        self.DIR_DESKTOP = os.path.join(self.DIR_OUT, "usr", "share", "applications")
        self.DIR_PIXMAPS = os.path.join(self.DIR_OUT, "usr", "share", "pixmaps")
        self.DIR_ICONS = os.path.join(self.DIR_OUT, "usr", "share", "icons")
        self.DIR_MIMETYPES = os.path.join(
            self.DIR_ICONS, "gnome", "scalable", "mimetypes"
        )

    def postinst(self):
        return util.get_template("deb/postinst").substitute(dict())

    def control(self):
        depends = "${shlibs:Depends}"
        if "depends" in self.config:
            depends += ", " + self.config["depends"]

        d = {
            "PACKAGE": self.config["package"],
            "MAINTAINER": self.config["maintainer"],
            "EMAIL": self.config["email"],
            "VERSION": self.config["version"],
            "MACHINE": self.config["machine"],
            "TAGLINE": self.config["tagline"],
            "DESCRIPTION": textwrap.fill(
                self.config["description"], 60, subsequent_indent=" "
            ),
            "DEPENDS": depends,
        }
        return util.get_template("deb/control").substitute(d)

    def changelog(self):
        now = datetime.datetime.now().timetuple()
        date = utils.formatdate(time.mktime(now))

        d = {
            "PACKAGE": self.config["package"],
            "MAINTAINER": self.config["maintainer"],
            "EMAIL": self.config["email"],
            "VERSION": self.config["version"],
            "DATETIME": date,
        }
        return util.get_template("deb/changelog").substitute(d)

    def help2man(self):
        if not util.which("help2man"):
            util.warning("help2man not found; skipping man page generation")
            return

        OUTDIR = os.path.join(self.DIR_OUT, self.OUT["bin"])
        for f in self.files["bin"]:
            g = os.path.basename(f)

            if g in self.config["help2man"]:
                util.command(
                    [
                        "help2man",
                        "--no-info",
                        "--source=" + self.config["package"],
                        os.path.join(OUTDIR, g),
                        "-o",
                        os.path.join(self.DIR_DEBIAN, g + ".1"),
                    ],
                    strict=False,
                )

    def menu(self, filename, config):
        d = {
            "NAME": config["name"],
            "PACKAGE": filename,
            "DESCRIPTION": self.config["description"],
            "SECTION": self.config["section"],
            "FILENAME": filename,
            "ICON": filename,
        }
        return util.get_template("deb/menu").substitute(d)

    def desktop(self, filename, config):
        d = {
            "NAME": config["name"],
            "PACKAGE": filename,
            "DESCRIPTION": self.config["description"],
            "TAGLINE": self.config["tagline"],
            "CATEGORIES": self.config["categories"],
            "FILENAME": filename,
            "ICON": filename,
        }
        output = util.get_template("deb/desktop").substitute(d)

        if "mimetypes" in list(config.keys()):
            mimestring = "MimeType="

            first = True
            for mimetype in config["mimetypes"]:
                if first:
                    first = False
                    mimestring += mimetype["type"]
                else:
                    mimestring += ";" + mimetype["type"]

            output += mimestring

        return output

    def package_mime(self, filename, mimetypes):
        output = ""

        for mimetype in mimetypes:
            d = {
                "TYPE": mimetype["type"],
                "EXECUTABLE": filename,
                "DESCRIPTION": mimetype["description"],
            }
            output += util.get_template("deb/package.mime").substitute(d)

        return output

    def package_sharedmimeinfo(self, mimetypes):
        output = util.get_template_text("deb/package.sharedmimeinfo.header")

        for mimetype in mimetypes:
            d = {
                "TYPE": mimetype["type"],
                "EXTENSION": mimetype["extension"],
                "DESCRIPTION": mimetype["description"],
            }
            output += util.get_template("deb/package.sharedmimeinfo.body").substitute(d)

        output += util.get_template_text("deb/package.sharedmimeinfo.footer")

        return output

    def icon(self, icon, executable):
        icons.imagemagick(
            os.path.join(executable, icon),
            os.path.join(self.DIR_PIXMAPS, executable + ".png"),
            128,
            "png",
        )

    def mime_icon(self, mimetype, executable, size):
        iconname = os.path.basename(mimetype["icon"])
        icons.imagemagick(
            os.path.join(executable, mimetype["icon"]),
            os.path.join(
                self.DIR_ICONS,
                "gnome",
                str(size) + "x" + str(size),
                "mimetypes",
                iconname,
            ),
            size,
            "png",
        )

    def mimetypes(self, mimetypes, executable, reponame):

        util.create(
            self.package_mime(executable, mimetypes),
            os.path.join(self.DIR_DEBIAN, executable + ".mime"),
        )
        util.create(
            self.package_sharedmimeinfo(mimetypes),
            os.path.join(self.DIR_DEBIAN, executable + ".sharedmimeinfo"),
        )

        for mimetype in mimetypes:
            #            util.copy(os.path.join(executable, mimetype['icon']), self.DIR_MIMETYPES)

            for size in [8, 16, 22, 24, 32, 48, 128, 256, 512]:
                self.mime_icon(mimetype, executable, size)

    def make(self):
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.install_files()

        if "help2man" in self.config:
            self.help2man()

        with util.pushd(self.DIR_STAGING):
            util.create(self.control(), os.path.join(self.DIR_DEBIAN, "control"))
            util.create(self.changelog(), os.path.join(self.DIR_DEBIAN, "changelog"))
            util.create("9", os.path.join(self.DIR_DEBIAN, "compat"))
            util.create(self.postinst(), os.path.join(self.DIR_DEBIAN, "postinst"))

            if "files" in self.config:
                for i in list(self.config["files"].keys()):
                    if (
                        "name" in self.config["files"][i]
                        and "icon" in self.config["files"][i]
                    ):
                        util.create(
                            self.menu(i, self.config["files"][i]),
                            os.path.join(self.DIR_MENU, i),
                        )
                        util.create(
                            self.desktop(i, self.config["files"][i]),
                            os.path.join(self.DIR_DESKTOP, i + ".desktop"),
                        )

    def finish(self):
        super(Packager, self).finish()

        with util.pushd(self.DIR_STAGING):

            executables = []
            for f in self.files["bin"]:
                OUTDIR = os.path.join(self.DIR_OUT, self.OUT["bin"])
                outf = os.path.join(OUTDIR, f)
                executables.append(outf)

            util.cksum(executables)

            deps = ["dpkg-shlibdeps", "--ignore-missing-info"]
            deps.extend(executables)

            for f in executables:
                deps.append(outf)

            if len(self.files["bin"]) > 0:
                util.command(deps)

            util.command(["dh_installmanpages"])
            util.command(["dh_installmenu"])
            util.command(["dh_installmime"])
            util.command(["dh_installdeb"])
            util.command(["dh_icons"])
            util.command(["dh_desktop"])

            try:
                util.command(
                    [
                        "dpkg-gencontrol",
                        "-v" + self.config["version"],
                        "-P" + self.DIR_OUT,
                    ]
                )
            except:
                sys.exit(1)

            util.command(["dh_fixperms"])
            util.command(["dpkg-deb", "-b", self.DIR_OUT, self.packagename() + ".deb"])

    def install(self):
        with util.pushd(self.DIR_STAGING):
            try:
                util.command(["dpkg", "-i", self.packagename() + ".deb"])
            except:
                util.error("Installation failed! Oh, well.")
