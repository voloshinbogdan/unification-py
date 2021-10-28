import data.context as ctx
from defenitions import *
import heapq


def add_substituons(res, subs):
    return res[0], res[1] + subs


adds = Infix(add_substituons)


def unify(constraints):
    if not constraints:
        return [], []
    v = heapq.heappop(constraints)
    if isinstance(v, Eq):
        unify_eq(v)
    elif isinstance(v, Sub):
        unify_sub(constraints, v)


def unify_eq(constraints, c):
    S, T = c.left, c.right
    if S |bel| Type and T |bel| Type and S == T:
        return unify(constraints)
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| 'lay':
        return unify([S |rep| T] |at| (constraints + ctx.outs['lay'])) |adds| [S |rep| T]
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| 'lay':
        return unify([T |rep| S] |at| (constraints + ctx.outs['lay'])) |adds| [T |rep| S]
    elif S |bel| Variable and T |bel| Variable:
        X = S |cros| T |out| 'cross'
        if X is not None:
            return unify([S |rep| X, T |rep| X] |at| (constraints + ctx.outs['cross'])) |adds| [S |rep| X, T |rep| X]
        else:
            raise Exception('fail')
    elif S |bel| GenType and T |bel| GenType and S.name == T.name:
        return unify(constraints + make_eq_constraints(S.params, T.params))
    else:
        raise Exception('fail')


def unify_sub(constraints, c):
    pass
