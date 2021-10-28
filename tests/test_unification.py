import data.context as ctx
from inheritance_parser import parse_file
from data.context import set_context
from unification import unify


if __name__ == '__main__':
    p = parse_file('example8.txt')
    set_context(p)
    try:
        print(unify(ctx.constraints))
    except Exception as e:
        if str(e) == 'fail':
            print('fail')
        else:
            raise

