import sys
from setuptools import setup
import platform

setup(
        name = "packup",
        version = "0.1",
        description = "Write once, package everywhere",
        entry_points={
            'console_scripts': [
                'packup = packup.main:console',
                ],
            },
        test_suite="test",
        )
