#!/usr/bin/python

import subprocess
import signal
import sys
import importlib

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

TOPOLOGY = 'fat_tree'
OBJECTIVE = 'max_spare_capacity'
RESULTS = 'results'

topo = importlib.import_module('topos.' + TOPOLOGY)

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
			       '--objective='+OBJECTIVE])

setLogLevel('output')
net = topo.create_net(controller=RemoteController)
c = net.addController('c0')

net.start()
bw = net.iperf()

f = open(RESULTS, "ab")
f.write("{0},{1},{2},{3}\n".format(TOPOLOGY, OBJECTIVE, bw[0], bw[1]))
f.close()

sleep(50)
CLI(net)
net.stop()

cleanup()
