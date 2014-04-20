#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.openflow.discovery as discovery

import networkx as nx
from collections import namedtuple

log = core.getLogger()


class Multicommodity:
    _core_name = "thesis_mcf"
    Flow = namedtuple("Flow", ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"])

    def __init__(self):
	Timer(5, self._update_flows, recurring=True)
	self.flows = {}
	core.openflow.addListeners(self)

    def _update_flows(self):
	#log.info(core.openflow_discovery.adjacency)
	log.info(self.flows)

    def add_flow(self, flow):
	self.flows[flow] = 0


def launch():
    core.registerNew(Multicommodity)
