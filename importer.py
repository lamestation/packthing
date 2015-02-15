import imp, sys

import util

def get_module(parentname, modulename):
    try:
        parent_info = imp.find_module(parentname)
        parent = imp.load_module(parentname,*parent_info)
        f, filename, description = imp.find_module(modulename, parent.__path__)
    except ImportError, e:
        raise ImportError(parentname.capitalize()+" '"+modulename+"' does not exist")

    return imp.load_module(parentname, f, filename, description)

def require(module):
    try:
        for r in module.REQUIRE:
            if util.which(r) == None:
                raise OSError("Executable '"+r+"' not found; required by '"+module.__name__+"'")
    except AttributeError: # Don't require external dependencies
        pass

