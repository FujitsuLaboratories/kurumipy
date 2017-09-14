import time
import pickle
import os
import hashlib
import func_analyzer

memo_dir = "memocache/"


# 計算時間を測るストップウォッチ
class Stopwatch(object):

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.processing_time = None

    # 計測開始
    def start(self):
        self.start_time = time.time()

    # 計測終了
    def stop(self):
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time
        return self.processing_time

# ファイル名に使用するハッシュ値(str型)を取得する
def get_hash(*args):
    hash_num = 0x0
    for data in args:
        print(data)
        hash_num = int(hashlib.md5(data.to_bytes(2, 'big')).hexdigest(), 16) ^ hash_num
    return str(hex(hash_num))

# メモ化用のデコレータ
def memo(function):
    def _memo(*args,**kwargs):

        # print(dir(function))
        # print(function.__globals__)
        # print(function.__code__.co_names)
        print(func_analyzer.get_load_globals(function))

        function_bytecode = function.__code__.co_code

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = get_hash(*args)

        env_path = memo_dir + function.__name__ + '-env.pickle'
        cache_path = memo_dir + function.__name__ + '-cache-' + cachefilename_hash + '.pickle'

        # メモ化用のキャッシュを置くディレクトリがなければ作成
        if not os.path.isdir(memo_dir):
            os.makedirs(memo_dir)

        cache_result = ''
        env_result = ''
        # envファイルがあればenvファイルに更新があるかチェックし、異なればenvファイル更新、キャッシュ更新
        if os.path.isfile(env_path):
            with open(env_path, mode='rb') as f:
                env_result = pickle.load(f)
            # envファイルが更新されていないければ
            if(env_result == function_bytecode):
                with open(cache_path, mode='rb') as f:
                    cache_result = pickle.load(f)
            else:
                with open(env_path, mode='wb') as f:
                    pickle.dump(function_bytecode, f)
                with open(cache_path, mode='wb') as f:
                    cache_result = function(*args,**kwargs)
                    pickle.dump(cache_result, f)
        # envファイルがなければenvファイルとキャッシュを作成
        else:
            with open(env_path, mode='wb') as f:
                pickle.dump(function_bytecode, f)
            with open(cache_path, mode='wb') as f:
                cache_result = function(*args,**kwargs)
                pickle.dump(cache_result, f)
        return cache_result
    return _memo

globalda = 120

@memo
def memo_test(n):
    total = 0
    for num in range(1, 10000000):
        total = total + num
    return total


@memo
def memo_test2(n, b, c):
    total = globalda
    for num in range(1, 10000000):
        total = total + num
    return total


if __name__ == '__main__':
    sw = Stopwatch()

    sw.start()
    result = memo_test(2)
    print('[memo_test] 1 回目: %f 秒' % sw.stop())
    print(result)

    sw.start()
    result = memo_test(2)
    print('[memo_test] 2 回目: %f 秒' % sw.stop())
    print(result)

    sw.start()
    result = memo_test2(10, 2, 1)
    print('[memo_test2] 1 回目: %f 秒' % sw.stop())
    print(result)
