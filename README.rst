.. image:: gfx/packthing-logo.png

packthing is a high-level integration tool that makes packaging and
distributing your application simple.

- **One project, many formats** - quickly produce a versioned distribution for any project type that's supported.
- **Configuration is simple** - prepare your project for deployment in just a few steps.
- **Not an expert? Not a problem** - save yourself hundreds of hours learning operating system details; get it done and get on with your life.

.. image:: gfx/packthing-tree.png

Configuration with ``packthing.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

packthing configuration may be saved permanently inside a packthing.yml
file. Run packthing in the same directory as the file to build the project.

.. code:: yaml

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

