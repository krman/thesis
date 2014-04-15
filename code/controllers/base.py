#!/usr/bin/python

"""
Route things! This is the base controller, which various modules plug into
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

import pox.openflow.discovery as discovery
import pox.openflow.spanning_tree as spanning_tree
import pox.thesis.statistics as statistics

log = core.getLogger()


class Switch:
    def __init__(self, connection):
	self.connection = connection
	connection.addListeners(self)

	log.info("setting NO_FLOOD on {0} ports on new switch".format(len(connection.ports)))
	log.info("port {0}".format(connection.ports))

    def _handle_PacketIn(self, event):
	packet = event.parsed
	#log.info(vars(packet))
	#log.info("new packet on switch {0}".format(self.connection))

	# flood arp
	msg = of.ofp_flow_mod()
	msg.match.dl_type = pkt.ethernet.ARP_TYPE
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	self.connection.send(msg)

	# only allow pings with certain tos
	msg = of.ofp_flow_mod()
	msg.match.dl_type = pkt.ethernet.IP_TYPE
	msg.match.nw_tos = 0x04
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	self.connection.send(msg)


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
    #Timer(5, print_topology, recurring=True)
    discovery.launch()
    spanning_tree.launch(no_flood=True, hold_down=True)
    statistics.launch()
    core.registerNew(Controller)
