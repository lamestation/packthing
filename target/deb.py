import os

import shutil
import util
import textwrap

import datetime
import time
from email import utils

from . import base

REQUIRE = [ 'dpkg-deb',
            'dh_fixperms',
            'dpkg-shlibdeps',
            'dpkg-gencontrol',
            'fakeroot',
            'help2man',
            'dh_installmanpages',
            'convert',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'deb'
        self.EXT_BIN = ''
        self.EXT_LIB = 'so'

        self.DIR_DEBIAN  = os.path.join(self.DIR_STAGING,'debian')
        self.DIR_DEBIAN2 = os.path.join(self.DIR_DEBIAN,self.NAME,'DEBIAN')
        self.DIR_OUT     = os.path.join(self.DIR_DEBIAN,self.NAME)
        self.DIR_MENU    = os.path.join(self.DIR_OUT,'usr','share','menu')
        self.DIR_DESKTOP = os.path.join(self.DIR_OUT,'usr','share','applications')
        self.DIR_PIXMAPS = os.path.join(self.DIR_OUT,'usr','share','pixmaps')

        self.OUT['bin'] = os.path.join('usr','bin')
        self.OUT['lib'] = os.path.join('usr','lib')
        self.OUT['share'] = os.path.join('usr','share',self.NAME)

    def control(self):
        script = util.get_template('deb/control')
        rendering = script.substitute(
                        application = self.NAME,
                        maintainer  = self.info.attrib['maintainer'],
                        email       = self.info.attrib['email'],
                        VERSION     = self.VERSION,
                        CPU         = self.CPU,
                        tagline     = self.info.attrib['tagline'],
                        description = textwrap.fill(self.info.attrib['description'], 
                                60, subsequent_indent = ' '),
                        depends     = "${shlibs:Depends}",
                    )
        return rendering

    def changelog(self):
        script = util.get_template('deb/changelog')
        nowdt = datetime.datetime.now()
        nowtuple = nowdt.timetuple()
        nowtimestamp = time.mktime(nowtuple)
        date = utils.formatdate(nowtimestamp)
        rendering = script.substitute(
                        application = self.NAME,
                        maintainer  = self.info.attrib['maintainer'],
                        email       = self.info.attrib['email'],
                        VERSION     = self.VERSION,
                        datetime    = date,  
                    )
        return rendering

    def manpages(self):
        for f in self.files['bin']:
            OUTDIR = os.path.join(self.DIR_OUT,self.OUT['bin'])
            g = os.path.basename(f)

            util.command(['help2man','--no-info',
                    os.path.join(OUTDIR,g),
                    '-o',os.path.join(self.DIR_DEBIAN,g+'.1')],strict=False)

    def menu(self):
        script = util.get_template('deb/menu')
        rendering = script.substitute(
                        NAME        = self.info.attrib['application'],
                        APPLICATION = self.NAME,
                        DESCRIPTION = self.info.attrib['description'],
                        SECTION     = "",
                    )
        return rendering

    def desktop(self):
        script = util.get_template('deb/desktop')
        rendering = script.substitute(
                        NAME        = self.info.attrib['application'],
                        APPLICATION = self.NAME,
                        DESCRIPTION = self.info.attrib['description'],
                        TAGLINE     = self.info.attrib['tagline'],
                        CATEGORIES= "",
                    )
        return rendering

    def icons(self,iconlist):
        for i in iconlist:
            if os.path.exists(i):
                util.mkdir(self.DIR_PIXMAPS)
                util.command(['convert',i,'-resize','32x32',
                        os.path.join(self.DIR_PIXMAPS,
                        os.path.splitext(os.path.basename(i))[0]+'.xpm')])

    def make(self):
        super(Packager,self).make()
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.copy()
#        self.manpages()

        with util.pushd(self.DIR_STAGING):
            util.create(self.control(),  os.path.join(self.DIR_DEBIAN,'control'))
            util.create(self.changelog(),os.path.join(self.DIR_DEBIAN,'changelog'))
            util.create('9',             os.path.join(self.DIR_DEBIAN,'compat'))
            util.create(self.menu(),    os.path.join(self.DIR_MENU,self.NAME))
            util.create(self.desktop(), os.path.join(self.DIR_DESKTOP,self.NAME+'.desktop'))

            util.command(['dpkg-shlibdeps','/usr/bin/propelleride'])
            util.command(['dh_installmanpages'])
            util.command(['fakeroot','dpkg-gencontrol','-v'+self.VERSION,'-P'+self.DIR_OUT])

    def finish(self):
        with util.pushd(self.DIR_STAGING):
            print self.packagename()
            util.command(['dpkg-deb','-b',self.DIR_OUT,self.packagename()])
