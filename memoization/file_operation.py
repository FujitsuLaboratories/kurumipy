import os
import pickle
import threading

def get_hash(*args):
    """Return hex string of hash value of args"""
    hash_num = hash(args)
    return hex(hash_num)

def file_write(path, data):
    """Serialize data and save to a file"""
    with open(path, mode='wb') as f:
        pickle.dump(data, f)

def file_read(path):
    """Deserialize from a file and return an object"""
    with open(path, mode='rb') as f:
        result = pickle.load(f)
    return result 

def try_file_read(path):
    """Try to deserialize from a file and return a tuple of boolean and object"""
    if os.path.isfile(path):
        with open(path, mode='rb') as f:
            result = pickle.load(f)
            return True, result
    return False, None

DIR_LOCK = threading.Lock()
def dir_make(dirpath):
    """Thread-safe version of makedirs"""
    if not os.path.isdir(dirpath):
        with DIR_LOCK:
            if not os.path.isdir(dirpath):
                try:
                    os.makedirs(dirpath)
                except:
                    pass
