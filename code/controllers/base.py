#!/usr/bin/python

"""
Route things! This is the base controller, which various modules plug into
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.recoco import Timer
from pox.openflow.of_json import *
from collections import namedtuple

import pox.openflow.discovery as discovery
import pox.openflow.spanning_tree as spanning_tree
import pox.thesis.statistics as statistics
import pox.thesis.multicommodity as multicommodity

log = core.getLogger()


class Switch:
    def __init__(self, connection):
	self.connection = connection
	connection.addListeners(self)

	log.info("setting NO_FLOOD on {0} ports on new switch".format(len(connection.ports)))
	log.info("port {0}".format(connection.ports))

	# flood arp
	msg = of.ofp_flow_mod()
	msg.match.dl_type = pkt.ethernet.ARP_TYPE
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	self.connection.send(msg)

    def _handle_PacketIn(self, event):
	msg = of.ofp_flow_mod()
	msg.match = msg.match.from_packet(event.parsed)
	d = match_to_dict(msg.match)

	try:
	    f = { k:d[k] for k in ["nw_src", "nw_dst", "tp_src", "tp_dst", "nw_proto"] }
	    flow = core.thesis_mcf.Flow(**f)
	    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	    self.connection.send(msg)
	    core.thesis_mcf.add_flow(flow)
	    #log.info("added flow to switch {0}: {1}".format(self.connection, flow))
	except Exception, e:
	    pass
	    


class Controller:
    def __init__(self):
	core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
	Switch(event.connection)

    def _handle_PortStatus(self, event):
	log.info("port %s on switch %s has been modified" % (event.port, event.dpid))



def print_topology():
    log.info(core.openflow_discovery.adjacency)

def launch():
    discovery.launch()
    spanning_tree.launch(no_flood=True, hold_down=True)
    statistics.launch()
    multicommodity.launch()

    core.registerNew(Controller)
