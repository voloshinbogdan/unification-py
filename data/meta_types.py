import data.context as ctx
import re
from collections import Counter
from copy import deepcopy


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

    def substitute(self, substitutions):
        if self.name in substitutions:
            return substitute(substitutions, substitutions[self.name].to)
        else:
            return self

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class GenType(TypeVal):

    def __init__(self, name, params):
        TypeVal.__init__(self, name)
        self.params = params

    def substitute(self, substitutions):
        if self.name in substitutions:
            return substitute(substitutions, substitutions[self.name].to)
        else:
            return GenType(self.name, [substitute(substitutions, p) for p in self.params])
        
    def __str__(self):
        return self.name + "<" + ",".join(map(str, self.params)) + ">"

    def __eq__(self, other):
        return self.name == other.name and self.params == other.params

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.name) | sum(map(hash, self.params))


class ConstrainedType(TypeVal):

    @easy_types(1)
    def __init__(self, any_type, subs):  #TODO: Можно ли заменить равенство на подстановки?
        if isinstance(subs, list):
            self.constraints = subs
        else:
            self.constraints = [subs]

        for c in self.constraints:
            if c == 'fail':
                continue
            if isinstance(c.of, ConstrainedType):
                self.constraints.extend(c.left.constraints)
                c.left = c.of.type
            if isinstance(c.to, ConstrainedType):
                self.constraints.extend(c.right.constraints)
                c.right = c.to.type

        if isinstance(any_type, ConstrainedType):
            self.type = any_type.type
            self.name = any_type.name
            self.constraints.extend(any_type.constraints)
        else:
            self.name = any_type.name
            self.type = any_type

        self.constraints = list(set(self.constraints))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{0}{1}".format(self.type, self.constraints)

    def substitute(self, substitutions):
        res = ConstrainedType(substitute(substitutions, self.type),
                              substitute(substitutions, list(set(self.constraints).difference(substitutions.values()))))
        if not res.constraints:
            res = res.type
        return res

    def __eq__(self, other):
        if other is None or not isinstance(other, ConstrainedType):
            return False

        return self.type == other.type and Counter(self.constraints) == Counter(other.constraints)

    def __hash__(self):
        return hash(self.type) | sum(map(hash, self.constraints))


variable_matches = None


def variable_matching_on():
    global variable_matches
    variable_matches = {}


def variable_matching_off():
    global variable_matches
    variable_matches = None


class Variable:

    @easy_types(2, 3)
    def __init__(self, name, lower, upper):
        self.name = name
        self.lower = lower
        self.upper = upper

    def substitute(self, substitutions):
        if self.name in substitutions:
            return substitute(substitutions, substitutions[self.name].to)
        else:
            return Variable(
                self.name,
                substitute(substitutions, self.lower),
                substitute(substitutions, self.upper))

    def __str__(self):
        return "{0}({1}, {2})".format(self.name, str(self.lower), str(self.upper))

    def __repr__(self):
        return self.__str__()

    def __le__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(self.lower) | hash(self.upper)

    def __eq__(self, other):
        is_bounds_equal = other is not None and isinstance(other, Variable) and\
                          self.lower == other.lower and self.upper == other.upper
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

    def substitute(self, substitutions):
        left = substitute(substitutions, self.left)
        right = substitute(substitutions, self.right)
        view = self.view and left == self.left and right == self.right
        return Sub(left, right, view)

    def viewed(self):
        self.view = True
        self.priority = 3


class Eq(Constraint):

    @easy_types(1, 2)
    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 1
        self.operation = '='

    def substitute(self, substitutions):
        return Eq(substitute(substitutions, self.left), substitute(substitutions, self.right))

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

    def substitute(self, substitutions):
        return Substitution(self.of, substitute(substitutions, self.to))

    def __hash__(self):
        return hash(self.of) | hash(self.to)

    def __le__(self, other):
        return str(self) < str(other)

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
        # assert isinstance(p, str) or isinstance(p, TypeVal) or isinstance(p, Variable) or isinstance(p, tuple),\
        #       "Type should be str or Type or Variable"
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


def find_in_first_level(s, c):
    locations = []
    closed = [0, 0, 0]
    for m in re.finditer('[\[\]<>()' + c + ']', s):
        if m[0] == c and closed == [0, 0, 0]:
            locations.append(m.start(0))
        elif m[0] == '<':
            closed[0] -= 1
        elif m[0] == '>' and s[m.start(0) - 1] != '-':
            closed[0] += 1
        elif m[0] == '(':
            closed[1] -= 1
        elif m[0] == ')':
            closed[1] += 1
        elif m[0] == '[':
            closed[2] -= 1
        elif m[0] == ']':
            closed[2] += 1
    return locations


def split_params(s):
    """
    Split string on parameters split by commas with attention to brackets
    :param s: string to split
    :return: list of parameters
    """
    commas = find_in_first_level(s, ',')

    last = 0
    res = []
    for v in commas:
        res.append(s[last: v])
        last = v + 1
    res.append(s[last:])

    return res


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
    check_ops = [
        find_in_first_level(s, '='),
        find_in_first_level(s, ':'),
        find_in_first_level(s, '-')
    ]
    if s == "BOTTOM":
        return BOTTOM
    elif s == "TOP":
        return TOP
    elif check_ops[0]:  # =
        t1, t2 = list(map(lambda x: parsetype(x.strip(), variables), [s[:check_ops[0][0]], s[check_ops[0][0] + 1:]]))
        return Eq(t1, t2)
    elif check_ops[1]:  # :
        t1, t2 = list(map(lambda x: parsetype(x.strip(), variables), [s[:check_ops[1][0]], s[check_ops[1][0] + 1:]]))
        return Sub(t1, t2)
    elif check_ops[2]:  # ->
        of, to = list(map(lambda x: parsetype(x.strip(), variables), [s[:check_ops[2][0]], s[check_ops[2][0] + 2:]]))
        return Substitution(of, to)
    else:

        if s.endswith(']'):
            t_val, _, params = s.partition('[')
            params = parse_constraints(params.rpartition(']')[0], variables)
            return ConstrainedType(parsetype(t_val, variables), params)

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


def parse_constraints(s, variables=None):
    params = []
    for param in split_params(s):
        lv, _, rv = list(map(lambda x: x.strip(), param.partition('->')))
        params.append(Substitution(parsetype(lv, variables), parsetype(rv, variables)))
    return params


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


def new_var_name():
    global var_num
    name = '$Generated{0}'.format(var_num)
    var_num += 1
    return name


def reset_var_num():
    """
    Resets generated variables counter
    """
    global var_num
    var_num = 0


TOP = TypeVal("$Top")
BOTTOM = TypeVal("$Bottom")


def substitute(substitutions, constraints):
    if isinstance(substitutions, list):
        dsubs = {}
        for s in substitutions:
            dsubs[s.of.name] = s
        substitutions = dsubs

    if isinstance(constraints, list) or isinstance(constraints, tuple):
        res = []
        for c in constraints:
            if isinstance(c, tuple) and isinstance(c[0], int):
                sub_res = substitute(substitutions, c[1])
                res.append((sub_res.priority, sub_res))
            else:
                res.append(substitute(substitutions, c))
        if isinstance(constraints, list):
            return res
        else:
            return tuple(res)
    elif isinstance(constraints, TypeVal) and (constraints == BOTTOM or constraints == TOP):
        return constraints
    else:
        return constraints.substitute(substitutions)
