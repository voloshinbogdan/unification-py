import data.context as ctx
from defenitions import *
import heapq

var_num = 0


def new_var(lower, upper):
    global var_num
    res = Variable('$Generated{0}'.format(var_num), lower, upper)
    var_num += 1
    return res


def add_substitutions(res, subs):
    return res[0], res[1] + subs


def concatenate_heap(heap, it):
    heap = heap + [(i.priority, i) for i in it]
    heapq.heapify(heap)
    return heap


adds = Infix(add_substitutions)
con = Infix(concatenate_heap)


def unify(constraints):
    heap = []
    heap |con| constraints
    return _unify(constraints)


def _unify(constraints):
    if not constraints:
        return [], []
    _, v = heapq.heappop(constraints)
    if v |bel| GenType and v.veiw:
        return constraints, []
    if isinstance(v, Eq):
        unify_eq(v)
    elif isinstance(v, Sub):
        unify_sub(constraints, v)
    else:
        raise Exception('fail')


def unify_eq(constraints, c):
    S, T = c.left, c.right
    if S |bel| Type and T |bel| Type and S == T:
        return _unify(constraints)
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| 'lay':
        return _unify([S |rep| T] |at| (constraints |con| ctx.outs['lay'])) |adds| [S |rep| T]
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| 'lay':
        return _unify([T |rep| S] |at| (constraints |con| ctx.outs['lay'])) |adds| [T |rep| S]
    elif S |bel| Variable and T |bel| Variable:
        X = S |cros| T |out| 'cross'
        if X is not None:
            return _unify([S |rep| X, T |rep| X] |at| (constraints |con| ctx.outs['cross'])) \
                   |adds| [S |rep| X, T |rep| X]
        else:
            raise Exception('fail')
    elif S |bel| GenType and T |bel| GenType and S.name == T.name:
        return _unify(constraints |con| make_eq_constraints(S.params, T.params))
    else:
        raise Exception('fail')


def unify_sub(constraints, c):
    S, T = c.left, c.right
    if S |vsub| T |out| 'vsub':
        _unify(constraints |con| ctx.outs['vsub'])
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| 'lay':
        X = new_var(T, S.upper)
        return _unify([S |rep| X] |at| (constraints |con| ctx.outs['lay'])) |adds| [S |rep| X]
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| 'lay':
        X = new_var(T.lower, S)
        return _unify([T |rep| X] |at| (constraints |con| ctx.outs['lay'])) |adds| [T |rep| X]
    elif S |bel| Variable and T |bel| Variable and not S |infv| T and not T |infv| S and\
            S.lower |gsub| T.upper |out| 'SgT':
        Z = new_var(S.lower, T.upper)
        X = Z |cros| T |out| 'ZT'
        Y = Z |cros| S |out| 'ZS'
        if X |vsub| Y |out| 'XvY':
            return _unify([S |rep| X, T |rep| Y] |at| (constraints |con| ctx.outs['SgT'] |con| ctx.outs['ZT'] |con|
                                                       ctx.outs['ZS'] |con| ctx.outs['XvY'])) \
                   |adds| [S |rep| X, T |rep| Y]
        else:
            return _unify([S |rep| X, T |rep| Y] |at| (constraints |con| ctx.outs['SgT'] |con| ctx.outs['ZT'] |con|
                                                       ctx.outs['ZS'] |con| ctx.outs['XvY']) |con| [viewed(Sub(X, Y))])\
                   |adds| [S |rep| X, T |rep| Y]
    else:
        raise Exception('fail')
