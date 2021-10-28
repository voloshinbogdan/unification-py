import data.context as ctx
from inheritance_parser import parse_file
from data.context import set_context
from unification import unify


if __name__ == '__main__':
    p = parse_file('example1.txt')
    set_context(p)
    try:
        cons, subs = unify(ctx.constraints)
        print('***Constraints***:')
        print('\n'.join(map(str, cons)))
        print('\n***Substitutions***:')
        print('\n'.join(map(str, subs)))
    except Exception as e:
        if str(e) == 'fail':
            print('fail')
        else:
            raise

