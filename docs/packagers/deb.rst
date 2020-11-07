Debian Packager
===============

.. contents::
    :local:

System Requirements
-------------------

- ``debhelper``
- ``dpkg-dev``
- ``fakeroot``
- ``help2man``
- ``imagemagick``
- ``lintian``

On Ubuntu::

    sudo apt-get install -y fakeroot help2man lintian debhelper dpkg-dev imagemagick

Configuration
-------------

Required
''''''''

**target.deb.categories**
    freedesktop.org `Categories
    <https://specifications.freedesktop.org/menu-spec/latest/apa.html>`_.

**target.deb.section**
    Debian Menu `Section
    <https://www.debian.org/doc/packaging-manuals/menu.html/ch3.html#s3.5>`_
    field.

Optional
''''''''

**target.deb.depends**
    Add explicit package dependencies.

**target.deb.help2man**
    Generate man pages for listed commands with `help2man
    <https://www.gnu.org/software/help2man/>`_. Requires commands to support a
    ``--version`` flag.

Example
'''''''

.. code-block:: yaml

    target: 
        deb: 
            depends: libftdi1
            categories: Development;IDE
            section: Applications/Editors
            help2man:
                - propelleride
                - propman
                - openspin
