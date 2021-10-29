import tests.draw_graph_example as dge
import tests.test_definitions as d
import tests.test_unification as u
import unittest


dge.main()
suite = unittest.TestLoader().loadTestsFromModule(u)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromModule(d)
unittest.TextTestRunner(verbosity=2).run(suite)


