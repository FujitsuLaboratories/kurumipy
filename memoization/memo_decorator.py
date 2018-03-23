import os
import re
import shutil
import threading
import fasteners
from .file_operation import get_hash, file_write, file_read, try_file_read, makedirs_safe
from .func_analyzer import get_load_globals, get_load_deref

# Directory for serialization
MEMO_DIR = os.path.join(os.path.dirname(__file__), 'memocache', 'cache')
# Directory for lock
LOCK_DIR = os.path.join(os.path.dirname(__file__), 'memocache', 'lock')

def key_value_list_to_dict(l):
    """
    Convert list of tuples of key string and value object to dict.
    Keys must be unique.
    """
    d = dict()
    for i in l:
        h = 0
        if callable(i[1]):
            try:
                h = hash(i[1].__code__.co_code)
            except AttributeError:
                h = hash(i[1].__name__)
        else:
            h = hash(i[1])
        d[i[0]] = h
    return d

class ReentrantInterprocessLock():
    """
    Inter-process lock using file.
    It supports reentrancy.
    """
    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.interprocess_lock = fasteners.InterProcessLock(lock_path)
        self.condition = threading.Condition()
        self.thread_id = 0
        self.recursion_count = 0

    def __enter__(self):
        ident = threading.get_ident()
        while True:
            with self.condition:
                if self.thread_id != 0 and self.thread_id != ident:
                    self.condition.wait()
                else:
                    if self.thread_id == ident:
                        self.recursion_count += 1
                    else:
                        self.thread_id = ident
                        self.recursion_count = 1
                        self.interprocess_lock.__enter__()
                    return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.condition:
            self.recursion_count -= 1
            if self.recursion_count == 0:
                self.thread_id = 0
                self.condition.notify_all()
                return self.interprocess_lock.__exit__(exc_type, exc_val, exc_tb)
            else:
                return False

def memo(function):
    """
    KurumiPy decorator.
    It will provide intelligent memonization to functions.
    """

    # Prepare directories
    makedirs_safe(MEMO_DIR)
    makedirs_safe(LOCK_DIR)

    # Generate path from function identifier
    qualified_name = function.__qualname__
    escaped_qname = re.sub(r'[<>]', '_', qualified_name)
    func_dir = os.path.join(MEMO_DIR, escaped_qname)
    env_path = os.path.join(func_dir, 'env.pickle')
    lock_path = os.path.join(LOCK_DIR, escaped_qname)

    def _memo(*args, **kwargs):
        _memo.calls += 1

        cachefilename_hash = get_hash(*args)
        cache_path = os.path.join(func_dir, 'cache-' + cachefilename_hash + '.pickle')

        func_env = {}
        func_env['bytecode'] = function.__code__.co_code
        func_env['consts'] = hash(function.__code__.co_consts)
        func_env['globals'] = key_value_list_to_dict(get_load_globals(function))
        func_env['frees'] = key_value_list_to_dict(get_load_deref(function))

        with _memo.lock:
            return_value = None
            has_env_file, previous_env = try_file_read(env_path)
            if has_env_file:
                if previous_env == func_env:
                    # Current env is save as previous. Use cache if it exists.
                    if os.path.isfile(cache_path):
                        _memo.hits += 1
                        return_value = file_read(cache_path)
                    else:
                        return_value = function(*args, **kwargs)
                        file_write(cache_path, return_value)
                else:
                    # Current env is different from previous. Remove all cache and recreate env file.
                    _memo.invalidates += 1
                    shutil.rmtree(func_dir)
                    os.makedirs(func_dir)
                    file_write(env_path, func_env)
                    return_value = function(*args, **kwargs)
                    file_write(cache_path, return_value)
            else:
                # There is no previous env file. Create it.
                if not os.path.isdir(func_dir):
                    os.makedirs(func_dir)
                file_write(env_path, func_env)
                return_value = function(*args, **kwargs)
                file_write(cache_path, return_value)
            return return_value
    _memo.calls = 0
    _memo.hits = 0
    _memo.invalidates = 0
    _memo.lock = ReentrantInterprocessLock(lock_path)

    return _memo
