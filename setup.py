import sys, os
from setuptools import setup
import platform

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name = "packthing",
        version = "0.1",
        author = "LameStation",
        author_email = "contact@lamestation.com",
        description = "Write once, package everywhere",
        license = "GPLv3",
        url = "https://github.com/lamestation/packthing",
        keywords = "packaging qt qmake building distribution",
        long_description = read('README.md'),
        packages=['packthing', 'test'],
        entry_points={
            'console_scripts': [
                'packthing = packthing.main:console',
                ],
            },
        test_suite="test",
        classifiers=[
            "Environment :: Console",
            "Development Status :: 2 - Pre-Alpha",
            "Topic :: Utilities",
            "License :: OSI Approved :: BSD License",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Topic :: System :: Archiving :: Packaging",
            "Environment :: X11 Applications :: Qt",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: C++",
            "Topic :: Software Development :: Code Generators",
            ]
        )
