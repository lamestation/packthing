packthing - *write once, package everywhere*
============================================

Why another packaging thing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the most frustrating aspects of starting a new project is
figuring out how to package it for release. No matter what shiny
framework you have, once you leave the safety of generating a plain old
binary, all bets are off and you're left to figure out how to get said
binary to your customers.

What's more, it's a problem that rarely needs to be solved more than
once, and so many of the resources on the subject are few and far
between, which makes it all the more frustrating.

The goal of Packthing is to create a language-agnostic, high-level
integration tool that **does the work for you**, making your application
fit for human consumption. It intends to support interoperability
between:

-  Multiple version control systems
-  Many output formats (windows installer, mac bundle, pkg, tar, debian,
   rpm, apk, and so on and so forth).
-  Many build systems

Famously described as a *glorified convenience wrapper*, **packthing**
is here to make your life easy.

It's a super project!
~~~~~~~~~~~~~~~~~~~~~

Multiple version control systems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Say someone wrote an awesome Python app with Mercurial for version
control, someone else wrote a cool C++ app using bjam, and yet another
person wrote a native C app using scons and SVN. Packthing let's you
ignore for a moment that they all came from different places.

Packthing projects use version control, but exist outside of it, forming
a super repository of smaller projects, defined by a JSON file.

.. code:: json

    {
        "info": {
            "org": "bazzbar industries",
            "name": "Frobnicator",
            "package": "frob",
            "url": "http://frobby.io"
        },
        "repo": [
            {
                "path": "frobtool",
                "url": "https://github.com/frob/frobtool.git",
                "type": "qmake",
                "master": true,
                "icon": "icons/propellerhat.png"
            },
            {
                "path": "frobdocs",
                "url": "https://github.com/frob/frob-docs.git",
                "type": "dir"
            }
        ]
    }

Packthing then fetchs the dependencies and auto-populates all the needed
information to package the project for a variety of formats.

Multiple package formats
^^^^^^^^^^^^^^^^^^^^^^^^

Build your application into a windows installer, mac bundle, pkg, tar,
Debian RPM, APK, and many more. ``packthing`` provides a generic
abstraction between the build system and the packaging system, so you
can all but forget what the final project layout actually looks like.

Future
------

At present, the focus has been on supporting Qt applications, but there
are other multiply cross-platform environments where a tool such as this
would be useful. Possible future targets include:

-  scons (C++)
-  distutils (Python)
-  CMake

Packthing does not attempt to support every possible configurations all
of the time. Rather, it's goal is to do a good enough job for more
common use cases first, with the possibility of finer-grained controls
in the future.

So use packthing because you want to get the thing out the door. **Now,
please!**

**NOTE: Packthing is in the early stages of development. Currently only
triplets including Git and Qt are supported.**

Usage
-----

Setting up your project to use ``packthing``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, write up a config file for your project, and save as
``packthing.json``. This file should be checked in to your project but
does not depend on your project. You should be able to download the
config file separately to use ``packthing``.

This config will include a single project repository. ``packthing`` is
useful for both single- and multi-repository projects!

Building a package
~~~~~~~~~~~~~~~~~~

Type ``packthing -h`` or ``packthing --help`` to get a nice pretty help
output.

::

    usage: packthing [-h] [-r REPO] [-c DIR] [-l LEVEL] [-a NAME] [--list-src]
                   [--list-build] [-j JOBS] [--refresh]
                   [TARGET]

    packthing - make working with your project more complicated

    ...

