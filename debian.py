#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import argparse
from repo import Repo
import textwrap

def get_template():
    return string.Template("""\
Source: ${application}
Maintainer: ${maintainer} <${email}>
Package: ${application}
Priority: optional
Version: ${VERSION}
Architecture: ${CPU}
Depends: ${depends}
Description: ${tagline}
 ${description}
""")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='iss.py - generate debian build files from repo.xml')
    parser.add_argument('project', nargs=1, metavar="PROJECT", help="repo.xml file to parse")
    parser.add_argument('-o','--out', nargs=1, metavar="OUTPUT", help="Output control file")
    parser.add_argument('-s','--show', action='store_true', help="Dump any output to stdout")
    parser.add_argument('-a','--arch', nargs=1, metavar="ARCH", help="CPU type (i386, amd64, armhf...)")
    parser.add_argument('-d','--deps', action='store_true', help="Calculate dependencies")
    args = parser.parse_args()

    repo = Repo(args.project[0])

    info = repo.info()
    script = get_template()

    if args.deps:
        depends = "${shlibs:Depends}, zlib1g, libftdi1"
    else:
        depends = ""

    rendering = script.substitute(
                    application = info.attrib['application'].lower(),
                    maintainer  = info.attrib['maintainer'],
                    email       = info.attrib['email'],
                    VERSION     = repo.version(),
                    CPU         = args.arch[0],
                    tagline     = info.attrib['tagline'],
                    description = textwrap.fill(info.attrib['description'], 
                            60, subsequent_indent = ' '),
                    depends     = depends,
                )

    if not args.out and not args.show:
        print "Command will not produce any output without -o or -s"

    if args.out:
        f = open(args.out[0], 'w')
        f.write(rendering)
        f.close()

    if args.show:
        print rendering
