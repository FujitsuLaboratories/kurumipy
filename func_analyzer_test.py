import unittest
import func_analyzer

g1 = 1
g2 = 2
g3 = 3

class TestFuncAnalyzer(unittest.TestCase):
    a1 = 1
    a2 = 2

    def test_load_globals(self):
        l1 = 1
        def get():
            t1 = g1
            t3 = g3
        self.assertEqual([("g1", 1), ("g3", 3)], func_analyzer.get_load_globals(get))
        def get_local():
            t1 = l1 # should not be reported because it is a free variable
        self.assertEqual([], func_analyzer.get_load_globals(get_local))
        def set():
            g2 = 22 # should not be reported because it is assignment
        self.assertEqual([], func_analyzer.get_load_globals(set))
        def builtin():
            t = sum(g1, g3) # sum should not be reported because it is a built-in function
        self.assertEqual([("g1", 1), ("g3", 3)], func_analyzer.get_load_globals(builtin))
        def attr():
            t1 = TestFuncAnalyzer.a1 # a1 should not be reported because it is an attribute name
        self.assertEqual([("TestFuncAnalyzer", TestFuncAnalyzer)], func_analyzer.get_load_globals(attr))

    def test_load_deref(self):
        l1 = 1
        l2 = 2
        l3 = 3
        def get():
            t1 = l1
            t3 = l3
        self.assertEqual([("l1", 1), ("l3", 3)], func_analyzer.get_load_deref(get))
        def set():
            l2 = 22 # should not be reported because it is assignment
        self.assertEqual([], func_analyzer.get_load_globals(set))
