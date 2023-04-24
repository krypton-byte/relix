import unittest


class RelixTest(unittest.TestCase):
    def test_import_modules(self):
        from .load import COMMAND
        self.assertTrue(bool(COMMAND))


if __name__ == '__main__':
    unittest.main()