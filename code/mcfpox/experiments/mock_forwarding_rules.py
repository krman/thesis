#!/usr/bin/python

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

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
    
    # Start mininet with given topology
    setLogLevel('output')
    net = pentagon.create_net(controller=RemoteController)
    net.start()
    
    # Wait for network to be discovered
    sleep(15)
    
    # Start flows/perform experiments
    print "Starting flows..."
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    h1.cmd('iperf -s -p 5001 &> h1.server.{0}.same_paths &'.format(objective))
    for i in [1]:
	print "{0} parallel threads starting".format(i)
	h2.cmd('iperf -c {0} -p 5001 -t 10 -P {1} &> h2.client.same_paths.{1} &'.format(str(h1.IP()), i))
	sleep(12)
    
    print "iperf sessions probably complete"
    controller.kill()


if __name__ == '__main__':
    experiment()
