#!/usr/bin/python

# modified from https://github.com/hip2b2/poxstuff/blob/master/flow_stats.py
# and https://github.com/CPqD/RouteFlow/blob/master/pox/pox/forwarding/l2_learning.py

"""
Monitor all traffic on the controller
"""

from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of

from pox.openflow.of_json import *
from pox.lib.recoco import Timer

log = core.getLogger()

class Switch:
    def __init__(self, connection):
	self.connection = connection
	connection.addListeners(self)
	
    def _handle_PacketIn(self, event):
	packet = event.parsed
	log.info(vars(self.connection))

	# flood...
	msg = of.ofp_packet_out()
	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	msg.data = event.ofp
	msg.in_port = event.port
	self.connection.send(msg)


class Controller:
    def __init__(self):
	core.openflow.addListeners(self)

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

def launch():
    core.registerNew(Controller)
    #Timer(5, request_stats, recurring=True)
