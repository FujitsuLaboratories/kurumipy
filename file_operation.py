import pickle
import hashlib

memo_dir = "memocache/"

# ファイル名に使用するハッシュ値(str型)を取得する
def get_hash(*args):
    hash_num = 0x0
    for data in args:
        print(data)
        hash_num = int(hashlib.md5(data.to_bytes(2, 'big')).hexdigest(), 16) ^ hash_num
    return str(hex(hash_num))

# ファイルにデータをシリアライズして保存
def file_write(path, data):
    with open(path, mode='wb') as f:
        pickle.dump(data, f)
 
# ファイルからデータをデシリアライズして読み込み、返す
def file_read(path):
    with open(path, mode='rb') as f:
        result = pickle.load(f)
    return result 
