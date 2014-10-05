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

import mcfpox.controller.statistics as statistics
import mcfpox.controller.topology as topology
import mcfpox.controller.multicommodity as multicommodity

from mcfpox.controller.lib import Flow

log = core.getLogger()


class Switch:
    def __init__(self, dpid, connection):
	self.dpid = dpid
	self.connection = connection
	connection.addListeners(self)

	# flood arp
	msg = of.ofp_flow_mod()
	msg.match.dl_type = pkt.ethernet.ARP_TYPE
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        msg.actions.append(of.ofp_action_output(port = of.OFPP_CONTROLLER))
	self.connection.send(msg)

    def _handle_PacketIn(self, event):
	packet = event.parsed
        if packet.find('tcp'):
            ip = packet.next
            tcp = ip.next
            if str(ip.srcip) != '0.0.0.0':
                flow = Flow(6, str(ip.srcip), str(ip.dstip),
                            tcp.srcport, tcp.dstport)
		log.info("flow {0} on switch {1}".format(flow, self.dpid))



class Controller:
    _core_name = "thesis_base"

    def __init__(self):
	self.switches = {}
	core.openflow.addListeners(self)
	core.addListeners(self)

    def _handle_ConnectionUp(self, event):
	self.switches[event.dpid] = Switch(event.dpid, event.connection)

    def _handle_PortStatus(self, event):
	log.info("port %s on switch %s has been modified" % (event.port, event.dpid))


def print_topology():
    log.info(core.openflow_discovery.adjacency)

def launch(objective=None, preinstall="{}"):
    discovery.launch()
    spanning_tree.launch(no_flood=True, hold_down=True)
    statistics.launch()
    topology.launch()
    multicommodity.launch(objective=objective, preinstall=preinstall)

    core.registerNew(Controller)
