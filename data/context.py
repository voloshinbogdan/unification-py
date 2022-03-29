
parents = None
variables = None
constraints = None
_outs = {}


def outs(key):
    return _outs.get(key, [])


def set_context(context):
    global parents
    global variables
    global constraints
    parents = context['parents']
    variables = context['variables']
    constraints = context['constraints']


def out_helper(pair, outp):
    if isinstance(outp, str):
        _outs[outp] = pair[1]
    elif isinstance(outp, list):
        if pair[1] is not None:
            outp.clear()
            outp.extend(pair[1])
    return pair[0]


def clear_storage():
    global _outs
    _outs = {}
