from setuptools import find_packages
from setuptools import setup

from packthing import __version__

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="packthing",
    version=__version__,
    author="LameStation",
    author_email="contact@lamestation.com",
    description="Write once, package everywhere",
    long_description=long_description,
    license="GPLv3",
    url="https://github.com/lamestation/packthing",
    keywords="packaging qt qmake building distribution",
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    entry_points={"console_scripts": ["packthing = packthing.main:console",],},
    install_requires=["pyyaml", "dmgbuild; sys_platform == 'darwin'",],
    test_suite="test",
    classifiers=[
        "Environment :: Console",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: Utilities",
    ],
)
