import data.context as ctx
from inheritance_parser import parse_file
from data.context import set_context
from unification import unify, Fail
import unittest
from parameterized import parameterized


class UnificationTest(unittest.TestCase):

    @parameterized.expand([('example1.txt',), ('example8.txt',)])
    def test_unify(self, fname):
        print('\n\n Test unify on ', fname)
        p = parse_file(fname)
        set_context(p)
        try:
            cons, subs = unify(ctx.constraints)
            print('***Constraints***:')
            print('\n'.join(map(str, cons)))
            print('\n***Substitutions***:')
            print('\n'.join(map(str, subs)))
        except Fail:
            print('fail')


def main():
    unittest.main()


if __name__ == '__main__':
    main()