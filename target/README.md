# Target modules

This directory contains implementations for packaging the build output
for different platforms.

## Defining new targets

The first step to creating your own target is redefining
`self.EXT` and `self.DIR_OUT`. `self.EXT` is the name
of the extension the file output will have. `self.DIR_OUT`
is the root directory of the final target package.

```
self.EXT = 'deb'
self.DIR_OUT = os.path.join(self.DIR_DEBIAN,'tmp')
```

Next, you need to populate the `self.OUT` dictionary.
There are several pre-defined locations to define; these
are: `'bin'`, `'lib'`, and `'share'`. On a UNIX, these
might be defined as:

```
self.OUT['bin'] = os.path.join('usr','bin')
self.OUT['lib'] = os.path.join('usr','lib')
self.OUT['share'] = os.path.join('usr','share','yourproject')
```

### make()

This function is called by `packman` to 

### The icons() function

This function will define how to handle/populate icons for different platforms.

*This section not yet complete*
