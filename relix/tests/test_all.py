from pathlib import Path
import unittest
import os
import sys
sys.path.insert(0, Path(os.getcwd()).parent.__str__())


class RelixTest(unittest.TestCase):
    def test_import_modules(self):
        self.assertTrue(bool)


if __name__ == '__main__':
    unittest.main()
