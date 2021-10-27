from defenitions import *
from inheritance_parser import parse_file
from data.meta_types import Type, GenType, Eq, Sub
from data.context import set_context
import unittest


class TestDefinitions(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        p = parse_file('example8.txt')
        set_context(p)

    def test_sub(self):
        self.assertTrue('LRightBranch2' |sub| 'LTemplate<double>')

    def test_bel(self):
        self.assertTrue('LRightBranch2' |bel| Type)
        self.assertFalse('LRightBranch2' |bel| GenType)
        self.assertFalse('LRightBranch2<T>' |bel| Type)
        self.assertTrue('LRightBranch2<T>' |bel| GenType)

    def test_gsub(self):
        self.assertEqual('LRightBranch2' |gsub| 'LTemplate<int>', (True, [Eq('double', 'int')]))
        self.assertEqual('LTemplate<T>' |gsub| 'LTemplate<int>', (True, [Eq('T', 'int')]))
        self.assertEqual('LRightBranch1' |gsub| 'LLeftBranch1', (False, []))
        self.assertEqual('LBase' |gsub| 'LTemplate<F>', (False, []))

    def test_lay(self):
        self.assertEqual('LTemplate<Z>' |lay| '(LRightBranch2, LIntermediate2)', (True, [Eq('double', 'Z')]))
        self.assertEqual('LRightBranch1' |lay| '(LLeftBranch2, LIntermediate2)', (False, []))

    def test_min_common_subtype(self):
        self.assertEqual(min_common_subtype('LRightBranch1', 'LLeftBranch1'),
                         (parsetype('LTemplate<double>'), [Eq('int', 'double')]))
        self.assertEqual(min_common_subtype('LRightBranch1', 'FakeClass'), (None, []))
        self.assertEqual(min_common_subtype('LRightBranch1', 'LIntermediate1'), (parsetype('LIntermediate1'), []))

    def test_max_type(self):
        self.assertEqual(max_type('LBase', 'LLeftBranch1'), (Type('LLeftBranch1'), []))
        self.assertEqual(max_type('LLeftBranch2', 'LLeftBranch1'), (Type('LLeftBranch2'), []))
        self.assertEqual(max_type('LLeftBranch2', 'LTemplate<F>'), (Type('LLeftBranch2'), [Eq('int', 'F')]))
        self.assertEqual(max_type('FakeClass', 'LLeftBranch1'), (None, []))

    def test_cros(self):
        self.assertEqual('(LLeftBranch1, LBase)' |cros| '(LRightBranch2, LIntermediate2)',
                         (parsetype('(LTemplate<int>, LIntermediate2)'), [Eq('double', 'int')]))
        self.assertEqual('(LIntermediate1, LBase)' |cros| '(LRightBranch2, LIntermediate2)',
                         (None, []))
        self.assertEqual('S' |cros| 'T', (parsetype('(LTemplate<double>, LIntermediate2'), [Eq('double', 'int')]))


    def test_vsub(self):
        self.assertEqual('U' |vsub| 'LBase', (True, []))
        self.assertEqual('U' |vsub| 'S', (False, []))
        self.assertEqual('LLeftBranch1' |vsub| '(LTemplate<Z>, LBase)', (True, [Eq('int', 'Z')]))
        self.assertEqual('LRightBranch2' |vsub| 'LTemplate<int>', (True, [Eq('double', 'int')]))


if __name__ == '__main__':
    unittest.main()
