# packman

## Why another packaging thing?

One of the most frustrating aspects of starting a new project is figuring out how to package it for release. No matter what shiny framework you have, once you leave the safety of generating a plain old binary, all bets are off and you're left to figure out how to get said binary to your customers.

What's more, it's a problem that rarely needs to be solved more than once, and so many of the resources on the subject are few and far between, which makes it all the more frustrating.

The goal of Packman is to create a language-agnostic, high-level integration tool that **does the work for you**, making your application fit for human consumption. It intends to support interoperability between:

Famously described as a *glorified convenience wrapper*, **packman** is here to make your life easy.

* Multiple version control systems
* Many output formats (windows installer, mac bundle, pkg, tar, debian, rpm, apk, and so on and so forth).
* Many build systems

## It's a super project!

Say someone wrote an awesome Python app with Mercurial for version control, someone else wrote a cool C++ app using bjam, and yet another person wrote a native C app using scons and SVN. You would have quite a challenge on your hands to try to integrate these under one hood to release them together; this is the use case that packman attempts to address.

Packman projects use version control, but exist outside of it, forming a *super repository* of smaller projects, defined by an XML file.

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

## Future

At present, the focus has been on supporting Qt applications, but there are other multiply cross-platform environments where a tool such as this would be useful. Possible future targets include:

* scons (C++)
* distutils (Python)
* CMake

Packman does not attempt to support every possible configurations all of the time. Rather, it's goal is to do a good enough job for more common use cases first, with the possibility of finer-grained controls in the future.

So use packman because you want to get the thing out the door. **Now, please!**

**NOTE: Packman is in the early stages of development. Currently only triplets including Git and Qt are supported.**
