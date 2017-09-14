import dis

builtin_function_names = {
    "abs": True,
    "all": True,
    "any": True,
    "ascii": True,
    "bin": True,
    "bool": True,
    "bytearray": True,
    "bytes": True,
    "callable": True,
    "chr": True,
    "classmethod": True,
    "compile": True,
    "complex": True,
    "delattr": True,
    "dict": True,
    "dir": True,
    "divmod": True,
    "enumerate": True,
    "eval": True,
    "exec": True,
    "filter": True,
    "float": True,
    "format": True,
    "frozenset": True,
    "getattr": True,
    "globals": True,
    "hasattr": True,
    "hash": True,
    "help": True,
    "hex": True,
    "id": True,
    "input": True,
    "int": True,
    "isinstance": True,
    "issubclass": True,
    "iter": True,
    "len": True,
    "list": True,
    "locals": True,
    "map": True,
    "max": True,
    "memoryview": True,
    "min": True,
    "next": True,
    "object": True,
    "oct": True,
    "open": True,
    "ord": True,
    "pow": True,
    "print": True,
    "property": True,
    "range": True,
    "repr": True,
    "reversed": True,
    "round": True,
    "set": True,
    "setattr": True,
    "slice": True,
    "sorted": True,
    "staticmethod": True,
    "str": True,
    "sum": True,
    "super": True,
    "tuple": True,
    "type": True,
    "vars": True,
    "zip": True,
    "__import__": True,
}

def is_builtin_function_name(func_name):
    'Returns True if func_name is a builtin function name'
    return func_name in builtin_function_names

def get_load_globals(func):
    '''Get global variables used in given func
    It returns list of tupples of name and value.
    '''
    g = []
    for i in dis.get_instructions(func):
        if i.opcode == 116: #LOAD_GLOBAL
            if not is_builtin_function_name(i.argrepr):
                g.append((i.argrepr, func.__globals__[i.argrepr]))
    return g
