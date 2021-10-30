import data.context as ctx
import re


def easy_types(*params):
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


class Type(TypeVal):
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name


class GenType(TypeVal):

    def __init__(self, name, params):
        Type.__init__(self, name)
        self.params = params
        
    def __str__(self):
        return self.name + "<" + ",".join(map(str, self.params)) + ">"

    def __eq__(self, other):
        return self.name == other.name and self.params == other.params


class Variable:

    @easy_types(2, 3)
    def __init__(self, name, lower, upper):
        self.name = name
        self.lower = lower
        self.upper = upper

    def __str__(self):
        return "{0}({1}, {2})".format(self.name, str(self.lower), str(self.upper))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return other is not None and isinstance(other, Variable) and\
               (self.name == other.name or '?' in [self.name, other.name]) and\
               self.lower == other.lower and self.upper == other.upper


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
        return (self.left, self.right, self.operation) == (other.left, other.right, other.operation)

    def __lt__(self, other):
        return str(self) < str(other)


class Sub(Constraint):

    @easy_types(1, 2)
    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 2
        self.operation = ':'
        self.view = False

    def viewed(self):
        self.view = True
        self.priority = 3


class Eq(Constraint):

    @easy_types(1, 2)
    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 1
        self.operation = '='


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
    res = []
    for p in params:
        if not (isinstance(p, str) or isinstance(p, TypeVal) or isinstance(p, Variable)):
            print('oops')
        assert isinstance(p, str) or isinstance(p, TypeVal) or isinstance(p, Variable),\
               "Type should be str or Type or Variable"
        if isinstance(p, str):
            res.append(parsetype(p))
        else:
            res.append(p)
    return res


def index(str, sub):
    if sub in str:
        return str.index(sub)
    else:
        return float('inf')


def split_params(str):
    splits = []
    last = 0
    closed = [0, 0]
    for m in re.finditer('[,<>()]', str):
        if m[0] == ',' and closed == [0, 0]:
            splits.append(str[last: m.start(0)])
            last = m.end(0)
        elif m[0] == '<':
            closed[0] -= 1
        elif m[0] == '>':
            closed[0] += 1
        elif m[0] == '(':
            closed[1] -= 1
        elif m[0] == ')':
            closed[1] += 1
    splits.append(str[last:])
    return splits


def parsetype(s, variables=None):
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
        inds = [index(s, '()'), index(s, '('), index(s, '<')]
        if all(map(lambda x: x == float('inf'), inds)):
            indicator = -1
        else:
            indicator = min(list(range(3)), key=inds.__getitem__)

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


def viewed(s):
    s.viewed()
    return s


def make_eq_constraints(params1, params2):
    assert(len(params1) == len(params2))
    return [Eq(p1, p2) for p1, p2 in zip(params1, params2)]


var_num = 0


def new_var(lower, upper):
    global var_num
    res = Variable('$Generated{0}'.format(var_num), lower, upper)
    var_num += 1
    return res


def reset_var_num():
    global var_num
    var_num = 0


TOP = TypeVal("$Top")
BOTTOM = TypeVal("$Bottom")
