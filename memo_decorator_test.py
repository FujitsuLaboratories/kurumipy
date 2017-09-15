import unittest
import memo_decorator

g1 = 1

class DecoratedCounter():
    def __init__(self):
        self.v = 0

    @memo_decorator.memo
    def count(self, n):
        self.v += 1
        return (self.v, n, g1)

class TestMemoDecorator(unittest.TestCase):
    def test_global_variable_changes(self):
        global g1
        counter = DecoratedCounter()
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
