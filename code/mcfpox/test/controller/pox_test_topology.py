#!/usr/bin/python

"""
Test controller for testing topology
"""

from pox.core import core
from pox.lib.recoco import Timer

import pox.openflow.discovery as discovery
import pox.openflow.spanning_tree as spanning_tree

import mcfpox.controller.topology as topology

log = core.getLogger()


class Controller:
    _core_name = "mcfpox_test_topology"

    def __init__(self, filename):
	Timer(15, self.write_topology)

	self.net = core.thesis_topo
	self.filename = filename

	core.openflow.addListeners(self)
	core.addListeners(self)

    def write_topology(self):
	self.net.refresh_network()
	edges = self.net.graph.edges()
	edges.sort()

	with open(self.filename, 'w') as f:
	    for a,b in edges:
		line = "{0}-{1}: {2}\n".format(a,b,self.net.graph.edge[a][b])
		f.write(line)


def launch(filename='results'):
    discovery.launch()
    spanning_tree.launch(no_flood=True, hold_down=True)
    topology.launch()

    core.registerNew(Controller, filename=filename)
