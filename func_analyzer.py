import dis

op_load_global = dis.opmap["LOAD_GLOBAL"]
op_load_deref = dis.opmap["LOAD_DEREF"]

def get_load_globals(func):
    '''Get global variables used in given func
    It returns list of tupples of name and value.
    '''
    return [
        (i.argrepr, func.__globals__[i.argrepr])
        for i in dis.get_instructions(func)
        if i.opcode == op_load_global
        if i.argrepr in func.__globals__
    ]

def get_load_deref(func):
    '''Get free variables used in given func
    It returns list of tupples of name and value.
    '''
    return [
        (i.argrepr, func.__closure__[i.arg].cell_contents)
        for i in dis.get_instructions(func)
        if i.opcode == op_load_deref
    ]
