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

    def add_flow(self, msg):
        try:
            d = match_to_dict(msg.match)
            f = { k:d[k] for k in ["nw_src", "nw_dst", "tp_src", "tp_dst", "nw_proto"] }
            flow = core.thesis_mcf.Flow(**f)
	    self.flows[flow] = 0
	    log.info("added flow: {0}".format(flow))
        except KeyError:
            pass

    def _handle_PacketIn(self, event):
        msg = of.ofp_flow_mod()
        msg.match = msg.match.from_packet(event.parsed)
        core.thesis_mcf.add_flow(msg)
	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	event.connection.send(msg)


def launch():
    core.registerNew(Multicommodity)
