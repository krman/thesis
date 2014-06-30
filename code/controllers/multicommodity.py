#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.thesis.topology as topology

from collections import namedtuple

log = core.getLogger()

	
class Multicommodity:
    _core_name = "thesis_mcf"

    def __init__(self, objective):
	#Timer(5, self._update_flows, recurring=True)
	Timer(50, self._solve_mcf)
	self.flows = {}
	self.net = core.thesis_topo
	self.objective = objective

	core.openflow.addListeners(self)
	core.addListeners(self)

    def _handle_PacketIn(self, event):
        msg = of.ofp_flow_mod()
        msg.match = msg.match.from_packet(event.parsed)

	if event.parsed.find("arp"):
	    #log.info("arp packet {}".format(event.parsed))
	    #log.info(vars(event.parsed))
	    pass

	if not event.parsed.find("ipv4"):
	    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	    event.connection.send(msg)
	    return
	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	event.connection.send(msg)

	flow = self.match_to_flow(msg.match)
	if flow:
	    self.flows[flow] = 500000	# set demand to 0.5 Mbps for shiggles

    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    print "{0}.{1}".format(switch.dpid,switch.port),
	    core.thesis_base.switches[switch.dpid].connection.send(msg)
	print

    def _solve_mcf(self):
	rules = self.objective(self.net, self.flows)
	print "RULES", rules
	for flow,hops in rules.items():
	    nw_src, nw_dst = flow
	    msg = of.ofp_flow_mod()
	    msg.command = of.OFPFC_MODIFY
	    msg.match.dl_type = 0x800
	    msg.match.nw_proto = 6
	    msg.match.nw_src = nw_src
	    msg.match.nw_dst = nw_dst
	    print "INSTALLING", nw_src, nw_dst,
	    #self._install_forward_rule(msg, hops)

    def _update_flows(self):
	#self._get_network()
	#stats = core.thesis_stats.get_flows()
	#log.info("stats:" + str(stats))
	self._solve_mcf()

    def match_to_flow(self, match):
	d = match if type(match) == dict else match_to_dict(match)
	try:
            f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
            flow = core.thesis_topo.Flow(**f)
	    return flow
        except KeyError:
            return None


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
