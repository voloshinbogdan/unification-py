from inheritance_parser import *
from defenitions import *
from data.meta_types import Type, GenType
import unittest


class TestDefinitions(unittest.TestCase):

    def test_sub(self):
        self.assertTrue('LRightBranch2' |sub| 'LTemplate<double>')

    def test_bel(self):
        self.assertTrue('LRightBranch2' |bel| Type)
        self.assertFalse('LRightBranch2' |bel| GenType)
        self.assertFalse('LRightBranch2<T>' |bel| Type)
        self.assertTrue('LRightBranch2<T>' |bel| GenType)


if __name__ == '__main__':
    p = parse_file('example8.txt')
    set_context(p)
    unittest.main()
