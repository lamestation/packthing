from __future__ import print_function
import sys
import util
import pkgutil, importlib
import inspect
import platform

def get_modulelist(package):
    packagelist = []
    for p in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        packagelist.append(p[1])

    for i in range(len(packagelist)):
        packagelist[i] = packagelist[i].split('.')[-1]

    return packagelist

def get_module(parent, modulename):
    try:
        module = importlib.import_module(parent.__name__+'.'+modulename)
    except ImportError as e:
        raise ImportError(parent.__name__+" '"+modulename+"' does not exist")

    return module

def require(module):
    if platform.system() == 'Windows': # REQUIRE DOESN'T WORK ON WINDOWS
        return

    clsmembers = inspect.getmembers(module, inspect.isclass)
    parenttree = list(clsmembers[0][1].__bases__)

    modulelist = []
    for p in parenttree:
        modulelist.append(importlib.import_module(p.__module__))
    modulelist.append(module)

    for m in modulelist:
        try:
            m.REQUIRE
        except AttributeError as e:
            continue

        for r in m.REQUIRE:
            found = util.which(r)
            if not found:
                util.error("Required program '"+r+"' not available")

#            print("Using",found)
