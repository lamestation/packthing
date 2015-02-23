import sys
from setuptools import setup
import platform

setup(
        name = "packthing",
        version = "0.1",
        description = "Write once, package everywhere",
        entry_points={
            'console_scripts': [
                'packthing = packthing.main:console',
                ],
            },
        test_suite="test",
        )
