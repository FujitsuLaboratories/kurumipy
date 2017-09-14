import time
import pickle
import os
import func_analyzer

path = "sample.pickle"

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


# 計算結果をキャッシュするデコレータ
def cache(function):
    def _cache(*args,**kwargs):

        print(dir(function))
        print(function.__name__)
        print(function.__code__.co_names)
        print(func_analyzer.get_load_globals(function))
        print(*args)

        result = ''
        if os.path.isfile(path):
            with open(path, mode='rb') as f:
                result = pickle.load(f)
        else:
            with open(path, mode='wb') as f:
                result = function(n)
                pickle.dump(result, f)
        return result
    return _cache

globalda = 120

@cache
def memo_test(n):
    total = 0
    for num in range(1, 10000000):
        total = total + num
    return total

@cache
def memo_test2(n):
    total = globalda
    for num in range(1, 100):
        total = total + num
    return total


if __name__ == '__main__':
    sw = Stopwatch()

    sw.start()
    result = memo_test(2)
    print('1 回目: %f 秒' % sw.stop())
    print(result)

    sw.start()
    result = memo_test(2)
    print('2 回目: %f 秒' % sw.stop())
    print(result)

    result = memo_test2(10)


def test():
    taro = {'ta' : 'ababa'}
    print(taro['ta'])

    with open('sample.pickle', mode='wb') as f:
        pickle.dump(taro, f)

    with open('sample.pickle', mode='rb') as f:
        ba = pickle.load(f)
    
    print(ba['ta'])




# 計算結果をキャッシュするデコレータ
def old_cache(function):
    def _cache(n):
        if not hasattr(function, 'cache'):
            # キャッシュを入れる辞書が無ければ作る
            function.cache = {}
        result = function.cache.get(n)
        if not result:
            # 計算結果が無ければ改めて計算する
            result = function(n)
            # 計算結果をキャッシュする
            function.cache = {n: result}
        # 計算結果を返す
        return result
    return _cache