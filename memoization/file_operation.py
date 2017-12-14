import os
import pickle
import threading

# ファイル名に使用するハッシュ値(str型)を取得する
def get_hash(*args):
    hash_num = hash(args)
    return hex(hash_num)

# ファイルにデータをシリアライズして保存
def file_write(path, data):
    with open(path, mode='wb') as f:
        pickle.dump(data, f)

# ファイルからデータをデシリアライズして読み込み、返す
def file_read(path):
    with open(path, mode='rb') as f:
        result = pickle.load(f)
    return result 

# ファイルの存在確認をし、ファイルがあればファイルからデータをデシリアライズして読み込み、返す
def try_file_read(path):
    if os.path.isfile(path):
        with open(path, mode='rb') as f:
            result = pickle.load(f)
            return True, result
    return False, None

# ディレクトリを作成（1プロセス複数スレッドにおける排他制御に対応）
DIR_LOCK = threading.Lock()
def dir_make(dirpath):
    if not os.path.isdir(dirpath):
        with DIR_LOCK:
            if not os.path.isdir(dirpath):
                try:
                    os.makedirs(dirpath)
                except:
                    pass
