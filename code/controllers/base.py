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
	eth_packet = event.parsed
	tcp = 0
	if eth_packet.type == pkt.ethernet.IP_TYPE:
	    ip_packet = eth_packet.payload
	    #log.info(vars(ip_packet))
	    if ip_packet.protocol == pkt.ipv4.TCP_PROTOCOL:
		tcp_packet = ip_packet.next
		#log.info(vars(tcp_packet))
		tcp = 1
	else:
	    #log.info(eth_packet)
	    pass
	
	if tcp:
	    flow = (ip_packet.srcip, tcp_packet.srcport, ip_packet.dstip, tcp_packet.dstport, ip_packet.protocol)
	    #log.info("Adding flow: {0}".format(flow))
	    core.thesis_mcf.add_flow(flow)
	    msg = of.ofp_flow_mod()
	    msg.match = msg.match.from_packet(eth_packet)
	    #log.info(str(msg.match))
	    #log.info(hash(msg.match))
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
    multicommodity.launch()
    core.registerNew(Controller)
