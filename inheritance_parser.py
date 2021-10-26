import graphviz
from data.meta_types import Type, GenType, parsetype, Eq, Sub, Variable


class Parser:

    def init_reading(self, line):
        raise ValueError("File should start with tag")
    
    def __init__(self):
        self.current_state = self.init_reading
        self.parents = {}
        self.variables = {}
        self.constraints = []

    def results(self):
        return {"parents": self.parents, "variables": self.variables, "constraints": self.constraints}

    def read_inheritance(self, line):
        tokens = list(map(parsetype, map(str.strip, line.split(':'))))
        self.parents[tokens[0]] = tokens[-1]

    def read_variables(self, line):
        var = parsetype(line)
        self.variables[var.name] = var
    
    def read_constraints(self, line):
        if ':' in line and '=' in line:
            raise ValueError('In one constraint can not be sub and eq')
        elif ':' in line:
            splitter = ':'
        elif '=' in line:
            splitter = '='
        else:
            raise ValueError('Unknown constraint {0}'.format(line))

        boundaries = list(map(str.strip, line.split(splitter)))
        bts = []
        for b in boundaries:
            if b in self.variables:
                bt = self.variables[b]
            else:
                bt = parsetype(b)
            bts.append(bt)
        left, right = bts
        
        if splitter == ':':
            c = Sub(left, right)
        else:
            c = Eq(left, right)
        
        self.constraints.append(c)

    def read_tag(self, line):
        line = str.strip(line)
        if line == "#Inheritance":
            self.current_state = self.read_inheritance
        elif line == "#Variables":
            self.current_state = self.read_variables
        elif line == "#Constraints":
            self.current_state = self.read_constraints
        else:
            raise ValueError("No such tag {0}".format(line))
    
    def read_line(self, line):
        if line.startswith("#"):
            self.read_tag(line)
        else:
            self.current_state(line)


def parse_file(fname):
    p = Parser()
    with open(fname) as f:
        for line in f:
            p.read_line(line)
    
    return {
        'parents': p.parents,
        'variables': p.variables,
        'constraints': p.constraints
    }


def build_graph(name, parents):
    e = graphviz.Digraph(name, filename=name + '.dot')
    e.graph_attr['rankdir'] = 'BT'
    
    keys = list(parents.keys())

    e.attr('node', shape='box')
    
    for k in keys:
        e.node(k.name, label=str(k))
    
    for f, t in parents.items():
        if isinstance(t, GenType):
            params = keys[keys.index(Type(t.name))].params
            e.edge(f.name, t.name, label=",".join(map(lambda x: '{0}={1}'.format(str(x[0]), str(x[1])),zip(params, t.params))))
        else:
            e.edge(f.name, t.name)
    print(e.source)
    return e
