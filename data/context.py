
parents = None
variables = None
constraints = None
outs = {}


def set_context(context):
    global parents
    global variables
    global constraints
    parents = context['parents']
    variables = context['variables']
    constraints = context['constraints']


def out_helper(pair, outp):
    outs[outp] = pair[1]
    return pair[0]


def clear_storage():
    global outs
    outs = {}
