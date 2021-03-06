import data.context as ctx
from data.meta_types import parsetype, variable_matching_on, variable_matching_off
from inheritance_parser import parse_file
from data.context import set_context
from unification import unify, Fail, simplify_solution_after_unify
from defenitions import rep
import unittest
from parameterized import parameterized


verbose = False


def parse_result(str):
    if str == 'fail':
        return None
    lines = list(filter(lambda x: x != '', str.split('\n')))
    splitter = lines.index('Subs:')
    constrs, subs = lines[:splitter], lines[splitter + 1:]
    constrs = list(map(parsetype, constrs))
    subs = list(map(parsetype, subs))
    return constrs, subs


class UnificationTest(unittest.TestCase):

    @parameterized.expand([
        ('example1.txt', """
S : ?Y(LTemplate<int>, LIntermediate2)

Subs:
F -> int
U -> ?Y(LTemplate<int>, LIntermediate2)
"""),
        ('example2.txt', """

Subs:
F -> int
S -> ?X(LIntermediate2, LIntermediate1)
T -> ?X(LIntermediate2, LIntermediate1)
"""),
        ('example3.txt', """

Subs:
G -> double
S -> ?X(LIntermediate2, LIntermediate1)
T -> ?X(LIntermediate2, LIntermediate1)
"""),
        ('example4.txt', """

Subs:
G -> double
T(LRightBranch2<int, double>, LBase) -> ?Y(LTemplate<int, double>, LBase)
F -> int
"""),
        ('example5.txt', 'fail'),
        ('example6.txt', 'fail'),
        ('example7.txt', """
S: U
?Y(LRightBranch2<int, G>, LIntermediate1): U

Subs:
T -> ?Y(LRightBranch2<int, G>, LIntermediate1)
"""),
        ('example8.txt', 'fail')])
    def test_unify(self, fname, expected):
        p = parse_file(fname)
        set_context(p)
        expected = parse_result(expected)
        try:
            cons, subs = simplify_solution_after_unify(unify(ctx.constraints))
            self.assertIsNotNone(expected)
            econs, esubs = expected
            variable_matching_on()
            self.assertCountEqual(cons, econs)
            self.assertCountEqual(subs, esubs)
            variable_matching_off()
            if verbose:
                print('\n\n Test unify on', fname)
                print('***Constraints***:')
                print('\n'.join(map(str, cons)))
                print('\n***Substitutions***:')
                print('\n'.join(map(str, subs)))
        except Fail:
            self.assertIsNone(expected)
        except Exception:
            raise


def main():
    unittest.main()


if __name__ == '__main__':
    main()
