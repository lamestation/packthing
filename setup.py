from setuptools import setup, find_packages

with open('README.rst') as f:
        long_description = f.read()

setup(
        name = "packthing",
        version = '0.2.1',
        author = "LameStation",
        author_email = "contact@lamestation.com",
        description = "Write once, package everywhere",
        long_description = long_description,
        license = "GPLv3",
        url = "https://github.com/lamestation/packthing",
        keywords = "packaging qt qmake building distribution",
        packages=find_packages(exclude=['test']),
        include_package_data=True,
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
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Topic :: System :: Archiving :: Packaging",
            "Environment :: X11 Applications :: Qt",
            "Programming Language :: Python :: 2 :: Only",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: C++",
            "Topic :: Software Development :: Code Generators",
            ]
        )
