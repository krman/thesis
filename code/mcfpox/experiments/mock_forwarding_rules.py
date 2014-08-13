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
import matplotlib.pyplot as plt


@run_experiment
def experiment():
    # Precalculate switch forwarding rules
    graph = pentagon_graph()
    
    #f1 = Flow(6, '10.0.0.1', '10.0.0.2', None, None)
    #f2 = Flow(6, '10.0.0.2', '10.0.0.1', None, None)
    f1 = Flow(17, '10.0.0.1', '10.0.0.2', None, None)
    f2 = Flow(17, '10.0.0.2', '10.0.0.1', None, None)
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
    
    received = []
    import json
    h1.cmd('iperf3 -s -p 5001 &> h1.server &')
    flows = [1,3,5,7,9]
    for i in flows:
	print "{0} parallel threads starting".format(i)
	h2.cmd('iperf3 -c {0} -p 5001 -b 4m -t 10 -P {1} -J &> h2.client.{1} &'.format(str(h1.IP()), i))
	sleep(15)
	f = open('h2.client.{0}'.format(i))
	j = json.load(f)
	print "Sent:", j['end']['sum_sent']['bits_per_second'], "/", 
	print "Received:", j['end']['sum_received']['bits_per_second']
	received.append(j['end']['sum_received']['bits_per_second'])
	#print "Sent:", j['end']['sum_sent']
	#print "Received:", j['end']['sum_received']
	#print "UDP bandwidth:", j['end']['sum']['bits_per_second'], "bps"
	#received.append(j['end']['sum']['bits_per_second'])

    
    sleep(2)
    print "iperf sessions probably complete"
    y = [i/1e6 for i in [0]+received]
    print y
    plt.plot([0]+flows, y, 'g-o')
    plt.plot(range(10), [20]*10, 'k:')
    plt.axis([0,9,0,30])
    plt.xlabel('Size of flow (Mbps)')
    plt.ylabel('Measured bandwidth between h1 and h2')
    plt.title('Single TCP flows')
    plt.show()
    print flows, received
    controller.kill()


if __name__ == '__main__':
    experiment()
