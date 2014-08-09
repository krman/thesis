#!/usr/bin/python

from time import sleep

from mcfpox.topos import pentagon
from mcfpox.objectives.shortest_path import objective
from mcfpox.test.objectives.test_shortest_path import pentagon_graph
from mcfpox.controller.lib import Flow, Hop

from boilerplate import run_experiment, start_pox


@run_experiment
def experiment():
    # Precalculate switch forwarding rules
    graph = pentagon_graph()
    
    f1 = Flow(6, '10.0.0.1', '10.0.0.2', None, None)
    f2 = Flow(6, '10.0.0.2', '10.0.0.1', None, None)
    rules = {
	f1: [Hop(1,2), Hop(2,2), Hop(5,1)],
	#f2: [Hop(5,3), Hop(4,1), Hop(3,1), Hop(1,1)] # different paths
	f2: [Hop(5,2), Hop(2,1), Hop(1,1)] # same paths
    }
    
    # Start POX, and pass through the pre-installed rules
    objective = 'mcfpox.objectives.shortest_path'
    controller = start_pox(objective=objective, rules=rules)
    
    controller.wait()
    controller.kill()


if __name__ == '__main__':
    experiment()
