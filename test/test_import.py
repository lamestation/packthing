import unittest
from packthing import importer
from packthing import target, vcs, builder

from types import ModuleType

class TestImporter(unittest.TestCase):

    def test_canimport(self):
        for f in ['qmake', 'dir',]:
            b = importer.get_module(builder,f)
            self.assertIsInstance(b, ModuleType)

        for f in ['git',]:
            v = importer.get_module(vcs,f)
            self.assertIsInstance(v, ModuleType)

    def test_invalidimport(self):
        with self.assertRaises(ImportError):
            importer.get_module(builder, "bacon")

if __name__ == '__main__':
    unittest.main()
