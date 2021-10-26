from data.meta_types import *
from utility import Infix

parents = None
variables = None
constraints = None


def set_context(context):
    global parents
    global variables
    global constraints
    parents = context['parents']
    variables = context['variables']
    constraints = context['constraints']


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
    elif t2 |bel| GenType:
        while t1 is not None:
            if t1.name == t2.name:
                return True, t1.params |eleq| t2.params
            t1 = parents.get(t1)
        return False, []

    return False, []


@easy_types()
def equal_types(t1, t2):
    if t1 |bel| Type and t2 |bel| Type:
        return t1.name == t2.name
    elif t1 |bel| GenType and t2 |bel| GenType:
        return t1.name == t2.name and t1.params == t2.params
    return False


@easy_types()
def lay_in(t, v):
    assert isinstance(t, Type) and v | bel | Variable, "Lay can be defined only for Type lay in Variable"
    r1 = t | gsub | v.upper
    r2 = v.lower | gsub | t
    if r1[0] and r2[0]:
        return True, r1[1] + r2[1]
    else:
        return False, []


@easy_types()
def min_common_subtype(t1, t2):
    while t1 is not None:
        r = t2 |gsub| t1
        if r[0]:
            return t1, r[1]
        t1 = parents.get(t1)
    return None, []


@easy_types()
def max_type(t1, t2):
    if gsub(t1, t2)[0]:
        return t1
    elif gsub(t2, t1)[0]:
        return t2
    else:
        return None


sub = Infix(is_subtype)
gsub = Infix(is_generic_subtype)
bel = Infix(belongs)
eq = Infix(equal_types)
eleq = Infix(make_eq_constraints)
lay = Infix(lay_in)
