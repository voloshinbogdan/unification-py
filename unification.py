import data.context as ctx
from defenitions import *
import heapq


class Fail(Exception):
    pass


def variable_cons(variable):
    assert isinstance(variable, Variable)

    if isinstance(variable.lower, GenType):
        cons = []
        for p in variable.lower.params:
            if isinstance(p, ConstrainedType):
                cons.append(p.constraints)
        return cons
    else:
        return []


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


def unify_fail(constraints):
    try:
        return unify(constraints)
    except Fail:
        return 'fail'


def unify(constraints):
    heap = []
    heap |con| constraints
    constrs, subs = _unify(heap)
    return [c[1] for c in constrs], subs


def _unify(constraints):
    if not constraints:
        return [], []
    _, v = heapq.heappop(constraints)
    S, T = v.left, v.right
    if isinstance(v, Sub) and v.view:
        return constraints |con| [v], []
    if isinstance(v, Eq):
        return unify_eq(constraints, S, T)
    elif isinstance(v, Sub):
        return unify_sub(constraints, S, T)


def unify_eq(constraints, S, T):
    r_lay, cross = [], []
    subs = []
    if S |bel| ConstrainedType:
        return _unify(constraints |con| ([Eq(S.type, T)] + S.constraints))
    if T |bel| ConstrainedType:
        return _unify(constraints |con| ([Eq(S, T.type)] + T.constraints))
    if S |bel| Type and T |bel| Type and S == T:
        return _unify(constraints)
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| r_lay:
        if r_lay:
            _, subs = unify(r_lay)
        subs += [S |rep| T]
        return _unify(subs |at| constraints) |adds| subs
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |lay| T |out| r_lay:
        if r_lay:
            _, subs = unify(r_lay)
        subs += [T |rep| S]
        return _unify(subs |at| constraints) |adds| subs
    elif S |bel| Variable and T |bel| Variable and not S |infv| T and not T |infv| S:
        X = test_lower_bound(S |cros| T |out| cross)  # May branch on X lower bound
        if X is not None:
            if cross:
                _, subs = unify(cross)
            subs += [S | rep | X, T | rep | X]
            return _unify(subs |at| constraints) |adds| subs
        else:
            raise Fail
    elif S |bel| GenType and T |bel| GenType and S.name == T.name:
        return _unify(constraints |con| make_eq_constraints(S.params, T.params))
    else:
        raise Fail


def test_lower_bound(X):
    if X is None:
        return None
    elif not X.lower |gsub| X.upper |out| "_":
        raise Fail
    elif unify_fail(unpack_constraints(X)) != 'fail':
        return X
    else:
        return test_lower_bound(new_var(get_parent(X.lower), X.upper))


def unify_sub(constraints, S, T):
    r_vsub, r_lay, SgT, ZS, ZT, r_gsub = [], [], [], [], [], []
    subs = []
    if S |bel| ConstrainedType:
        return _unify(constraints |con| ([Sub(S.type, T)] + S.constraints))
    if T |bel| ConstrainedType:
        return _unify(constraints |con| ([Sub(S, T.type)] + T.constraints))
    if S |vsub| T |out| r_vsub:  #TODO:  Здесь проаерятся, что S.Upper : T.Lower и S : T.Lower и S.Upper : T
        # May branch on T lower bound (TypeVal: Variable, Variable: Variable)
        if T |bel| Variable and T.lower |bel| GenType and r_vsub:
            Tnew = test_lower_bound(new_var(T.lower, T.upper, r_vsub))
            return _unify([T |rep| Tnew] |at| constraints) |adds| [T |rep| Tnew]
        else:
            if r_vsub:
                _, subs = unify(r_vsub)
            return _unify(subs |at| constraints) |adds| subs
    elif S |bel| Variable and T |bel| TypeVal and not S |infv| T and T |lay| S |out| r_lay:
        if r_lay:
            _, subs = unify(r_lay)
        X = new_var(S.lower, T)  # MAY BRANCH ON LOWER BOUND X OR NOT? No, S.lower O: T generate constraints, which can be excluded only when T excluded from variable, which leads to empty variable
        subs += [S |rep| X]
        return _unify(subs |at| (constraints |con| r_lay)) |adds| subs
    elif S |bel| TypeVal and T |bel| Variable and not T |infv| S and S |gsub| T.upper |out| r_gsub:
        Z = new_var(S, T.upper, r_gsub)
        X = test_lower_bound(Z |cros| T |out| ZT)
        if ZT:
            _, subs = unify(ZT)
        subs += [T |rep| X]
        return _unify(subs |at| constraints) |adds| subs
    elif S |bel| Variable and T |bel| Variable and not S |infv| T and not T |infv| S and\
            S.lower |gsub| T.upper |out| SgT:  # Should be any way.
        Z = new_var(S.lower, T.upper)
        X = test_lower_bound(Z |cros| S |out| ZS)  # May branch on X lower bound
        Y = test_lower_bound(Z |cros| T |out| ZT)  # May branch on Y lower bound
        subs = []
        for vf, vt in [(S, X), (T, Y)]:
            tmp_subs = unify(unpack_constraints(vf))
            if tmp_subs[1] |at| vf.lower != tmp_subs[1] |at| vt.lower or\
                    tmp_subs[1] |at| vf.upper != tmp_subs[1] |at| vt.upper:
                subs.append(vf |rep| vt)
        if SgT + ZS + ZT:
            _, s = unify(SgT + ZS + ZT)
            subs += s

        return _unify(subs |at| (constraints |con| [viewed(Sub(S, T))])) |adds| subs
    else:
        raise Fail


def unbranching():
    # We should have to consider substitution results (there is branching!)
    pass


def simplify_solution_after_unify(solution):
    intermediate_subs = []
    base_subs = []
    constraints, subs = solution

    for s in subs:
        if s.of.name.startswith('$Generated'):
            intermediate_subs.append(s)
        else:
            base_subs.append(s)

    res1 = []
    for i in range(len(base_subs)):
        res1.append((intermediate_subs + base_subs[:i] + base_subs[i+1:]) |at| base_subs[i])

    return intermediate_subs |at| constraints, res1
