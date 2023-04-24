import unittest


class RelixTest(unittest.TestCase):
    def test_import_modules(self):
        self.assertTrue(bool(__import__('relix.command').command))


if __name__ == '__main__':
    unittest.main()
