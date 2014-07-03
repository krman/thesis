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
OBJECTIVE = 'capacity_spare_max'
RESULTS = 'results'

sys.path.append(os.path.abspath('/home/imz/src/pox'))
topo = importlib.import_module('topos.' + TOPOLOGY)
obj = importlib.import_module('objectives.' + OBJECTIVE)


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")

# (src,dst):(p1,p2)
links = {('h1','s1'):(1,1),
	 ('s1','s2'):(2,1),
	 ('s1','s3'):(3,1),
	 ('s2','s4'):(2,2),
	 ('s3','s4'):(2,3),
	 ('s4','h2'):(1,1)}

# expected generated rules
expected = {Flow(nw_proto=None, nw_src='10.0.0.1', nw_dst='10.0.0.2', tp_src=None, tp_dst=None): [Hop(dpid='s1', port=3), Hop(dpid='s3', port=2)]}


class TestTopology:

    Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
    Hop = namedtuple("Hop", "dpid port")
    Port = namedtuple("Port", "port_num mac_addr")

    def __init__(self, k=4):
	print "graph with k=",k
	self.graph = fat_tree_graph(k=k)


print "k,run,obj time"
#for k in [2,4,6,8,10]:
    #for i in range(5):
for i in range(1):
	k = 4
	print "{0}, {1},".format(k,i),

	net = TestTopology(k=k)
	flows = {Flow(nw_src='10.1.3.1', nw_dst='10.3.2.1',nw_proto=None,tp_src=None,tp_dst=None):3}

	start = datetime.now()
	rules = obj.objective(net, flows)
	end = datetime.now()
	#assert rules == expected, "incorrect result"
	print end-start
