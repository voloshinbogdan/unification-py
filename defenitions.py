from data.meta_types import *
from utility import Infix


@easy_types()
def is_subtype(t1, t2):
    while t1 is not None:
        if t1 |eq| t2:
            return True
        t1 = ctx.parents.get(t1.name, (None, None))[1]
    return False


@easy_types(0)
def belongs(v1, v2):
    return isinstance(v1, v2)


@easy_types()
def is_generic_subtype(t1, t2):
    if t1 |sub| t2:
        return True, []
    elif t2 |bel| GenType:
        while t1 is not None:
            if t1.name == t2.name:
                return True, t1.params |eleq| t2.params
            t1 = ctx.parents.get(t1.name, (None, None))[1]
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
    assert t |bel| TypeVal and v |bel| Variable, "Lay can be defined only for Type lay in Variable"
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
        t1 = ctx.parents.get(t1.name, (None, None))[1]
    return None, []


@easy_types()
def max_type(t1, t2):
    if t1 |gsub| t2 |out| "<":
        return t1, ctx.outs["<"]
    elif t2 |gsub| t1 |out| ">":
        return t2, ctx.outs[">"]
    else:
        return None, []


@easy_types()
def variables_cross(v1, v2):
    assert v1 |bel| Variable and v2 |bel| Variable, "Only two Variables can be crossed"
    lower, rmin = min_common_subtype(v1.lower, v2.lower)
    upper, rmax = max_type(v1.upper, v2.upper)

    if lower is None or upper is None or not lower |gsub| upper |out| "l sub u":
        return None, []
    else:
        return Variable('', lower, upper), rmin + rmax + ctx.outs["l sub u"]


@easy_types()
def variable_subtype(v1, v2):
    if v1 |bel| TypeVal and v2 |bel| TypeVal:
        return v1 |gsub| v2
    if v1 |bel| TypeVal and v2 |bel| Variable:
        return v1 |gsub| v2.lower
    if v1 |bel| Variable and v2 |bel| TypeVal:
        return v1.upper |gsub| v2
    if v1 |bel| Variable and v2 |bel| Variable:
        return v1.upper |gsub| v2.lower


def substitute(substitutions, constraints):
    if isinstance(substitutions, list):
        dsubs = {}
        for s in substitutions:
            dsubs[s.of.name] = s
        substitutions = dsubs

    if isinstance(constraints, list):
        res = []
        for c in constraints:
            res.append(substitute(substitutions, c))
        constraints.clear()
        constraints.extend(res)
        return None
    elif isinstance(constraints, Eq):
        return Eq(substitute(substitutions, constraints.left), substitute(substitutions, constraints.right))
    elif isinstance(constraints, Sub):
        return Sub(substitute(substitutions, constraints.left), substitute(substitutions, constraints.right))
    elif constraints |bel| GenType:
        if constraints.name in substitutions:
            return substitutions[constraints.name].to
        else:
            return GenType(constraints.name, [substitute(substitutions, p) for p in constraints.params])
    elif constraints |bel| Type:
        if constraints.name in substitutions:
            return substitutions[constraints.name].to
        else:
            return constraints
    elif constraints |bel| Variable:
        if constraints.name in substitutions:
            return substitutions[constraints.name].to
        else:
            return Variable(constraints.name, substitute(substitutions, constraints.lower),
                            substitute(substitutions, constraints.upper))


@easy_types()
def is_in_free_varaiables(v, t):
    if t.name == v.name:
        return True
    if t |bel| GenType:
        return all([is_in_free_varaiables(v, p) for p in t.params])
    return False


sub = Infix(is_subtype)
gsub = Infix(is_generic_subtype)
bel = Infix(belongs)
eq = Infix(equal_types)
eleq = Infix(make_eq_constraints)
lay = Infix(lay_in)
cros = Infix(variables_cross)
out = Infix(ctx.out_helper)
vsub = Infix(variable_subtype)
rep = Infix(lambda x, y: Substitution(x, y))
at = Infix(substitute)
infv = Infix(is_in_free_varaiables)
