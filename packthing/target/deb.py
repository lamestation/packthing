import os
import shutil
from .. import util
import textwrap

import datetime
import time
from email import utils

from . import base

REQUIRE = [ 'dpkg-deb',
            'dh_fixperms',
            'dpkg-shlibdeps',
            'dpkg-gencontrol',
            'help2man',
            'dh_installmanpages',
            'convert',
            ]

if os.geteuid() != 0:
        exit("Debian packaging requires root privileges; exiting!")

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
        nowdt = datetime.datetime.now()
        nowtuple = nowdt.timetuple()
        nowtimestamp = time.mktime(nowtuple)
        date = utils.formatdate(nowtimestamp)

        d = {
            'application' : self.info['package'],
            'maintainer'  : self.info['maintainer'],
            'email'       : self.info['email'],
            'VERSION'     : self.VERSION,
            'datetime'    : date,  
        }
        return util.get_template('deb/changelog').substitute(d)

    def manpages(self):
        for f in self.files['bin']:
            OUTDIR = os.path.join(self.DIR_OUT,self.OUT['bin'])
            g = os.path.basename(f)

            util.command(['help2man','--no-info',
                    os.path.join(OUTDIR,g),
                    '-o',os.path.join(self.DIR_DEBIAN,g+'.1')],strict=False)

    def menu(self):
        d = {
            'NAME'        : self.info['name'],
            'APPLICATION' : self.info['package'],
            'DESCRIPTION' : self.info['description'],
            'SECTION'     : self.info['section'],
        }
        return util.get_template('deb/menu').substitute(d)

    def desktop(self):
        d = {
            'NAME'        : self.info['name'],
            'APPLICATION' : self.info['package'],
            'DESCRIPTION' : self.info['description'],
            'TAGLINE'     : self.info['tagline'],
            'CATEGORIES'  : self.info['categories'],
        }
        return util.get_template('deb/desktop').substitute(d)

    def icon(self,icon,target):
        if os.path.exists(icon):
            util.mkdir(self.DIR_PIXMAPS)
            util.command(['convert',icon,'-resize','32x32',
                    os.path.join(self.DIR_PIXMAPS,target+'.xpm')])

    def make(self):
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.install()
#        self.manpages()

        with util.pushd(self.DIR_STAGING):
            util.create(self.control(),  os.path.join(self.DIR_DEBIAN,'control'))
            util.create(self.changelog(),os.path.join(self.DIR_DEBIAN,'changelog'))
            util.create('9',             os.path.join(self.DIR_DEBIAN,'compat'))
            util.create(self.postinst(), os.path.join(self.DIR_DEBIAN,'postinst'))

            util.create(self.menu(),    os.path.join(self.DIR_MENU,self.info['package']))
            util.create(self.desktop(), os.path.join(self.DIR_DESKTOP,self.info['package']+'.desktop'))

            deps = ['dpkg-shlibdeps','--ignore-missing-info']
            for f in self.files['bin']:
                OUTDIR = os.path.join(self.DIR_OUT,self.OUT['bin'])
                outf = os.path.join(OUTDIR,f)
                deps.append(outf)

            util.command(deps)

            util.command(['dh_installmanpages'])
            util.command(['dpkg-gencontrol','-v'+self.VERSION,'-P'+self.DIR_OUT])
            util.command(['dh_fixperms'])

    def finish(self):
        super(Packager,self).finish()
        with util.pushd(self.DIR_STAGING):
            util.command(['dpkg-deb','-b',self.DIR_OUT,self.packagename()+'.deb'])
