#!/usr/bin/python

import subprocess
import signal
import sys
import os
import importlib

from time import sleep
from datetime import datetime
from collections import namedtuple

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

import networkx as nx
from fat_tree_graph import fat_tree_graph


TOPOLOGY = 'fat_tree'
OBJECTIVE = 'shortest_path'
RESULTS = 'results'

sys.path.append(os.path.abspath('/home/imz/src/pox'))
topo = importlib.import_module('topos.' + TOPOLOGY)
obj = importlib.import_module('objectives.' + OBJECTIVE)


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")

class TestTopology:
    def __init__(self, k=4):
	self.graph = fat_tree_graph(k=k)


print "max path len,k,num paths,num switches,obj time"
for c in [10]:
    for k in [2,4,6,8,10,50,100]:
	print "{0}, {1},".format(c,k),

	net = TestTopology(k=k)

	nw_src = '10.{0}.{1}.2'.format(0,k/2)
	nw_dst = '10.{0}.{1}.2'.format(k-1,k-1)
	flows = {Flow(nw_src=nw_src, nw_dst=nw_dst,nw_proto=None,tp_src=None,tp_dst=None):3}

	h1 = 'h{0},{1}.2'.format(0,k/2)
	h2 = 'h{0},{1}.2'.format(k-1,k-1)
	#paths = nx.all_simple_paths(net.graph, h1, h2)
	#print "{0}, {1},".format(len(list(paths)), len(net.graph.nodes())),

	start = datetime.now()
	rules = obj.objective(net, flows)
	end = datetime.now()
	print end-start
