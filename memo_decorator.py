import time
import os
import shutil
import file_operation as fo
import func_analyzer

memo_dir = "memocache/"


# 計算時間を測るストップウォッチ（下記URLのコードのコピペ）
# http://momijiame.tumblr.com/post/62619539929/python-%E3%81%A7%E3%83%87%E3%82%B3%E3%83%AC%E3%83%BC%E3%82%BF%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E9%96%A2%E6%95%B0%E3%81%AE%E8%A8%88%E7%AE%97%E7%B5%90%E6%9E%9C%E3%82%92%E3%82%AD%E3%83%A3%E3%83%83%E3%82%B7%E3%83%A5%E3%81%99%E3%82%8B
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
        print(func_analyzer.get_load_globals(function))

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = fo.get_hash(*args)
        # キャッシュファイル関係のパス名生成
        func_dir = memo_dir + function.__name__ + '/'
        env_path = func_dir + 'env.pickle'
        cache_path = func_dir + 'cache-' + cachefilename_hash + '.pickle'
        # メモ化用のキャッシュを置くディレクトリがなければ作成
        if not os.path.isdir(memo_dir):
            os.makedirs(memo_dir)

        func_env = {}
        # 関数のコードのバイトコードを取得
        func_env['bytecode'] = function.__code__.co_code
        # 関数で使われているグローバル変数とレキシカル変数を取得
        func_env['globals'] = func_analyzer.get_load_globals(function)
        func_env['frees'] = func_analyzer.get_load_deref(function)

        cache_result = ''
        # envファイルがあればenvファイルに更新があるかチェックし、異なればenvファイル更新、該当関数内のenvとキャッシュファイルを全削除、キャッシュ新規作成
        if os.path.isfile(env_path):
            env_result = fo.file_read(env_path)
            # envファイルと差異がなく、かつ、キャッシュファイルがあればキャッシュを読み込み
            if(env_result == func_env):
                if os.path.isfile(cache_path):
                    cache_result = fo.file_read(cache_path)
                # キャッシュファイルがなければ、該当関数を実行して、キャッシュを新規作成
                else:
                    cache_result = function(*args,**kwargs)
                    fo.file_write(cache_path, cache_result)
            # envファイルと差異があれば、該当関数内のenvとキャッシュファイルを全削除し、envファイルを新規作成、該当関数を実行して、キャッシュを新規作成
            else:
                # 関数フォルダを削除
                shutil.rmtree(func_dir)
                os.makedirs(func_dir)
                fo.file_write(env_path, func_env)
                cache_result = function(*args,**kwargs)
                fo.file_write(cache_path, cache_result)
        # envファイルがなければenvファイルとキャッシュを作成
        else:
            if not os.path.isdir(func_dir):
                os.makedirs(func_dir)
            fo.file_write(env_path, func_env)
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
    print(str(result) + '\n')

    sw.start()
    result = memo_test(2)
    print('[memo_test] 2 回目: %f 秒' % sw.stop())
    print(str(result) + '\n')

    sw.start()
    result = memo_test2(10, 2, 1)
    print('[memo_test2] 1 回目: %f 秒' % sw.stop())
    print(str(result) + '\n')
