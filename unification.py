import data.context as ctx
from defenitions import *
import heapq


def unify(constraints):
    if not constraints:
        return [], []
    v = heapq.heappop(constraints)
    if v |bel| Eq:
        unify_eq(v)
    elif v |bel| Sub:
        unify_sub(v)


def unify_eq(c):
    pass


def unify_sub(c):
    pass
