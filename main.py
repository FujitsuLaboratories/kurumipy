import time
import memo_decorator

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


globalda = 120

@memo_decorator.memo
def memo_test(n):
    total = 0
    for num in range(1, 10000000):
        total = total + num
    return total

@memo_decorator.memo
def memo_test2(n, b, c):
    total = globalda
    for num in range(1, 10000000):
        total = total + num
    return total

class testArgs:
    def __init__(self, filename, sampling_rate, selected_filter):
        self.filename = filename
        self.sampling_rate = sampling_rate
        self.selected_filter = selected_filter

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

    test_args = testArgs('windsurfing-001.csv', 200, 'lowpass')
    sw.start()
    result = memo_test2(test_args.filename, 2, 1)
    print('[memo_test2] 1 回目: %f 秒' % sw.stop())
    print(str(result) + '\n')
