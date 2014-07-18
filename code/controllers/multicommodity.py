#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from pox.lib.addresses import IPAddr

import pox.thesis.topology as topology

from collections import namedtuple

log = core.getLogger()

	
class Multicommodity:
    _core_name = "thesis_mcf"

    def __init__(self, objective):
	Timer(30, self._update_flows)

	self.net = core.thesis_topo
	self.stats = core.thesis_stats
	self.objective = objective

	core.openflow.addListeners(self)
	core.addListeners(self)

    def _handle_PacketIn(self, event):
	p = event.parsed
	if p.find("ipv4"):
	    #log.info("PacketIn on s{0}: src {1}".format(event.dpid, event.parsed.src))
	    if event.parsed.next.find("udp"):
		return
	    print dir(event.parsed)
	    print event.parsed.next
	    print dir(event.parsed.next)

    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    print "{0}.{1}".format(switch.dpid,switch.port),
	    core.thesis_base.switches[switch.dpid].connection.send(msg)
	print

    def _solve_mcf(self):
	rules = self.objective(self.net, self.flows)
	for flow,hops in rules.items():
	    msg = of.ofp_flow_mod()
	    msg.command = of.OFPFC_MODIFY
	    msg.match.dl_type = 0x800
	    msg.match.nw_proto = 6
	    msg.match.nw_src = flow.nw_src
	    msg.match.nw_dst = flow.nw_dst
	    ts, td = flow.tp_src, flow.tp_dst
	    msg.match.tp_src = None if ts == "None" else int(ts)
	    msg.match.tp_dst = None if td == "None" else int(td)
	    #msg.match.tp_src = None if ts is None else int(ts)
	    #msg.match.tp_dst = None if td is None else int(td)
	    print "INSTALLING", flow.nw_src, flow.nw_dst,
	    self._install_forward_rule(msg, hops)

    def _update_flows(self):
	self.net.refresh_network()
	self.flows = self.stats.get_fake_flows()
	self._solve_mcf()


def default_objective(net, flows):
    print "Default objective function, given:"
    print "net:", net
    print "flows:", flows

def launch(objective=None):
    import sys, os
    sys.path.append(os.path.abspath('../experiments/objectives'))
    try:
	obj_module = __import__(objective)
	f = obj_module.objective
    except Exception:
	f = default_objective

    core.registerNew(Multicommodity, objective=f)
