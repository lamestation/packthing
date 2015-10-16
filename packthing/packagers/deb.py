# -*- coding: utf-8 -*-

import os, sys
import shutil
import textwrap

import datetime
import time
from email import utils

import packthing.util as util
import packthing.icons as icons

REQUIRE = [ 'dpkg-deb',
            'dh_fixperms',
            'dpkg-shlibdeps',
            'dpkg-gencontrol',
            'dh_installmanpages',
            'convert',
            ]

KEYS = [
        'depends',
        'section',
        'categories',
        ]

util.root()

from . import _linux

class Packager(_linux.Packager):

    def __init__(self, info, files):
        super(Packager,self).__init__(info, files)

        self.PREFIX = 'usr'
        self.EXT = 'deb'

        self.DIR_DEBIAN  = os.path.join(self.DIR_STAGING,'debian')
        self.DIR_DEBIAN2 = os.path.join(self.DIR_DEBIAN,self.info['package'],'DEBIAN')
        self.DIR_OUT     = os.path.join(self.DIR_DEBIAN,self.info['package'])

        self.OUT['bin']   = os.path.join('usr','bin')
        self.OUT['lib']   = os.path.join('usr','lib')
        self.OUT['share'] = os.path.join('usr','share',self.info['package'])

        self.DIR_MENU    = os.path.join(self.DIR_OUT,'usr','share','menu')
        self.DIR_DESKTOP = os.path.join(self.DIR_OUT,'usr','share','applications')
        self.DIR_PIXMAPS = os.path.join(self.DIR_OUT,'usr','share','pixmaps')

    def postinst(self):
        return util.get_template('deb/postinst').substitute(dict())
        

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
        now = datetime.datetime.now().timetuple()
        date = utils.formatdate(time.mktime(now))

        d = {
            'application' : self.info['package'],
            'maintainer'  : self.info['maintainer'],
            'email'       : self.info['email'],
            'VERSION'     : self.VERSION,
            'datetime'    : date,  
        }
        return util.get_template('deb/changelog').substitute(d)

    def help2man(self):
        if not util.which('help2man'):
            util.warning("help2man not found; skipping man page generation")
            return

        OUTDIR = os.path.join(self.DIR_OUT,self.OUT['bin'])
        for f in self.files['bin']:
            g = os.path.basename(f)

            if g in self.info['help2man']:
                util.command(['help2man',
                        '--no-info',
                        '--source='+self.info['package'],
                        os.path.join(OUTDIR,g),
                        '-o',os.path.join(self.DIR_DEBIAN,g+'.1')],strict=False)

    def menu(self, filename, config):
        d = {
            'NAME'        : config['name'],
            'PACKAGE'     : filename,
            'DESCRIPTION' : self.info['description'],
            'SECTION'     : self.info['section'],
            'FILENAME'    : filename,
            'ICON'        : filename,
        }
        return util.get_template('deb/menu').substitute(d)

    def desktop(self, filename, config):
        d = {
            'NAME'        : config['name'],
            'PACKAGE'     : filename,
            'DESCRIPTION' : self.info['description'],
            'TAGLINE'     : self.info['tagline'],
            'CATEGORIES'  : self.info['categories'],
            'FILENAME'    : filename,
            'ICON'        : filename,
        }
        return util.get_template('deb/desktop').substitute(d)

    def icon(self,icon,target):
        icons.imagemagick(icon, os.path.join(self.DIR_PIXMAPS,target), 32, 'xpm')

    def make(self):
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.install_files()
        self.help2man()

        with util.pushd(self.DIR_STAGING):
            util.create(self.control(),  os.path.join(self.DIR_DEBIAN,'control'))
            util.create(self.changelog(),os.path.join(self.DIR_DEBIAN,'changelog'))
            util.create('9',             os.path.join(self.DIR_DEBIAN,'compat'))
            util.create(self.postinst(), os.path.join(self.DIR_DEBIAN,'postinst'))

            for i in self.info['files'].keys():
                util.create(self.menu(i, self.info['files'][i]),    os.path.join(self.DIR_MENU,i))
                util.create(self.desktop(i, self.info['files'][i]), os.path.join(self.DIR_DESKTOP,i+'.desktop'))

    def finish(self):
        with util.pushd(self.DIR_STAGING):
            deps = ['dpkg-shlibdeps','--ignore-missing-info']
            for f in self.files['bin']:
                OUTDIR = os.path.join(self.DIR_OUT,self.OUT['bin'])
                outf = os.path.join(OUTDIR,f)
                deps.append(outf)

            util.command(deps)
            util.command(['dh_installmanpages'])
            util.command(['dh_installmenu'])

            try:
                util.command(['dpkg-gencontrol','-v'+self.VERSION,'-P'+self.DIR_OUT])
            except:
                sys.exit(1)

            util.command(['dh_fixperms'])
            util.command(['dpkg-deb','-b',self.DIR_OUT,self.packagename()+'.deb'])
        super(Packager,self).finish()

    def install(self):
        with util.pushd(self.DIR_STAGING):
            try:
                util.command(['dpkg','-i',self.packagename()+'.deb'])
            except:
                util.error("Installation failed! Oh, well.")