#!/usr/bin/python

import subprocess
import signal
import sys
import importlib

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

from mcfpox.topos import pentagon
from mcfpox.objectives.shortest_path import objective
from mcfpox.test.objectives.test_shortest_path import pentagon_graph
from mcfpox.controller.lib import Flow, Hop


# Handle SIGINT
def cleanup(signal=None, frame=None):
    try:
	controller.kill()
    except Exception:
	print "failed to stop controller"
	pass

    try:
	net.stop()
    except Exception:
	print "failed to stop net"
	pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

# Remove any running controllers and/or mininets
clean = subprocess.call(['sudo', 'mn', '-c'])

# Precalculate switch forwarding rules
graph = pentagon_graph()

f1 = Flow(6, '10.0.0.1', '10.0.0.2', None, None)
f2 = Flow(6, '10.0.0.2', '10.0.0.1', None, None)
flows = {
    f1: [Hop(1,2), Hop(2,2), Hop(5,1)],
    f2: [Hop(5,2), Hop(2,1), Hop(1,1)]
}

rules = objective(graph, flows)

# Start POX, and pass through the pre-installed rules
objective = 'mcfpox.objectives.shortest_path'
#"""
controller = subprocess.Popen(['pox.py', 'log.level', '--CRITICAL', 
			       'mcfpox.controller.base', 
			       '--objective='+objective,
			       '--preinstall='+str(rules)])
#"""

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

h1.cmd('iperf -s -p 5001 &> h1.server.{0} &'.format(objective))
for i in [1,2,3,4,5]:
    print "{0} parallel threads starting".format(i)
    h2.cmd('iperf -c {0} -p 5001 -P {1} &'.format(str(h1.IP()), i))
    sleep(12)

print "iperf sessions probably complete"

# Don't exit the script until the controller is killed
controller.wait()
