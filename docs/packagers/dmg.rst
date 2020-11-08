Apple Disk Image (DMG) Packager
===============================

.. contents::
    :local:

System Requirements
-------------------

- ``dmgbuild``
- ``iconutil``
- ``macdeployqt``
- ``sips``

Configuration
-------------

**target.dmg.category**
    `Application Category
    <https://developer.apple.com/documentation/bundleresources/information_property_list/lsapplicationcategorytype>`_.

**target.dmg.background**
    DMG background image.

**target.dmg.bundle**
    App bundle name (``.app``).

Example
'''''''

.. code-block:: yaml

    target:
      dmg:
        category: public.app-category.developer-tools
        background: icons/mac-dmg.png
        bundle: propelleride
