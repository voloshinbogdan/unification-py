from data.meta_types import *
from utility import Infix


def check_bottom_top(v1, v2):
    if v1 |bel| TypeVal and v1 == BOTTOM or v2 |bel| TypeVal and v2 == TOP:
        return True
    else:
        return False


def replace_parents_params(parent_pair, t):
    if parent_pair[0] is None:
        return None
    assert parent_pair[0].name == t.name

    if parent_pair[1] |bel| GenType and t |bel| GenType:
        subs = []
        for p1, p2 in zip(parent_pair[0].params, t.params):
            if p1 != p2:
                subs.append(p1 |rep| p2)
        return subs | at | parent_pair[1]
    else:
        return parent_pair[1]


def get_parent(t):
    return replace_parents_params(ctx.parents.get(t.name, (None, None)), t)


@easy_types()
def is_subtype(t1, t2):
    if check_bottom_top(t1, t2):
        return True
    while t1 is not None:
        if t1 |eq| t2:
            return True
        t1 = get_parent(t1)
    return False


@easy_types(0)
def belongs(v1, v2):
    return isinstance(v1, v2)


@easy_types()
def is_generic_subtype(t1, t2):
    if check_bottom_top(t1, t2):
        return True, []
    if t1 |sub| t2:
        return True, []
    elif t2 |bel| GenType:
        while t1 is not None:
            if t1.name == t2.name:
                return True, t1.params |eleq| t2.params
            t1 = get_parent(t1)
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
        t1 = get_parent(t1)
    return None, []


@easy_types()
def max_type(t1, t2):
    less, more = [], []
    if t1 |gsub| t2 |out| less:
        return t1, less
    elif t2 |gsub| t1 |out| more:
        return t2, more
    else:
        return None, []


@easy_types()
def variables_cross(v1, v2):
    assert v1 |bel| Variable and v2 |bel| Variable, "Only two Variables can be crossed"
    lower, rmin = min_common_subtype(v1.lower, v2.lower)
    upper, rmax = max_type(v1.upper, v2.upper)

    l_sub_u = []
    if lower is None or upper is None or not lower |gsub| upper |out| l_sub_u:
        return None, []
    else:
        return new_var(lower, upper), rmin + rmax + l_sub_u


@easy_types()
def variable_subtype(v1, v2):
    if check_bottom_top(v1, v2):
        return True, []
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
            if isinstance(c, tuple):
                sub_res = substitute(substitutions, c[1])
                res.append((sub_res.priority, sub_res))
            else:
                res.append(substitute(substitutions, c))
        constraints.clear()
        constraints.extend(res)
        return constraints
    elif isinstance(constraints, Substitution):
        return substitute(substitutions, constraints.of) |rep| substitute(substitutions, constraints.to)
    elif isinstance(constraints, Eq):
        return Eq(substitute(substitutions, constraints.left), substitute(substitutions, constraints.right))
    elif isinstance(constraints, Sub):
        left = substitute(substitutions, constraints.left)
        right = substitute(substitutions, constraints.right)
        view = constraints.view and left == constraints.left and right == constraints.right
        return Sub(left, right, view)
    elif constraints |bel| TypeVal and (constraints == BOTTOM or constraints == TOP):
        return constraints
    elif constraints |bel| GenType:
        if constraints.name in substitutions:
            return substitute(substitutions, substitutions[constraints.name].to)
        else:
            return GenType(constraints.name, [substitute(substitutions, p) for p in constraints.params])
    elif constraints |bel| Type:
        if constraints.name in substitutions:
            return substitute(substitutions, substitutions[constraints.name].to)
        else:
            return constraints
    elif constraints |bel| Variable:
        if constraints.name in substitutions:
            return substitute(substitutions, substitutions[constraints.name].to)
        else:
            return Variable(constraints.name, substitute(substitutions, constraints.lower),
                            substitute(substitutions, constraints.upper))


@easy_types()
def is_in_free_variables(v, t):
    if t.name == v.name:
        return True
    if t |bel| GenType:
        return all([is_in_free_variables(v, p) for p in t.params])
    return False


sub = Infix(is_subtype)
""" Operation t1 |sub| t2 define is t1 direct subtype of t2. Uses @easy_types. """

gsub = Infix(is_generic_subtype)
"""
Operation t1 |gsub| t2 define is t1 subtype of t2 with substitution in generic types. Uses @easy_types.
Returns (bool, [Constraint]). Use with out: t1 |gsub| t2 |out| "t1:t2".
"""

bel = Infix(belongs)
""" Operation t |bel| MetaType define is t instance of MetaType. Uses @easy_types. """

eq = Infix(equal_types)
""" Operation t1 |eq| t2 define is t1 and t2 equal. Uses @easy_types. """

eleq = Infix(make_eq_constraints)
""" Operation lt1 |eleq| lt2 makes equality constraints element wise from lists lt1, lt2. """

lay = Infix(lay_in)
"""
Operation t |lay| v define is type t inside type variable v. Uses @easy_types.
Returns (bool, [Constraint]). Use with out: t |lay| v |out| "t_in_v".
"""

cros = Infix(variables_cross)
"""
Operation v1 |cros| v2 calculates maximum general type diapason into new general variable. Uses @easy_types.
Returns (Variable, [Constraint]). Use with out: v1 |cros| v2 |out| "v1_cros_v2".
"""

out = Infix(ctx.out_helper)
"""
Helper operator result |out| key unpacks pair. Key has type string. Return first value, second value writes in context.
To get second value use context.outs(key).
"""

vsub = Infix(variable_subtype)
"""
Operation v1 |vsub| v2. Extends generic subtype on variables. Uses @easy_types. Returns (bool, [Constraint]).
Use with out: v1 |vsub| v2 |out| "v1_vsub_v2"
"""

rep = Infix(lambda x, y: Substitution(x, y))
""" Operation x |rep| y. Makes substitution x -> y. Replace x by y. Uses @easy_types. """

at = Infix(substitute)
""" Operation subs |at| x. Substitute substitutions subs in x. """

infv = Infix(is_in_free_variables)
""" Operation v |infv| x define is variable v in variables occurred in x. """
