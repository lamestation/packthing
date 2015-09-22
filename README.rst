packthing - write once, package everywhere
============================================

packthing is a high-level integration tool that makes packaging and
distributing your application dirt simple.

- **One project, many formats** - packthing allows you to quickly produce
a versioned distribution for any project type that it supports.
- **Configuration is simple** -  set up your project by following a few
instructions; no headache required.
- **Not an expert? Not a problem** - packaging is a complex problem that
has to be solved over and over again. packthing saves you from having to
become an OS guru on every operating system your application runs on.

Configuration with ``packthing.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

packthing configuration may be saved permanently inside a packthing.json
file. Run packthing in the same directory as the file to build the project.

.. code:: json

    org: "bazzbar industries"
    name: "Frobnicator"
    package: "frob"
    url: "http://frobby.io"
    
    repo: 
      - 
        path: "frobtool"
        url: "https://github.com/frob/frobtool.git"
        type: "qmake"
        master: true
        icon: "icons/propellerhat.png"
      - 
        path: "frobdocs"
        url: "https://github.com/frob/frob-docs.git"
        type: "dir"

