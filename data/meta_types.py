import data.context as ctx
import re
from collections import Counter


def easy_types(*params):
    """
    Decorator optional parse arguments on positions params to meta types
    :param params: positions to convert if is empty convert all arguments
    :return: decorated function
    """
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


class TypeVal:

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __le__(self, other):
        return str(self) < str(other)


class Type(TypeVal):
    
    def __init__(self, name):
        TypeVal.__init__(self, name)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name


class GenType(TypeVal):

    def __init__(self, name, params):
        TypeVal.__init__(self, name)
        self.params = params
        
    def __str__(self):
        return self.name + "<" + ",".join(map(str, self.params)) + ">"

    def __eq__(self, other):
        return self.name == other.name and self.params == other.params


variable_matches = None


def variable_matching_on():
    global variable_matches
    variable_matches = {}


def variable_matching_off():
    global variable_matches
    variable_matches = None


class Variable:

    @easy_types(2, 3)
    def __init__(self, name, lower, upper, params=None):
        self.name = name
        self.lower = lower
        self.upper = upper
        if params is None:
            self.params = []
        else:
            self.params = params

    def __str__(self):
        return "{0}({1}|{3}, {2})".format(self.name, str(self.lower), str(self.upper), str(self.params))

    def __repr__(self):
        return self.__str__()

    def __le__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        is_bounds_equal = other is not None and isinstance(other, Variable) and\
                          self.lower == other.lower and self.upper == other.upper and\
                          Counter(self.params) == Counter(other.params)
        if not is_bounds_equal:
            return False

        if variable_matches is not None and self.name != '?' and other.name != '?':
            if self.name.startswith('?') and other.name.startswith('?'):
                return self.name == other.name

            sname = variable_matches.get(self.name) if self.name.startswith('?') else self.name
            oname = variable_matches.get(other.name) if other.name.startswith('?') else other.name
            if sname is None:
                if oname in variable_matches:
                    return False
                sname = oname
                variable_matches[self.name] = sname
                variable_matches[sname] = self.name
            elif oname is None:
                if sname in variable_matches:
                    return False
                oname = sname
                variable_matches[other.name] = oname
                variable_matches[oname] = other.name

            return sname == oname

        return self.name == other.name or '?' in [self.name, other.name]


class Constraint:

    @easy_types(1, 2)
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.priority = -1
        self.operation = '?'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{0} {2} {1}".format(self.left, self.right, self.operation)

    def __eq__(self, other):
        return other is not None and isinstance(other, Constraint) and\
               (self.left, self.right, self.operation) == (other.left, other.right, other.operation)

    def __lt__(self, other):
        return str(self) < str(other)


class Sub(Constraint):

    @easy_types(1, 2)
    def __init__(self, left, right, view=False):
        Constraint.__init__(self, left, right)
        self.priority = 3 if view else 2
        self.operation = ':'
        self.view = view

    def viewed(self):
        self.view = True
        self.priority = 3


class Eq(Constraint):

    @easy_types(1, 2)
    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 1
        self.operation = '='

    def __eq__(self, other):
        return other is not None and isinstance(other, Eq) and (
               (self.left, self.right) == (other.left, other.right) or
               (self.right, self.left) == (other.left, other.right)
        )

    def __hash__(self):
        return hash(str(sorted([str(self.left), str(self.right)])))


class Substitution:

    @easy_types(1, 2)
    def __init__(self, of, to):
        self.to = to
        self.of = of

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{0} -> {1}".format(self.of, self.to)

    def __eq__(self, other):
        return other is not None and isinstance(other, Substitution) and self.to == other.to and self.of == other.of


def op_conv_to_type(*params):
    """
    Optional parameters to meta types
    :param params: list of str or TypeVal or Variable
    :return: converted arguments
    """
    res = []
    for p in params:
        assert isinstance(p, str) or isinstance(p, TypeVal) or isinstance(p, Variable),\
               "Type should be str or Type or Variable"
        if isinstance(p, str):
            res.append(parsetype(p))
        else:
            res.append(p)
    return res


def index(s, sub):
    """
    Get index of substring sub in string str. If there are no such substring returns inf
    :param s: string to find substring
    :param sub: substring to find
    :return: First index of sub in s
    """
    if sub in s:
        return s.index(sub)
    else:
        return float('inf')


def split_params(s):
    """
    Split string on parameters split by commas with attention to brackets
    :param s: string to split
    :return: list of parameters
    """
    splits = []
    last = 0
    closed = [0, 0]
    for m in re.finditer('[,<>()]', s):
        if m[0] == ',' and closed == [0, 0]:
            splits.append(s[last: m.start(0)])
            last = m.end(0)
        elif m[0] == '<':
            closed[0] -= 1
        elif m[0] == '>':
            closed[0] += 1
        elif m[0] == '(':
            closed[1] -= 1
        elif m[0] == ')':
            closed[1] += 1
    splits.append(s[last:])
    return splits


def parsetype(s, variables=None):
    """
    Parse string on meta types, based on set of variables
    :param s: string to parse
    :param variables: dict from type variable name to Variable
    :return: parsed meta type
    """
    if variables is None:
        variables = ctx.variables
    s = str.strip(s)
    if s == "BOTTOM":
        return BOTTOM
    elif s == "TOP":
        return TOP
    elif '->' in s:
        of, to = list(map(lambda x: parsetype(x.strip(), variables), s.split('->')))
        return Substitution(of, to)
    elif ':' in s:
        t1, t2 = list(map(lambda x: parsetype(x.strip(), variables), s.split(':')))
        return Sub(t1, t2)
    elif '=' in s:
        t1, t2 = list(map(lambda x: parsetype(x.strip(), variables), s.split('=')))
        return Eq(t1, t2)
    else:
        indices = [index(s, '()'), index(s, '('), index(s, '<')]
        if all(map(lambda x: x == float('inf'), indices)):
            indicator = -1
        else:
            indicator = min(list(range(3)), key=indices.__getitem__)

        if indicator == 0:
            var_name, _, _ = list(map(str.strip, s.partition('(')))
            return Variable(var_name, BOTTOM, TOP)
        elif indicator == 1:
            var_name, _, borders_line = list(map(str.strip, s.partition('(')))
            lower, upper = list(map(lambda x: parsetype(x, variables), split_params(borders_line.rpartition(')')[0])))

            return Variable(var_name, lower, upper)
        elif indicator == 2:
            name, _, params = s.partition('<')
            params = params.rpartition('>')[0]
            params = list(map(lambda x: parsetype(x, variables), split_params(params)))
            return GenType(name, params)
        else:
            if s in variables:
                return variables[s]
            else:
                return Type(s)


def viewed(s: Sub) -> Sub:
    """
    Make constraint subtype viewed and return this
    :param s: subtype constraint
    :return: s made viewed
    """
    s.viewed()
    return s


def make_eq_constraints(params1, params2):
    assert(len(params1) == len(params2))
    return [Eq(p1, p2) for p1, p2 in zip(params1, params2)]


var_num = 0


def new_var(lower, upper, params=[]):
    """
    Generate new variable with generated name
    :param params: lower bound params
    :param lower: lower bound
    :param upper: upper bound
    :return: generated variable
    """
    global var_num
    res = Variable('$Generated{0}'.format(var_num), lower, upper)
    res.params.extend(params)
    var_num += 1
    return res


def reset_var_num():
    """
    Resets generated variables counter
    """
    global var_num
    var_num = 0


TOP = TypeVal("$Top")
BOTTOM = TypeVal("$Bottom")
