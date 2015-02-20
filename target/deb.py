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
        self.DIR_DEBIAN2 = os.path.join(self.DIR_DEBIAN,self.info['package'],'DEBIAN')
        self.DIR_OUT     = os.path.join(self.DIR_DEBIAN,self.info['package'])
        self.DIR_MENU    = os.path.join(self.DIR_OUT,'usr','share','menu')
        self.DIR_DESKTOP = os.path.join(self.DIR_OUT,'usr','share','applications')
        self.DIR_PIXMAPS = os.path.join(self.DIR_OUT,'usr','share','pixmaps')

        self.OUT['bin'] = os.path.join('usr','bin')
        self.OUT['lib'] = os.path.join('usr','lib')
        self.OUT['share'] = os.path.join('usr','share',self.info['package'])

    def control(self):
        script = util.get_template('deb/control')
        depends     = "${shlibs:Depends}"
        if 'depends' in self.info:
            depends += ', '+self.info['depends']
        rendering = script.substitute(
                        application = self.info['package'],
                        maintainer  = self.info['maintainer'],
                        email       = self.info['email'],
                        VERSION     = self.VERSION,
                        CPU         = self.CPU,
                        tagline     = self.info['tagline'],
                        description = textwrap.fill(self.info['description'], 
                                60, subsequent_indent = ' '),
                        depends     = depends,
                    )
        return rendering

    def changelog(self):
        script = util.get_template('deb/changelog')
        nowdt = datetime.datetime.now()
        nowtuple = nowdt.timetuple()
        nowtimestamp = time.mktime(nowtuple)
        date = utils.formatdate(nowtimestamp)
        rendering = script.substitute(
                        application = self.info['package'],
                        maintainer  = self.info['maintainer'],
                        email       = self.info['email'],
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
        section = ""
        if 'section' in self.info:
            section += self.info['section']
        rendering = script.substitute(
                        NAME        = self.info['name'],
                        APPLICATION = self.info['package'],
                        DESCRIPTION = self.info['description'],
                        SECTION     = "",
                    )
        return rendering

    def desktop(self):
        script = util.get_template('deb/desktop')
        categories = ""
        if 'categories' in self.info:
            categories += self.info['categories']
        rendering = script.substitute(
                        NAME        = self.info['name'],
                        APPLICATION = self.info['package'],
                        DESCRIPTION = self.info['description'],
                        TAGLINE     = self.info['tagline'],
                        CATEGORIES  = categories,
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
            util.create(self.menu(),    os.path.join(self.DIR_MENU,self.info['package']))
            util.create(self.desktop(), os.path.join(self.DIR_DESKTOP,self.info['package']+'.desktop'))

            util.command(['dpkg-shlibdeps','/usr/bin/propelleride'])
            util.command(['dh_installmanpages'])
            util.command(['fakeroot','dpkg-gencontrol','-v'+self.VERSION,'-P'+self.DIR_OUT])

    def finish(self):
        with util.pushd(self.DIR_STAGING):
            print self.packagename()
            util.command(['dpkg-deb','-b',self.DIR_OUT,self.packagename()])
