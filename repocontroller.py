import util, sys, os
from lxml import etree

class RepoController:
    def __init__(self, repofile, dtd='repo.dtd'):
        self.name = repofile

        if not os.path.exists(self.name) or not os.path.isfile(self.name):
            raise IOError("File "+self.name+" does not exist")

        self.root = etree.parse(self.name).getroot()
        self.validate(util.from_scriptroot(dtd))

        self.gfx  = self.root.find('gfx').attrib['path']
        self.info = self.root.find('info')
        self.master = self.root.find('master').attrib['path']
        self.target = self.root.find('target')
        self.build_tree()

    def build_tree(self):
        self.repo = []
        for child in self.root.findall('repo'):
            r = {}
            r['path'] = child.attrib['path']
            r['url'] = child.attrib['url']
            r['type'] = child.attrib['type']

            if 'branch' in child.attrib:
                r['ref'] = child.attrib['branch']
            elif 'tag' in child.attrib:
                r['ref'] = child.attrib['tag']

            self.repo.append(r)

        return self.repo

    def validate(self, dtdfile):
        dtd = etree.DTD(dtdfile)

        if not dtd.validate(self.root):
            print dtd.error_log.filter_from_errors()[0]
            sys.exit(1)

    def print_info(self):
        print
        print "%30s  %s" % ("Master project:",self.master)
        print "%30s  %s" % ("Graphics path:",self.gfx)
        print

