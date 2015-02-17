import os

import base
import util
import textwrap

REQUIRE = [ 'dpkg-deb',
            'dh_fixperms',
            'dh_shlibdeps',
            'dh_gencontrol',
            'fakeroot',
            ]

class Packager(base.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.EXT = 'deb'

        self.DIR_DEBIAN = os.path.join(self.DIR_STAGING,'debian')
        self.DIR_DEBIAN2 = os.path.join(self.DIR_DEBIAN,'tmp','DEBIAN')
        self.DIR_MAN = os.path.join(self.DIR_OUT,'share','man','man1')

        self.DIR_OUT = os.path.join(self.DIR_DEBIAN,'tmp')
        self.OUT['bin'] = os.path.join('usr','bin')

    def control(self):
        script = util.get_template('debian/control')
        depends = "${shlibs:Depends}"
        rendering = script.substitute(
                        application = self.NAME,
                        maintainer  = self.info.attrib['maintainer'],
                        email       = self.info.attrib['email'],
                        VERSION     = self.VERSION,
                        CPU         = self.CPU,
                        tagline     = self.info.attrib['tagline'],
                        description = textwrap.fill(self.info.attrib['description'], 
                                60, subsequent_indent = ' '),
                        depends     = depends,
                    )
        return rendering

    def changelog(self):
        script = util.get_template('debian/changelog')
        import datetime
        import time
        from email import utils
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

#    def manpages(self):

    def make(self):
        super(Packager,self).make()
        util.mkdir(self.DIR_DEBIAN)
        util.mkdir(self.DIR_DEBIAN2)
        self.copy()

        with util.pushd(self.DIR_STAGING):
            util.write(self.control(),  os.path.join(self.DIR_DEBIAN,'control'))
            util.write(self.changelog(),os.path.join(self.DIR_DEBIAN,'changelog'))
            util.write('9',os.path.join(self.DIR_DEBIAN,'compat'))
            util.command(['dpkg-shlibdeps','/usr/bin/propelleride'])
            util.command(['fakeroot','dpkg-gencontrol','-v'+self.VERSION])
            util.command(['dpkg-deb','-b','debian/tmp','.'])
