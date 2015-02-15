from __future__ import print_function
import os, sys
import subprocess
import logging
from contextlib import contextmanager

def warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)

def error(*objs):
    print("ERROR:", *objs, file=sys.stderr)

@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)

def command(args):
    logging.debug(["util.command", args, os.getcwd()])
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    logging.debug(["util.command", args, out, err])
    return out, err

def command_in_dir(args, newdir):
    with pushd(newdir):
        out, err = command(args)
        return out, err

def table(path, version, url):
    return "%30s  %10s  %s" % (path, version, url)

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def archive(name, files):
    import tarfile
    shortname = os.path.basename(name)

    tar = tarfile.open(name=name, mode='w:gz')
    for f in files:
        tar.add(name=f, arcname=os.path.join(os.path.splitext(shortname)[0],f), recursive=False)
    tar.close()

