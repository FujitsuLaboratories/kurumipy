import time
from contextlib import contextmanager
from memoization.memo_decorator import memo
import threading

@contextmanager
def stopwatch(format_str):
    """Print execution time. Argument format_str must have '%f' in it."""
    start_time = time.time()
    yield
    end_time = time.time()
    print(format_str % (end_time - start_time))

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

free = 0
@memo
def f(i):
    return free + i
class Caller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopRequested = False
        self.lastError = None
    def run(self):
        i = 0
        while not self.stopRequested:
            try:
                f(i)
            except Exception as e:
                self.lastError = e
            i += 1
            if i > 100:
                i = 0
    def stop(self):
        self.stopRequested = True

@memo
def recursion(n):
    if n <= 0:
        return 0
    return n + recursion(n-1)

if __name__ == '__main__':
    with stopwatch('[memo_test] 1st: %f sec'):
        result = memo_test(2)
        print(result)

    with stopwatch('[memo_test] 2nd: %f sec'):
        result = memo_test(2)
        print(result)

    with stopwatch('[memo_test2] 1st: %f sec'):
        result = memo_test2(1, 2, 3)
        print(result)

    # Test multiple threads in one process
    callers = [Caller(), Caller(), Caller()]
    for t in callers:
        t.start()
    for i in range(10):
        time.sleep(0.1)
        free = i
    for t in callers:
        t.stop()
        t.join()
    for t in callers:
       print(t.lastError)

    # Test recursive function
    recursion(2)
