#!/usr/bin/python

import subprocess
import signal
import sys
import importlib

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

topology = 'diamond'
objective = 'shortest_path'
results = 'results'

topo = importlib.import_module('topos.' + topology)

def cleanup(signal=None, frame=None):
    try:
	controller.kill()
	net.stop()
    except Exception:
	pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

clean = subprocess.Popen(['sudo', 'mn', '-c'])
clean.wait()
controller = subprocess.Popen(['../controllers/pox_base.sh',
			       '--objective='+objective])

setLogLevel('output')
net = topo.create_net(controller=RemoteController)
c = net.addController('c0')

net.start()

sleep(15)
h1 = net.get('h1')
h2 = net.get('h2')
h1.cmd('ping -c1 ' + str(h2.IP()))
h2.cmd('ping -c1 ' + str(h1.IP()))

sleep(10)
CLI(net)
net.stop()

cleanup()
