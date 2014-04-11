#!/usr/bin/python

"""
Route things! This is the base controller, which various modules plug into
"""

from pox.core import core
from pox.lib.util import dpidToStr
from pox.lib.recoco import Timer

import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
import pox.openflow.discovery as discovery
import pox.openflow.spanning_tree as spanning_tree

log = core.getLogger()


class Switch:
    def __init__(self, connection):
	self.connection = connection
	connection.addListeners(self)

	log.info("setting NO_FLOOD on {0} ports on new switch".format(len(connection.ports)))
	log.info("port {0}".format(connection.ports))

    def _handle_PacketIn(self, event):
	packet = event.parsed
	#log.info(vars(self.connection))
	log.info("new packet on switch {0}".format(self.connection))

	# flood...
        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        msg.data = event.ofp
        msg.in_port = event.port
        self.connection.send(msg)


class Controller:
    def __init__(self):
	core.openflow.addListeners(self)
	self.switches = []

    def _handle_ConnectionUp(self, event):
	Switch(event.connection)

    def _handle_PortStatus(self, event):
	log.info("port %s on switch %s has been modified" % (event.port, event.dpid))

    def _handle_FlowStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	log.info("flow stats: %s" % (stats))

    def _handle_PortStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	log.info("port stats: %s" % (stats))


def request_stats():
    for connection in core.openflow._connections.values():
	connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
	connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

def print_topology():
    log.info(core.openflow_discovery.adjacency)

def launch():
    #Timer(5, print_topology, recurring=True)
    #Timer(5, request_stats, recurring=True)
    for module in (discovery, spanning_tree): 
	module.launch()
    core.registerNew(Controller)
