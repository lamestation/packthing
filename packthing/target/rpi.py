from . import deb

class Packager(deb.Packager):

    def __init__(self, info, version, files):
        super(Packager,self).__init__(info, version, files)

        self.CPU = 'armhf'
