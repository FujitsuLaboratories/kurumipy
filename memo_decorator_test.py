import unittest
import memoization.memo_decorator as memo_decorator
import time
from functools import reduce
import threading

def get_stats(f):
    return (f.calls, f.hits, f.invalidates)

g1 = 1

def gf(x):
    return x

class GlobalClass():
    pass

class TestMemoDecorator(unittest.TestCase):
    def test_global_variable_changes(self):
        global g1
        @memo_decorator.memo
        def f(i):
            return (i, g1)
        # to invalidates cache
        g1 = time.time()
        f(0)
        initial_invalidates = f.invalidates

        g1 = 1
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (2, 0, initial_invalidates + 1))
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (3, 1, initial_invalidates + 1))
        self.assertEqual(f(2), (2, 1))
        self.assertEqual(get_stats(f), (4, 1, initial_invalidates + 1))
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (5, 2, initial_invalidates + 1))
        g1 = 2
        self.assertEqual(f(1), (1, 2))
        self.assertEqual(get_stats(f), (6, 2, initial_invalidates + 2))
        g1 = 1
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (7, 2, initial_invalidates + 3))

    def test_free_variable_changes(self):
        free = 1
        @memo_decorator.memo
        def f(i):
            return (i, free)

        # to invalidates cache
        free = time.time()
        f(0)
        initial_invalidates = f.invalidates

        free = 1
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (2, 0, initial_invalidates + 1))
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (3, 1, initial_invalidates + 1))
        self.assertEqual(f(2), (2, 1))
        self.assertEqual(get_stats(f), (4, 1, initial_invalidates + 1))
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (5, 2, initial_invalidates + 1))
        free = 2
        self.assertEqual(f(1), (1, 2))
        self.assertEqual(get_stats(f), (6, 2, initial_invalidates + 2))
        free = 1
        self.assertEqual(f(1), (1, 1))
        self.assertEqual(get_stats(f), (7, 2, initial_invalidates + 3))

    def test_same_method_of_different_instances(self):
        free = 0
        class C:
            @memo_decorator.memo
            def f(self):
                return free
        c1, c2 = C(), C()

        # to invalidate cache
        free = time.time()
        c1.f()
        initial_invalidates = c1.f.invalidates

        c1.f()
        self.assertEqual(get_stats(c1.f), (2, 1, initial_invalidates))
        c2.f()
        self.assertEqual(get_stats(c2.f), (3, 1, initial_invalidates))
        c1.f()
        self.assertEqual(get_stats(c1.f), (4, 2, initial_invalidates))

    def test_equality_of_different_string_instances(self):
        free = time.time()
        @memo_decorator.memo
        def strlen(s):
            dummy = free
            return len(s)

        strlen("")
        initial_invalidates = strlen.invalidates

        strlen("aaa")
        self.assertEqual(get_stats(strlen), (2, 0, initial_invalidates))
        strlen("aaa")
        self.assertEqual(get_stats(strlen), (3, 1, initial_invalidates))
        strlen("".join(["a", "aa"]))
        self.assertEqual(get_stats(strlen), (4, 2, initial_invalidates))
        strlen("bbb")
        self.assertEqual(get_stats(strlen), (5, 2, initial_invalidates))

    def test_equality_of_different_tuple_instances(self):
        free = time.time()
        @memo_decorator.memo
        def tuple_hash(t):
            dummy = free
            return hash(t)

        tuple_hash(())
        initial_invalidates = tuple_hash.invalidates

        tuple_hash((1, "aaa"))
        self.assertEqual(get_stats(tuple_hash), (2, 0, initial_invalidates))
        tuple_hash((1, "".join(["a", "aa"])))
        self.assertEqual(get_stats(tuple_hash), (3, 1, initial_invalidates))
        tuple_hash((2, "aaa"))
        self.assertEqual(get_stats(tuple_hash), (4, 1, initial_invalidates))
        tuple_hash((2, "bbb"))
        self.assertEqual(get_stats(tuple_hash), (5, 1, initial_invalidates))
        tuple_hash((1, "aaa"))
        self.assertEqual(get_stats(tuple_hash), (6, 2, initial_invalidates))

    def test_deffensive_against_collision(self):
        @memo_decorator.memo
        def sum(i, j):
            return i + j
        self.assertEqual(sum(0, 0), 0)
        self.assertEqual(sum(0, 1), 1)
        self.assertEqual(sum(1, 1), 2)

    def test_redefining_function(self):
        # same constants but different byte code
        if True:
            @memo_decorator.memo
            def f(n):
                return n+100
            self.assertEqual(101, f(1))
            self.assertEqual(102, f(2))
        if True:
            @memo_decorator.memo
            def f(n):
                return n-100
            self.assertEqual(-99, f(1))
            self.assertEqual(-98, f(2))
        # same byte code but different constants
        if True:
            @memo_decorator.memo
            def g(n):
                return n+10
            self.assertEqual(11, g(1))
            self.assertEqual(12, g(2))
        if True:
            @memo_decorator.memo
            def g(n):
                return n+100
            self.assertEqual(101, g(1))
            self.assertEqual(102, g(2))

    def test_list_comprehension_in_function(self):
        @memo_decorator.memo
        def f(n):
            l = [i for i in range(0, n+1)]
            return sum(l)
        self.assertEqual(55, f(10))

    def test_recursive_function(self):
        free = time.time()
        @memo_decorator.memo
        def f(n):
            dummy = free
            if n <= 0:
                return 0
            return n + f(n-1)
        f(0)
        initial_invalidates = f.invalidates
        self.assertEqual(55, f(10))
        self.assertEqual((1+10+1, 1, initial_invalidates), get_stats(f))
        self.assertEqual(15, f(5))
        self.assertEqual((1+10+1+1, 2, initial_invalidates), get_stats(f))

    def test_tail_recursive_function(self):
        free = time.time()
        @memo_decorator.memo
        def f(n, s=0):
            dummy = free
            if n <= 0:
                return s
            return f(n-1, s+n)
        f(0)
        initial_invalidates = f.invalidates
        self.assertEqual(55, f(10))
        self.assertEqual((1+10+1, 0, initial_invalidates), get_stats(f))
        self.assertEqual(15, f(5))
        self.assertEqual((1+10+1+5+1, 0, initial_invalidates), get_stats(f))

    def test_mutual_recursive_function(self):
        @memo_decorator.memo
        def f(n):
            if n > 0:
                return 1+g(n-1)
            else:
                return 0
        @memo_decorator.memo
        def g(n):
            if n > 0:
                return 1+f(n-1)
            else:
                return 0
        f(0)
        g(0)
        initial_invalidates_f = f.invalidates
        initial_invalidates_g = g.invalidates
        self.assertEqual(3, f(3))
        self.assertEqual((1+2, 0, initial_invalidates_f), get_stats(f))
        self.assertEqual((1+2, 1, initial_invalidates_g), get_stats(g))

    def test_global_function_usage(self):
        @memo_decorator.memo
        def f(x):
            return gf(x)
        self.assertEqual(1, f(1))
        self.assertEqual(2, f(2))

    def test_reduce_usage(self):
        @memo_decorator.memo
        def f(*args):
            def add(x, y):
                return x+y
            return reduce(add, args)
        self.assertEqual(6, f(1, 2, 3))

    def test_class_usage(self):
        @memo_decorator.memo
        def f(s):
            return GlobalClass.__name__ + s
        self.assertEqual("GlobalClass-1", f("-1"))

    def test_exception_handling(self):
        @memo_decorator.memo
        def f(n):
            if n == 0:
                raise ValueError()
            return f(n-1)
        with self.assertRaises(ValueError):
            f(1)
        self.assertEqual(2, f.calls)
        with self.assertRaises(ValueError):
            f(2)
        self.assertEqual(2+3, f.calls)
        # TODO should not know implementation details
        self.assertEqual(0, f.lock.thread_id)
        self.assertEqual(0, f.lock.recursion_count)

    def test_multithread_safety(self):
        free = 0
        @memo_decorator.memo
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
        callers = [Caller(), Caller()]
        for t in callers:
            t.start()
        for i in range(10):
            time.sleep(0.1)
            free = i
        for t in callers:
            t.stop()
            t.join()
        for t in callers:
            self.assertIsNone(t.lastError)

    @unittest.skip("No support for lock ordering")
    def test_multithread_mutual_recursive(self):
        @memo_decorator.memo
        def f(n):
            if n > 0:
                return 1+g(n-1)
            else:
                return 0
        @memo_decorator.memo
        def g(n):
            if n > 0:
                return 1+f(n-1)
            else:
                return 0
        f(0)
        g(0)
        initial_invalidates_f = f.invalidates
        initial_invalidates_g = g.invalidates
        class Caller(threading.Thread):
            def __init__(self, entry):
                threading.Thread.__init__(self)
                self.entry = entry
                self.stopRequested = False
                self.lastError = None
            def run(self):
                i = 0
                while not self.stopRequested:
                    try:
                        self.entry(2 * i)
                    except Exception as e:
                        self.lastError = e
                    i += 1
            def stop(self):
                self.stopRequested = True
        callers = [Caller(f), Caller(g)]
        for t in callers:
            t.start()
        time.sleep(1)
        for t in callers:
            t.stop()
            t.join()
        for t in callers:
            self.assertIsNone(t.lastError)
