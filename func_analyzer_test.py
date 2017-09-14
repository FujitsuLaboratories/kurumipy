import unittest
import func_analyzer

g1 = 1
g2 = 2
g3 = 3

class TestFuncAnalyzer(unittest.TestCase):
    a1 = 1
    a2 = 2

    def test_load_globals(self):
        def get():
            t1 = g1
            t3 = g3
        self.assertEqual([("g1", 1), ("g3", 3)], func_analyzer.get_load_globals(get))
        def set():
            g2 = 22 # should not reported because it is assignment
        self.assertEqual([], func_analyzer.get_load_globals(set))
        def builtin():
            t = sum(g1, g3) # sum should not be reported because it is a built-in function
        self.assertEqual([("g1", 1), ("g3", 3)], func_analyzer.get_load_globals(builtin))
        def attr():
            t1 = TestFuncAnalyzer.a1 # a1 should not be reported because it is an attribute name
        self.assertEqual([("TestFuncAnalyzer", TestFuncAnalyzer)], func_analyzer.get_load_globals(attr))
