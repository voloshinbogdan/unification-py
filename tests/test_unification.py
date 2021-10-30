import data.context as ctx
from data.meta_types import parsetype
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
?(LLeftBranch2, LIntermediate2) : ?(LTemplate<int>, LIntermediate2)

Subs:
F -> int
S -> ?(LLeftBranch2, LIntermediate2)
U -> ?(LTemplate<int>, LIntermediate2)
"""),
        ('example2.txt', """

Subs:
F -> int
S -> ?(LIntermediate2, LIntermediate1)
T -> ?(LIntermediate2, LIntermediate1)
"""),
        ('example3.txt', """

Subs:
G -> double
S -> ?(LIntermediate2, LIntermediate1)
T -> ?(LIntermediate2, LIntermediate1)
"""),
        ('example4.txt', """

Subs:
G -> double
S -> ?(LLeftBranch2, LLeftBranch1)
T(LRightBranch2<int, double>, LBase) -> ?(LTemplate<int, double>, LBase)
F -> int
"""),
        ('example5.txt', 'fail'),
        ('example6.txt', 'fail'),
        ('example8.txt', 'fail')])
    def test_unify(self, fname, expected):
        p = parse_file(fname)
        set_context(p)
        expected = parse_result(expected)
        try:
            cons, subs = simplify_solution_after_unify(unify(ctx.constraints))
            self.assertIsNotNone(expected)
            econs, esubs = expected
            self.assertCountEqual(cons, econs)
            self.assertCountEqual(subs, esubs)
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
