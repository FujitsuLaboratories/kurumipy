import unittest
import memo_decorator

g1 = 1

class DecoratedCounter():
    def __init__(self, name):
        self.name = name
        self.v = 0

    @memo_decorator.memo
    def count(self, n):
        self.v += 1
        return (self.v, n, g1)

    def __hash__(self):
        # Does not include v on purpse
        # Use hash of name because self instance may share same address
        return hash(self.name)

class PureFunctions():
    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = 0

    @memo_decorator.memo
    def string_length(self, str):
        self.calls += 1
        return len(str)

    @memo_decorator.memo
    def tuple_hash(self, tuple):
        self.calls += 1
        return hash(tuple)

class TestMemoDecorator(unittest.TestCase):
    def test_global_variable_changes(self):
        global g1
        counter = DecoratedCounter("test_global_variable_changes")
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        r = counter.count(2)
        self.assertEqual(r, (2, 2, 1))
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        g1 = 2
        r = counter.count(1)
        self.assertEqual(r, (3, 1, 2))
        r = counter.count(2)
        self.assertEqual(r, (4, 2, 2))
        g1 = 1
        r = counter.count(1)
        self.assertEqual(r, (5, 1, 1))

    def test_free_variable_changes(self):
        free = 1
        class DecoratedCounterFree():
            def __init__(self):
                self.v = 0
            @memo_decorator.memo
            def count(self, n):
                self.v += 1
                return (self.v, n , free)
            # Do not implement __hash__ on purpse
        counter = DecoratedCounterFree()
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        r = counter.count(2)
        self.assertEqual(r, (2, 2, 1))
        r = counter.count(1)
        self.assertEqual(r, (1, 1, 1))
        free = 2
        r = counter.count(1)
        self.assertEqual(r, (3, 1, 2))
        r = counter.count(2)
        self.assertEqual(r, (4, 2, 2))
        r = counter.count(1)
        self.assertEqual(r, (3, 1, 2))

    def test_same_method_of_different_instances(self):
        c1, c2 = DecoratedCounter("test_same_method_of_different_instances 1"), DecoratedCounter("test_same_method_of_different_instances 2")
        r = c1.count(1)
        self.assertEqual(r, (1, 1, 1))
        r = c1.count(2)
        self.assertEqual(r, (2, 2, 1))
        r = c2.count(2)
        self.assertEqual(r, (1, 2, 1))
        r = c1.count(1)
        self.assertEqual(r, (1, 1, 1))

    def test_equality_of_different_objects(self):
        p = PureFunctions()
        self.assertEqual(p.calls, 0)
        p.string_length("aaa")
        p.string_length("aaa")
        p.string_length("".join(["a", "aa"]))
        p.string_length("bbb")
        self.assertEqual(p.calls, 2)

        p.reset()
        self.assertEqual(p.calls, 0)
        p.tuple_hash((1, "aaa"))
        p.tuple_hash((1, "".join(["a", "aa"])))
        self.assertEqual(p.calls, 1)
        p.tuple_hash((2, "aaa"))
        self.assertEqual(p.calls, 2)
        p.tuple_hash((2, "bbb"))
        self.assertEqual(p.calls, 3)
        p.tuple_hash((1, "aaa"))
        self.assertEqual(p.calls, 3)

    def test_deffensive_against_collision(self):
        @memo_decorator.memo
        def sum(i, j):
            return i + j
        self.assertEqual(sum(0, 0), 0)
        self.assertEqual(sum(0, 1), 1)
        self.assertEqual(sum(1, 1), 2)
