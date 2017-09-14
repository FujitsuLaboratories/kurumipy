import time
import os
import file_operation as fo
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

# メモ化用のデコレータ
def memo(function):
    def _memo(*args,**kwargs):

        # print(dir(function))
        # print(function.__globals__)
        # print(function.__code__.co_names)
        print(func_analyzer.get_load_globals(function))

        function_bytecode = function.__code__.co_code

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = fo.get_hash(*args)

        func_dir = memo_dir + function.__name__ + '/'
        env_path = func_dir + 'env.pickle'
        cache_path = func_dir + 'cache-' + cachefilename_hash + '.pickle'

        # メモ化用のキャッシュを置くディレクトリがなければ作成
        if not os.path.isdir(memo_dir):
            os.makedirs(memo_dir)
        if not os.path.isdir(func_dir):
            os.makedirs(func_dir)

        cache_result = ''
        env_result = ''
        # envファイルがあればenvファイルに更新があるかチェックし、異なればenvファイル更新、キャッシュ更新
        if os.path.isfile(env_path):
            env_result = fo.file_read(env_path)
            # envファイルと差異がなく、かつ、キャッシュファイルがあればキャッシュを読み込み
            if(env_result == function_bytecode):
                if os.path.isfile(cache_path):
                    cache_result = fo.file_read(cache_path)
                # キャッシュファイルがなければ、該当関数実行して、キャッシュを新規作成
                else:
                    cache_result = function(*args,**kwargs)
                    fo.file_write(cache_path, cache_result)
            # envファイルと差異があれば、envファイルを更新、該当関数実行して、キャッシュを新規作成 or 更新
            else:
                fo.file_write(env_path, function_bytecode)
                cache_result = function(*args,**kwargs)
                fo.file_write(cache_path, cache_result)
        # envファイルがなければenvファイルとキャッシュを作成
        else:
            fo.file_write(env_path, function_bytecode)
            cache_result = function(*args,**kwargs)
            fo.file_write(cache_path, cache_result)
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
