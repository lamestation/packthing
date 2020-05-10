import importlib
import inspect
import pkgutil
import sys

from . import util

_platform = util.get_platform()


def get_modulelist(package):
    packagelist = []

    for p in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        packagelist.append(p[1])

    #    for p in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
    #        packagelist.append(p[1])

    for i in range(len(packagelist)):
        packagelist[i] = packagelist[i].split(".")[-1]

    packagelist = [x for x in packagelist if not x.startswith("_")]

    return packagelist


def get_module(parent, modulename):
    return importlib.import_module(parent.__name__ + "." + modulename)


def list_module_hierarchy(module):
    clsmembers = inspect.getmembers(module, inspect.isclass)
    return inspect.getmro(clsmembers[0][1])


def build_module_hierarchy(module):
    clsmembers = inspect.getmembers(module, inspect.isclass)
    parenttree = inspect.getmro(clsmembers[0][1])

    modulelist = []
    for p in parenttree:
        modulelist.append(importlib.import_module(p.__module__))
    modulelist.append(module)

    return modulelist


def require(module):
    if _platform["system"] == "windows":  # REQUIRE DOESN'T WORK ON WINDOWS
        return

    for m in build_module_hierarchy(module):
        try:
            m.REQUIRE
        except AttributeError as e:
            continue

        for r in m.REQUIRE:
            found = util.which(r)
            if not found:
                util.error("Required program '" + r + "' not available")


def required_keys(module):
    keylist = []
    for m in build_module_hierarchy(module):
        try:
            keylist.extend(m.KEYS)
        except AttributeError as e:
            continue
    return list(set(keylist))
