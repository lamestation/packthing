Free Pascal Compiler (FPC) Builder
==================================

.. contents::
    :local:

Configuration
-------------

**repos.<repo>.url**
    Repository to check out.

**repos.<repo>.tag**
    Repository branch/tag to check out.

**repos.<repo>.builder**
    Set to ``fpc``.

**repos.<repo>.root**
    Root directory of FPC project.

Example
'''''''

.. code-block:: yaml

    repos:
      propbasic:
        url: https://github.com/parallaxinc/PropBasic.git
        tag: 1.44.2
        builder: fpc
        root: src
