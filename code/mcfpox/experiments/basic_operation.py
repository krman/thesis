#!/usr/bin/python

import subprocess
import signal
import sys
import importlib

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

import mcfpox.topos.pentagon as topo


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

# Start POX, running the mcfpox controller module
objective = 'mcfpox.objectives.shortest_path'
controller = subprocess.Popen(['pox.py', 'log.level', '--CRITICAL', 
			       'mcfpox.controller.base', 
			       '--objective='+objective])

# Start mininet with given topology
setLogLevel('output')
net = topo.create_net(controller=RemoteController)
c = net.addController('c0')
net.start()

# Wait for network to be discovered
sleep(15)

# Start flows/perform experiments
h1 = net.get('h1')
h2 = net.get('h2')
h1.cmd('ping -c1 ' + str(h2.IP()))
h2.cmd('ping -c1 ' + str(h1.IP()))

# Don't exit the script until the controller is killed
controller.wait()
