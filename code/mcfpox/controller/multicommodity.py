#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from pox.lib.addresses import IPAddr

from mcfpox.controller import topology
from mcfpox.controller.lib import Flow, Hop
from mcfpox.objectives import shortest_path

from collections import namedtuple

log = core.getLogger()

	
class Multicommodity:
    _core_name = "thesis_mcf"

    def __init__(self, objective, preinstall):
	#Timer(30, self._update_flows)
	Timer(15, self._preinstall_rules)

	self.flows = {}
	self.net = core.thesis_topo
	self.stats = core.thesis_stats
	self.objective = objective

	self.preinstall = preinstall

	core.openflow.addListeners(self)
	core.addListeners(self)

    def _handle_PacketIn(self, event):
	self.net.refresh_network()
	packet = event.parsed
	if packet.find('tcp'):
	    ip = packet.next
	    tcp = ip.next
	    if str(ip.srcip) != '0.0.0.0':
		flow = Flow(6, str(ip.srcip), str(ip.dstip), 
			    tcp.srcport, tcp.dstport)
		rules = shortest_path.objective(self.net.graph, [flow])
		self._install_rule_list(rules)

	
    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    #print "{0}.{1}".format(switch.dpid,switch.port),
	    core.thesis_base.switches[switch.dpid].connection.send(msg)
	print

    def _install_rule_list(self, rules):
	for flow,hops in rules.items():
	    msg = of.ofp_flow_mod()
	    msg.command = of.OFPFC_MODIFY
	    msg.match.dl_type = 0x800
	    msg.match.nw_proto = 6
	    msg.match.nw_src = flow.nw_src
	    msg.match.nw_dst = flow.nw_dst
	    ts, td = flow.tp_src, flow.tp_dst
	    msg.match.tp_src = None if ts is None else int(ts)
	    msg.match.tp_dst = None if td is None else int(td)
	    #print "INSTALLING", flow.nw_src, flow.nw_dst,
	    self._install_forward_rule(msg, hops)
	
    def _preinstall_rules(self):
	#print "PREINSTALLING RULES"
	self._install_rule_list(self.preinstall)

    def _solve_mcf(self):
	rules = self.objective(self.net.graph, self.flows)
	self._install_rule_list(rules)

    def _update_flows(self):
	self.net.refresh_network()
	self.flows = self.stats.get_fake_flows()
	self._solve_mcf()


def default_objective(net, flows):
    print "Default objective function, given:"
    print "net:", net
    print "flows:", flows

def launch(objective=default_objective, preinstall="{}"):
    try:
	p = eval(preinstall) # HORRIBLE HORRIBLE
    except TypeError:
	pass

    core.registerNew(Multicommodity, objective=objective, preinstall=p)
