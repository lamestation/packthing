from __future__ import print_function
import os, sys
import subprocess
import logging
from contextlib import contextmanager
import string
import errno
import tarfile

def warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)

def error(*objs):
    print("ERROR:", *objs, file=sys.stderr)

def headline(func):
    def wrapper(*args, **kwargs):
        line = (80-(len(func.__name__)+2))/2
        print("-"*line,func.__name__.upper(),"-"*(line+(len(func.__name__) % 2)))
        res = func(*args, **kwargs)
        return res
    return wrapper

def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        logging.info(__name__+'.'+func.__name__+str(args)+str(kwargs))
        return res
    return wrapper

@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)

@log
def command(args,strict=True,stdinput=None):
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(input=stdinput)
    if strict:
        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, args, err)
    return out, err

@log
def command_in_dir(args, newdir, strict=True):
    with pushd(newdir):
        out, err = command(args,strict=strict)
        return out, err

@log
def table(path, version, url):
    return "%30s  %10s  %s" % (path, version, url)

@log
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

@log
def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

@log
def archive(name, files):
    shortname = os.path.basename(name)

    tar = tarfile.open(name=name, mode='w:gz')
    for f in files:
        tar.add(name=f, arcname=os.path.join(os.path.splitext(shortname)[0],f), recursive=False)
    tar.close()

@log
def from_scriptroot(filename):
    currentpath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(currentpath,filename)

@log
def get_template(template):
    template = os.path.join('template',template)
    template = from_scriptroot(template)
    return string.Template(open(template,'r').read())



#python-chroot-builder
#Copyright (C) 2012 Ji-hoon Kim
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------
@log
def ldd(filenames):
    libs = [] 
    for x in filenames:
        p = subprocess.Popen(['ldd', x], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        result = p.stdout.readlines()

        for x in result:
            s = x.split()
            s.pop(1)
            s.pop()
            if len(s) == 2:
                libs.append(s)
	return libs
#-----------------------------------------

@log
def extract_libs(files, libs):
    resultlibs = []
    for f in files:
        for l in ldd([which(f)]):
            for lib in libs:
                if l[0].find(lib) == -1:
                    pass
                else:
                    resultlibs.append(l)
    return sorted(list(set(tuple(lib) for lib in resultlibs)))

@log
def write(text, filename):
    f = open(filename, 'w')
    f.seek(0)
    f.write(text)
    f.close()

@log
def create(text, filename):
    mkdir(os.path.dirname(filename))
    f = open(filename, 'w')
    f.seek(0)
    f.write(text)
    f.close()
