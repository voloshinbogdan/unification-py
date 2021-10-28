from defenitions import *
from inheritance_parser import parse_file
from data.meta_types import Type, GenType, Eq, Sub
from data.context import set_context
import unittest
from parameterized import parameterized

p = parse_file('example8.txt')
set_context(p)


class TestDefinitions(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

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
        reset_var_num()
        self.assertEqual('(LLeftBranch1, LBase)' |cros| '(LRightBranch2, LIntermediate2)',
                         (parsetype('$Generated0(LTemplate<int>, LIntermediate2)'), [Eq('double', 'int')]))
        self.assertEqual('(LIntermediate1, LBase)' |cros| '(LRightBranch2, LIntermediate2)',
                         (None, []))
        self.assertEqual('S' |cros| 'T',
                         (parsetype('$Generated1(LTemplate<int>, LIntermediate2'), [Eq('double', 'int')]))

    def test_vsub(self):
        self.assertEqual('U' |vsub| 'LBase', (True, []))
        self.assertEqual('U' |vsub| 'S', (False, []))
        self.assertEqual('LLeftBranch1' |vsub| '(LTemplate<Z>, LBase)', (True, [Eq('int', 'Z')]))
        self.assertEqual('LRightBranch2' |vsub| 'LTemplate<int>', (True, [Eq('double', 'int')]))

    def test_rep(self):
        self.assertEqual(str('T' |rep| 'S'), 'T(LRightBranch2, LIntermediate2) -> S(LLeftBranch2, LIntermediate2)')

    @parameterized.expand([
        ([Eq('S', 'T'), Sub('S', 'U')], ['float' |rep| 'bool'],
         [Eq('S(LLeftBranch2, LIntermediate2)', 'T(LRightBranch2, LIntermediate2)'),
          Sub('S(LLeftBranch2, LIntermediate2)', 'U(LTemplate<bool>, LIntermediate2)')]),

        ([Eq('S', 'T'), Sub('S', 'U')], ['LIntermediate2' |rep| 'LIntermediate1'],
         [Eq('S(LLeftBranch2, LIntermediate1)', 'T(LRightBranch2, LIntermediate1)'),
          Sub('S(LLeftBranch2, LIntermediate1)', 'U(LTemplate<float>, LIntermediate1)')]),

        ([Eq('S', 'T'), Sub('S', 'U')], ['S' |rep| 'bool', 'LTemplate<float>' |rep| 'Student'],
         [Eq('bool', 'T(LRightBranch2, LIntermediate2)'),
          Sub('bool', 'U(Student, LIntermediate2)')])
    ])
    def test_at(self, constraints, substitutions, expected):
        substitutions |at| constraints
        self.assertSequenceEqual(constraints, expected)


    def test_infv(self):
        self.assertTrue('S' |infv| 'LTemplate<S>')
        self.assertFalse('T' |infv| 'LTemplate<S>')


    def test_bottom_top(self):
        self.assertTrue('BOTTOM' |sub| 'TOP')
        self.assertFalse('TOP' |sub| 'BOTTOM')
        self.assertTrue('BOTTOM' |gsub| 'TOP')
        self.assertEqual('TOP' |gsub| 'BOTTOM', (False, []))
        self.assertTrue('BOTTOM' |vsub| 'TOP')
        self.assertEqual('TOP' |vsub| 'BOTTOM', (False, []))

if __name__ == '__main__':
    unittest.main()
