import dis

op_load_global = dis.opmap["LOAD_GLOBAL"]
op_load_deref = dis.opmap["LOAD_DEREF"]

def get_load_globals(func):
    '''Get global variables used in given func
    It returns list of tupples of name and value.
    '''
    reprs = [
        i.argrepr
        for i in dis.get_instructions(func)
        if i.opcode == op_load_global
        if i.argrepr in func.__globals__
    ]
    # Make unique and preserve ordering
    reprs_uniq = sorted(set(reprs), key=reprs.index)
    return [
        (r, func.__globals__[r])
        for r in reprs_uniq
    ]

def get_load_deref(func):
    '''Get free variables used in given func
    It returns list of tupples of name and value.
    '''
    insts = [
        (i.argrepr, i.arg)
        for i in dis.get_instructions(func)
        if i.opcode == op_load_deref
    ]
    # Make unique and preserve ordering
    insts_uniq = sorted(set(insts), key=insts.index)
    return [
        (i[0], func.__closure__[i[1]].cell_contents)
        for i in insts_uniq
    ]
