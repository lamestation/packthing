import errno
import os
import platform
import shutil
import string
import subprocess
import sys
import tarfile
import zipfile
from contextlib import contextmanager


def get_platform():
    _platform = dict()

    _platform["system"] = platform.system().lower()

    machine = platform.machine().lower()
    if machine == "x86_64":
        machine = "amd64"
    _platform["machine"] = machine

    return _platform


def warning(*args):
    print("WARNING:" + " ".join(args))


def error(*objs):
    blocks = []
    for b in " ".join(objs).split("\n"):
        if len(blocks) > 0:
            blocks.append("       " + b)
        else:
            blocks.append(b)

    print("\nERROR:" + "\n".join(blocks))
    print()
    sys.exit(1)


def subtitle(text):
    line = (80 - (len(text) + 2)) // 2
    print("-" * line, text, "-" * (line + (len(text) % 2)))


def title(text):
    line = (80 - (len(text) + 2)) // 2
    print("=" * line, text.upper(), "=" * (line + (len(text) % 2)))


def headline(func):
    def wrapper(*args, **kwargs):
        title(func.__name__)
        res = func(*args, **kwargs)
        return res

    return wrapper


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)


def copy(src, dest, verbose=True, permissions=0o644):
    destfile = os.path.join(dest, os.path.basename(src))
    if verbose:
        print("Copy", src, "to dir", dest)
    mkdir(dest)
    shutil.copy(src, destfile)
    os.chmod(destfile, permissions)


def command(args, verbose=True, strict=True, stdinput=None):
    if verbose:
        print("-", " ".join(args))

    if not args:
        error("Attempting to run empty command.")

    try:
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except (OSError, WindowsError) as e:
        error("Command '" + args[0] + "' not found; exiting.")

    if stdinput is not None:
        stdinput = stdinput.encode()

    out, err = process.communicate(input=stdinput)
    out = out.decode()
    err = err.decode()
    if strict:
        if process.returncode:
            print(err)
            raise subprocess.CalledProcessError(process.returncode, args, err)
    return out, err


def command_in_dir(args, newdir, verbose=True, strict=True, stdinput=None):
    if verbose:
        print("DIR:", newdir)

    with pushd(newdir):
        out, err = command(args, verbose=verbose, strict=strict)
        return out, err


def table(path, version, url):
    return "%30s  %10s  %s" % (path, version, url)


def make(path, args):
    with pushd(path):
        args.insert(0, "make")
        for m in ["make", "mingw32-make"]:
            args[0] = m
            failed = 0

            try:
                subprocess.check_call(args)
            except OSError:
                failed = 1
            except subprocess.CalledProcessError as e:
                error("Failed to build project '" + path + "'")

            if not failed:
                return


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


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def tar_archive(name, files):
    shortname = os.path.basename(name)
    name += ".tgz"

    archive = tarfile.open(name=name, mode="w:gz")
    for f in files:
        archive.add(name=f, arcname=os.path.join(shortname, f), recursive=False)
    archive.close()


def zip_archive(name, files):
    shortname = os.path.basename(name)
    name += ".zip"

    archive = zipfile.ZipFile(name, "w")
    for f in files:
        archive.write(
            filename=f,
            arcname=os.path.join(shortname, f),
            compress_type=zipfile.ZIP_DEFLATED,
        )
    archive.close()


def from_scriptroot(filename):
    currentpath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(currentpath, filename)


def get_template_text(template):
    template = os.path.join("template", template)
    template = from_scriptroot(template)
    return open(template, "r").read()


def get_template(template):
    return string.Template(get_template_text(template))


# python-chroot-builder
# Copyright (C) 2012 Ji-hoon Kim
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------
def ldd(filenames):
    libs = []
    for x in filenames:
        p = subprocess.Popen(["ldd", x], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result = p.stdout.readlines()

        for x in result:
            s = x.split()
            s.pop(1)
            s.pop()
            if len(s) == 2:
                libs.append(s)
    return libs


# -----------------------------------------


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


def write(text, filename):
    f = open(filename, "w")
    f.seek(0)
    f.write(text)
    f.close()


def create(text, filename, executable=False):
    print("Create", filename)
    mkdir(os.path.dirname(filename))
    f = open(filename, "w")
    f.seek(0)
    f.write(text)
    f.close()
    if executable:
        os.chmod(filename, 0o755)
    else:
        os.chmod(filename, 0o644)


def root():
    if os.geteuid() != 0:
        error("This configuration requires root privileges!")


def cksum(files):
    print("cksum:")
    for f in files:
        try:
            out, err = command(["cksum", f], verbose=False)
        except subprocess.CalledProcessError as e:
            error("Failed to checksum file:", f)

        print("| " + out.replace("\n", ""))
