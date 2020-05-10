# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

from .. import util

KEYS = [
    "name",
    "package",
    "org",
    "url",
    "maintainer",
    "email",
    "copyright",
    "license",
    "tagline",
    "description",
    "system",
    "machine",
]


class Packager(object):
    def __init__(self, config, files):
        self.config = config

        self.PREFIX = ""

        self.EXT = ""
        self.EXT_BIN = ""
        self.EXT_LIB = ""
        self.LIB_PREFIX = "lib"

        self.DIR = os.getcwd()
        self.DIR_STAGING = os.path.join(self.DIR, "staging")

        self.DIR_OUT = self.DIR_STAGING
        self.OUT = {}

        self.files = files

    def clean(self):
        if os.path.exists(self.DIR_STAGING) and os.path.isdir(self.DIR_STAGING):
            try:
                shutil.rmtree(self.DIR_STAGING)
            except OSError as e:
                util.error(
                    "You do not have permission to delete this file:\n" + e.filename
                )

    def packagename(self):
        n = self.config["package"]
        n += "-" + self.config["version"]
        n += "-" + self.config["machine"]
        return n.lower()

    def library(self, target):
        f = self.LIB_PREFIX + os.path.basename(target) + "." + self.EXT_LIB
        return os.path.join(os.path.dirname(target), f)

    def executable(self, target):
        return target + "." + self.EXT_BIN

    def copy(self):
        for outdir in self.files:
            OUTDIR = os.path.join(self.DIR_OUT, self.OUT[outdir])

            util.mkdir(OUTDIR)

            for f in self.files[outdir]:
                if outdir == "bin" and self.EXT_BIN:
                    f = self.executable(f)
                elif outdir == "lib":
                    f = self.library(f)

                if outdir == "share":
                    outf = os.path.join(OUTDIR, f)
                    util.mkdir(os.path.dirname(outf))
                else:
                    outf = OUTDIR

                shutil.copy(f, outf)

    def install_files(self):
        executables = []
        for outdir in self.files:
            OUTDIR = os.path.join(self.DIR_OUT, self.OUT[outdir])

            util.mkdir(OUTDIR)

            for f in self.files[outdir]:
                if outdir == "bin" and self.EXT_BIN:
                    f = self.executable(f)
                elif outdir == "lib":
                    f = self.library(f)

                if outdir == "share":
                    outf = os.path.join(OUTDIR, f)
                    util.mkdir(os.path.dirname(outf))
                else:
                    outf = OUTDIR

                perm = "644"
                if outdir == "bin":
                    perm = "755"

                if outdir == "bin" or outdir == "lib":
                    try:
                        #                        util.command(['install','-m',perm,'-s',f,outf])
                        #                    except subprocess.CalledProcessError as e:
                        util.command(["install", "-m", perm, f, outf])
                    except subprocess.CalledProcessError as e:
                        raise Exception

                    if outdir == "bin":
                        executables.append(os.path.join(outf, os.path.basename(f)))

                else:
                    try:
                        util.command(["install", "-m", perm, f, outf])
                    except subprocess.CalledProcessError as e:
                        raise Exception

        util.cksum(executables)
        util.command(["sync"])

    def make(self):
        util.mkdir(self.DIR_STAGING)
        util.mkdir(self.DIR_OUT)
        self.copy()

    def finish(self):
        text = self.packagename()
        if not self.EXT == "":
            text += "." + self.EXT
        util.subtitle("Building package: " + text)
