import os

from . import base
import util
import textwrap

import datetime
import time
from email import utils

REQUIRE = [ 'dpkg-deb',
            'dh_fixperms',
            'dpkg-shlibdeps',
            'dpkg-gencontrol',
            'fakeroot',
            'help2man',
            'dh_installmanpages',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'deb'
        self.EXT_BIN = ''
        self.EXT_LIB = 'so'

        self.DIR_DEBIAN = os.path.join(self.DIR_STAGING,'debian')
        self.DIR_DEBIAN2 = os.path.join(self.DIR_DEBIAN,self.NAME,'DEBIAN')
        self.DIR_OUT = os.path.join(self.DIR_DEBIAN,self.NAME)

        self.OUT['bin'] = os.path.join('usr','bin')
        self.OUT['lib'] = os.path.join('usr','lib')
        self.OUT['share'] = os.path.join('usr','share',self.NAME)

    def control(self):
        script = util.get_template(os.path.join('debian','control'))
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
        script = util.get_template('debian/changelog')
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


    def make(self):
        super(Packager,self).make()
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.copy()
        self.manpages()

        with util.pushd(self.DIR_STAGING):
            util.write(self.control(),  os.path.join(self.DIR_DEBIAN,'control'))
            util.write(self.changelog(),os.path.join(self.DIR_DEBIAN,'changelog'))
            util.write('9',os.path.join(self.DIR_DEBIAN,'compat'))
            util.command(['dpkg-shlibdeps','/usr/bin/propelleride'])
            util.command(['dh_installmanpages'])
            util.command(['fakeroot','dpkg-gencontrol','-v'+self.VERSION,'-P'+self.DIR_OUT])
            util.command(['dpkg-deb','-b',self.DIR_OUT,'.'])
