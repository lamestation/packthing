# packman - *write once, package everywhere*




## About

### Why another packaging thing?

One of the most frustrating aspects of starting a new project is figuring out how to package it for release. No matter what shiny framework you have, once you leave the safety of generating a plain old binary, all bets are off and you're left to figure out how to get said binary to your customers.

What's more, it's a problem that rarely needs to be solved more than once, and so many of the resources on the subject are few and far between, which makes it all the more frustrating.

The goal of Packman is to create a language-agnostic, high-level integration tool that **does the work for you**, making your application fit for human consumption. It intends to support interoperability between:

* Multiple version control systems
* Many output formats (windows installer, mac bundle, pkg, tar, debian, rpm, apk, and so on and so forth).
* Many build systems

Famously described as a *glorified convenience wrapper*, **packman** is here to make your life easy.

### It's a super project!

#### Multiple version control systems

Say someone wrote an awesome Python app with Mercurial for version control, someone else wrote a cool C++ app using bjam, and yet another person wrote a native C app using scons and SVN. Packman let's you ignore for a moment that they all came from different places.

Packman projects use version control, but exist outside of it, forming a super repository of smaller projects, defined by an XML file.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
  <info
    organization="..."
    application="..."
    ...
    ...
    />

  <repo path="src/openspin/repo"    url="https://github.com/bweir/OpenSpin.git" />
  <repo path="src/p1load/repo"      url="https://github.com/dbetz/p1load.git" />
</project>
```
Packman then fetchs the dependencies and auto-populates all the needed information to package the project for a variety of formats.

#### Multiple package formats

Build your application into a windows installer, mac bundle, pkg, tar, Debian RPM, APK, and many more. `packman` provides a generic abstraction between the build system and the packaging system, so you can all but forget what the final project layout actually looks like.

## Future

At present, the focus has been on supporting Qt applications, but there are other multiply cross-platform environments where a tool such as this would be useful. Possible future targets include:

* scons (C++)
* distutils (Python)
* CMake

Packman does not attempt to support every possible configurations all of the time. Rather, it's goal is to do a good enough job for more common use cases first, with the possibility of finer-grained controls in the future.

So use packman because you want to get the thing out the door. **Now, please!**

**NOTE: Packman is in the early stages of development. Currently only triplets including Git and Qt are supported.**

## Usage

### Setting up your project to use `packman`

First, write up a config file for your project, and save as `repo.xml` (or whatever you feel like). This file should be checked in to your project but does not depend on your project. You should be able to download the config file separately to use `packman`.

This config will include a single project repository. `packman` is useful for both single- and multi-repository projects!
```xml
<project>
  <info
    organization="CompanyX"
    application="Project"
    url="http://www.companyx.com"
    maintainer="This Guy"
    email="info@companyx.com"
    copyright="2014-2015"
    license="GPLv3"
    tagline="An awesome project"
    description="A very awesome project that can't be described in so few words, this project is epic."
    />

  <gfx      path="gfx" />
  <master   path="src/propelleride" />

  <repo
    type="qt"
    path="packman"
    url="https://github.com/lamestation/packman.git"
    branch="master"
    />
```
### Building a package

Type `packman -h` or `packman --help` to get a nice pretty help output.

```
usage: packman [-h] [-r REPO] [-c DIR] [-l LEVEL] [-a NAME] [--list-src]
               [--list-build] [-j JOBS] [--refresh]
               [TARGET]

packman - make working with your project more complicated

positional arguments:
  TARGET                Target platform to build (deb, mac, rpi, win)

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  Project repository config file (default: packman.xml)
  -c DIR                Change to DIR before running
  -l LEVEL, --log LEVEL
                        Log level of debug output (DEBUG, INFO, WARNING,
                        ERROR, CRITICAL)
  -a NAME, --archive NAME
                        Create tar archive from super-repository
  --list-src            List all files in super-repository
  --list-build          List all files to be included in package
  -j JOBS, --jobs JOBS  Number of jobs to pass to child builds
  --refresh             Force update of all checkouts
```
