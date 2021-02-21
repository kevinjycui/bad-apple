import unittest
from gmplot.utility import StringIO

class StringIOTest(unittest.TestCase):
    def test_enter_exit(self):
        with StringIO() as f:
            f.write('Content')
            self.assertEqual(f.getvalue(), 'Content')

        self.assertTrue(f.closed) 
