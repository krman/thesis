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

TOPOLOGY = 'fat_tree'
OBJECTIVE = 'shortest_path'
RESULTS = 'results'

sys.path.append(os.path.abspath('/home/imz/src/pox'))
topo = importlib.import_module('topos.' + TOPOLOGY)
obj = importlib.import_module('objectives.' + OBJECTIVE)


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")

# (src,dst):kbps
matrix = None

# (src,dst):(p1,p2)
links = {('h1','s1'):(1,1),
	 ('s1','s2'):(2,1),
	 ('s1','s4'):(3,1),
	 ('s2','s3'):(2,1),
	 ('s3','s5'):(2,2),
	 ('s4','s5'):(2,3),
	 ('s5','h2'):(1,1)}

# expected generated rules
expected = {Flow(nw_proto=None, nw_src='10.0.0.1', nw_dst='10.0.0.2', tp_src=None, tp_dst=None): [Hop(dpid='h1', port={'port': 1}), Hop(dpid='s1', port={'port': 3}), Hop(dpid='s4', port={'port': 2}), Hop(dpid='s5', port={'port': 1})]}

class TestTopology:

    Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
    Hop = namedtuple("Hop", "dpid port")
    Port = namedtuple("Port", "port_num mac_addr")

    def __init__(self):
	UG = nx.Graph()
	UG.add_edges_from(links.keys())
	G = nx.DiGraph(UG)

	for a,b in G.edges():
	    try:
		G.edge[a][b]['port'] = links[(a,b)][0]
	    except KeyError:
		G.edge[a][b]['port'] = links[(b,a)][1]

	G.node['h1']['ip'] = '10.0.0.1'
	G.node['h2']['ip'] = '10.0.0.2'

	self.graph = G



print "k,run,obj time"
for k in [2,4,6,8,10]:
    for i in range(5):
	print "{0}, {1},".format(k,i),

	net = TestTopology()
	flows = {Flow(nw_src='10.0.0.1', nw_dst='10.0.0.2',nw_proto=None,tp_src=None,tp_dst=None):5}

	start = datetime.now()
	rules = obj.objective(net, flows)
	end = datetime.now()
	assert rules == expected, "incorrect result"
	print end-start
