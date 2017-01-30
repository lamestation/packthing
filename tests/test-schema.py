import unittest

from packthing import PackthingSchema

print PackthingSchema.SCHEMAS.keys()

class TestSchema(unittest.TestCase):

    def test_missing_keys(self):
        PackthingSchema.validate_packfile('draft2.yml')
        self.assertTrue({} == [])

if __name__ == '__main__':
    PackthingSchema.validate_packfile('draft2.yml')
#    unittest.main()
