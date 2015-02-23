import sys
import util
import pkgutil, importlib
import logging

@util.log
def get_modulelist(package):
    packagelist = []
    for p in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        packagelist.append(p[1])

    for i in range(len(packagelist)):
        packagelist[i] = packagelist[i].split('.')[-1]

    return packagelist

@util.log
def get_module(parent, modulename):
    try:
        module = importlib.import_module(parent.__name__+'.'+modulename)
    except ImportError, e:
        raise ImportError(parent.__name__+" '"+modulename+"' does not exist")

    return module

@util.log
def require(module):
    pass
