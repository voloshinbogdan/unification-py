from data.meta_types import *
import data.constraints
from functools import partial
from inheritance_parser import parsetype

parents = None
variables = None
constraints = None


class Infix(object):
    def __init__(self, func):
        self.func = func

    def __or__(self, other):
        return self.func(other)

    def __ror__(self, other):
        return Infix(partial(self.func, other))

    def __call__(self, v1, v2):
        return self.func(v1, v2)


def easy_types(*params):
    def layer(func):
        def inner(*args):
            if not params:
                return func(*op_conv_to_type(*args))

            new_args = []
            for i, a in enumerate(args):
                if i in params:
                    new_args.append(op_conv_to_type(a)[0])
                else:
                    new_args.append(a)

            return func(*new_args)
        return inner
    return layer


def set_context(context):
    global parents
    global variables
    global constraints
    parents = context['parents']
    variables = context['variables']
    constraints = context['constraints']


def op_conv_to_type(*params):
    res = []
    for p in params:
        assert isinstance(p, str) or isinstance(p, Type), "Type should be str or Type"
        if isinstance(p, str):
            res.append(parsetype(p))
        else:
            res.append(p)
    return res


@easy_types()
def is_subtype(t1, t2):

    while t1 is not None:
        if t1 |eq| t2:
            return True
        t1 = parents.get(t1)
    return False


@easy_types(0)
def belongs(v1, v2):
    return type(v1) is v2


@easy_types()
def is_generic_subtype(t1, t2):
    if t1 |sub| t2:
        return True, []
    elif t1 |bel| Type and t2 |bel| GenType:
        pass

    return False, []


@easy_types()
def equal_types(t1, t2):
    if t1 |bel| Type and t2 |bel| Type:
        return t1.name == t2.name
    elif t1 |bel| GenType and t2 |bel| GenType:
        return t1.name == t2.name and t1.params == t2.params
    return False


sub = Infix(is_subtype)
gsub = Infix(is_generic_subtype)
bel = Infix(belongs)
eq = Infix(equal_types)
