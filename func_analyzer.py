import dis

builtin_function_names = frozenset([
    "abs",
    "all",
    "any",
    "ascii",
    "bin",
    "bool",
    "bytearray",
    "bytes",
    "callable",
    "chr",
    "classmethod",
    "compile",
    "complex",
    "delattr",
    "dict",
    "dir",
    "divmod",
    "enumerate",
    "eval",
    "exec",
    "filter",
    "float",
    "format",
    "frozenset",
    "getattr",
    "globals",
    "hasattr",
    "hash",
    "help",
    "hex",
    "id",
    "input",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "locals",
    "map",
    "max",
    "memoryview",
    "min",
    "next",
    "object",
    "oct",
    "open",
    "ord",
    "pow",
    "print",
    "property",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "setattr",
    "slice",
    "sorted",
    "staticmethod",
    "str",
    "sum",
    "super",
    "tuple",
    "type",
    "vars",
    "zip",
    "__import__",
])

op_load_global = dis.opmap["LOAD_GLOBAL"]
op_load_deref = dis.opmap["LOAD_DEREF"]

def is_builtin_function_name(func_name):
    'Returns True if func_name is a builtin function name'
    return func_name in builtin_function_names

def get_load_globals(func):
    '''Get global variables used in given func
    It returns list of tupples of name and value.
    '''
    return [
        (i.argrepr, func.__globals__[i.argrepr])
        for i in dis.get_instructions(func)
        if i.opcode == op_load_global
        if not is_builtin_function_name(i.argrepr)
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
