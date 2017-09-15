import pickle

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
