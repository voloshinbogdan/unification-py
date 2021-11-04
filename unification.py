import data.context as ctx
from defenitions import *
import heapq


class Fail(Exception):
    pass


def add_substitutions(res, subs):
    return res[0], res[1] + subs


def concatenate_heap(_heap, it):
    f = isinstance(_heap, tuple)
    heap = _heap
    heap.extend([(i.priority, i) for i in it])
    heapq.heapify(heap)
    return heap


adds = Infix(add_substitutions)
con = Infix(concatenate_heap)


def unify(constraints):
    heap = []
    heap |con| constraints
    constrs, subs = _unify(heap)
    return [c[1] for c in constrs], subs


def _unify(constraints):
    if not constraints:
        return [], []
    _, v = heapq.heappop(constraints)
    if isinstance(v, Sub) and v.view:
        return constraints |con| [v], []
    if isinstance(v, Eq):
        return unify_eq(constraints, v)
    elif isinstance(v, Sub):
        return unify_sub(constraints, v)


def unify_eq(constraints, c):
    S, T = c.left, c.right
    r_lay, cross = [], []
    if S |bel| Type and T |bel| Type and S == T:
        return _unify(constraints)
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| r_lay:
        return _unify([S |rep| T] |at| (constraints |con| r_lay)) |adds| [S |rep| T]
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| r_lay:
        return _unify([T |rep| S] |at| (constraints |con| r_lay)) |adds| [T |rep| S]
    elif S |bel| Variable and T |bel| Variable:
        X = S |cros| T |out| cross  # May branch on X lower bound
        if X is not None:
            subs = [S | rep | X, T | rep | X]
            return _unify(subs |at| (constraints |con| cross)) |adds| subs
        else:
            raise Fail
    elif S |bel| GenType and T |bel| GenType and S.name == T.name:
        return _unify(constraints |con| make_eq_constraints(S.params, T.params))
    else:
        raise Fail


def unify_sub(constraints, c):
    S, T = c.left, c.right
    r_vsub, r_lay, SgT, ZS, ZT, XvY= [], [], [], [], [], []
    if S |vsub| T |out| r_vsub:
        # May branch on T lower bound (TypeVal: Variable, Variable: Variable)
        return _unify(constraints |con| r_vsub)
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| r_lay:
        X = new_var(S.lower, T)
        return _unify([S |rep| X] |at| (constraints |con| r_lay)) |adds| [S |rep| X]
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| r_lay:
        X = new_var(S, T.upper)
        return _unify([T |rep| X] |at| (constraints |con| r_lay)) |adds| [T |rep| X]
    elif S |bel| Variable and T |bel| Variable and not S |infv| T and not T |infv| S and\
            S.lower |gsub| T.upper |out| SgT:  # Should be any way.
        Z = new_var(S.lower, T.upper)
        X = Z |cros| S |out| ZS  # May branch on X lower bound
        Y = Z |cros| T |out| ZT  # May branch on Y lower bound
        subs = []
        for vf, vt in [(S, X), (T, Y)]:
            if vf.lower != vt.lower or vf.upper != vt.upper:
                subs.append(vf |rep| vt)

        def unify_constraints(additional=None):
            if additional is None:
                additional = []
            return _unify(subs |at| (constraints |con| SgT |con| ZS |con| ZT |con| XvY) |con| additional)

        if X |vsub| Y |out| XvY:
            return unify_constraints() |adds| subs
        else:
            return unify_constraints([viewed(subs |at| Sub(S, T))]) |adds| subs
    else:
        raise Fail


def simplify_solution_after_unify(solution):
    intermediate_subs = []
    base_subs = []
    constraints, subs = solution

    for s in subs:
        if s.of.name.startswith('$Generated'):
            intermediate_subs.append(s)
        else:
            base_subs.append(s)

    return intermediate_subs |at| constraints, intermediate_subs |at| base_subs
