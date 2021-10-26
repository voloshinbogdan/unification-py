

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


class Type:
    
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


class GenType(Type):

    def __init__(self, name, params):
        Type.__init__(self, name)
        self.params = params
        
    def __str__(self):
        return self.name + "<" + ",".join(map(str, self.params)) + ">"


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


class Constraint:

    @easy_types(1, 2)
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.priority = -1
        self.operation = ''

    def __str__(self):
        return "{0} ? {1}".format(self.left, self.right)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{0} {2} {1}".format(self.left, self.right, self.operation)

    def __eq__(self, other):
        return (self.left, self.right, self.operation) == (other.left, other.right, other.operation)


class Sub(Constraint):

    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 10
        self.operation = ':'


class Eq(Constraint):

    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 1
        self.operation = '='


def op_conv_to_type(*params):
    res = []
    for p in params:
        assert isinstance(p, str) or isinstance(p, Type) or isinstance(p, Variable),\
               "Type should be str or Type or Variable"
        if isinstance(p, str):
            res.append(parsetype(p))
        else:
            res.append(p)
    return res


def parsetype(s):
    s = str.strip(s)
    if "<" in s:
        name, params = s.replace(">", "").split("<")
        params = list(map(parsetype, params.split(",")))
        return GenType(name, params)
    elif "(" in s:
        var_name, borders_line = list(map(str.strip, s.split('(')))
        lower, upper = list(map(parsetype, borders_line.split(')')[0].split(',')))

        return Variable(var_name, lower, upper)
    else:
        return Type(s)


def make_eq_constraints(params1, params2):
    assert(len(params1) == len(params2))
    return [Eq(p1, p2) for p1, p2 in zip(params1, params2)]