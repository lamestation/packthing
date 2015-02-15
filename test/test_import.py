import unittest
import importer

from types import ModuleType

class TestImporter(unittest.TestCase):

    def test_canimport(self):
        for f in ['qmake', 'directory',]:
            builder = importer.get_module("builder",f)
            self.assertIsInstance(builder, ModuleType)

        for f in ['git',]:
            vcs = importer.get_module("vcs",f)
            self.assertIsInstance(vcs, ModuleType)

    def test_invalidimport(self):
        self.assertRaises(ImportError, importer.get_module, "builder", "bacon")

if __name__ == '__main__':
    unittest.main()
