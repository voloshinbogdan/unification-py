import string


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

    def __init__(self, name, lower, upper):
        self.name = name
        self.lower = lower
        self.upper = upper
    
    def __str__(self):
        return "{0}({1}, {2})".format(self.name, str(self.lower), str(self.upper))
    
    def __repr__(self):
        return self.__str__()
