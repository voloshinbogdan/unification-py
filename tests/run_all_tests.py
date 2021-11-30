import unittest

import tests.draw_graph_example as dge
dge.main()

import tests.test_unification as u
suite = unittest.TestLoader().loadTestsFromModule(u)
unittest.TextTestRunner(verbosity=2).run(suite)

import tests.test_definitions as d
suite = unittest.TestLoader().loadTestsFromModule(d)
unittest.TextTestRunner(verbosity=2).run(suite)


