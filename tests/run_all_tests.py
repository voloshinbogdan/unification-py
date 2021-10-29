import tests.draw_graph_example as dge
import tests.test_definitions as d
import tests.test_unification as u
import unittest


dge.main()
u.main()
suite = unittest.TestLoader().loadTestsFromModule(d)
unittest.TextTestRunner(verbosity=2).run(suite)


