import imp, sys

import util
import pkgutil
import logging

def get_modulelist(packagename):
    package_info = imp.find_module(packagename)
    package = imp.load_module(packagename,*package_info)

    packagelist = []
    for p in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        packagelist.append(p[1].split('.')[1])

    return packagelist

def get_module(parentname, modulename):
    logging.debug("importer.get_module('"+parentname+"','"+modulename+"')")
    try:
        parent_info = imp.find_module(parentname)
        parent = imp.load_module(parentname,*parent_info)
        f, filename, description = imp.find_module(modulename, parent.__path__)
    except ImportError, e:
        raise ImportError(parentname.capitalize()+" '"+modulename+"' does not exist")

    return imp.load_module(parentname+'.'+modulename, f, filename, description)

def require(module):
    pass
