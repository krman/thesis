#!/usr/bin/python

import subprocess
import signal
import sys
import os
import importlib

from time import sleep
from datetime import datetime

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

import networkx as nx

TOPOLOGY = 'fat_tree'
OBJECTIVE = 'max_spare_capacity'
RESULTS = 'results'

def cleanup(signal=None, frame=None):
    try:
	net.stop()
    except Exception:
	pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def mnc():
    clean = subprocess.Popen(['sudo', 'mn', '-c'])
    clean.wait()

topo = importlib.import_module('topos.' + TOPOLOGY)
obj = importlib.import_module('objectives.' + OBJECTIVE)

print "k,run,setup time"
for k in [2,4,6,8,10]:
    print "k={0}: {1} switches, {2} hosts".format(k,5*k**2/4,k**3/4)
    for i in range(3):
	print "{}, {},".format(k, i),
	mnc()
	start = datetime.now()
	net = topo.create_net(controller=RemoteController, k=k)
	end = datetime.now()
	net.stop()
	print "{},".format(end-start),
	#net = nx.Graph()
	#flows = {}
	#print obj.objective(net, flows),
	print

cleanup()
