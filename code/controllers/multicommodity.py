#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.thesis.topology as topology

import networkx as nx
from collections import namedtuple
from pulp import *
from pox.lib.addresses import IPAddr

log = core.getLogger()

	
class Multicommodity:
    _core_name = "thesis_mcf"

    def __init__(self):
	#Timer(5, self._update_flows, recurring=True)
	Timer(18, self._solve_mcf)
	self.flows = {}

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
	"""
	TODO use output of mcf to do this

	if str(event.parsed.src) == '00:00:00:00:00:01':
	    hops = self.all["ltr"][self.ltr]
	    self.ltr = 1 - self.ltr
	elif str(event.parsed.src) == '00:00:00:00:00:02':
	    hops = self.all["rtl"][self.rtl]
	    self.rtl = 1 - self.rtl
	else:
	    return
	log.info("PacketIn on s{0}: src {1}, path {2}".format(event.dpid, event.parsed.src, hops))
	self._install_forward_rule(msg, hops)
	"""

	flow = self.match_to_flow(msg.match)
	if flow:
	    self.flows[flow] = 500000	# set demand to 0.5 Mbps for shiggles

    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    core.thesis_base.switches[switch.dpid].connection.send(msg)

    def _solve_mcf(self):
	core.thesis_topo.get_links()
	mcf = LpProblem("routes", LpMaximize)

	# objective function
	z = LpVariable("z")
	mcf += z

	# "for all i in P" (per-commodity) constraints
	chosen = {}
	for flow in self.flows:
	    print "FLOW", flow
	    src = core.thesis_topo.get_host(ip=flow.nw_src)
	    dst = core.thesis_topo.get_host(ip=IPAddr(flow.nw_dst.split('/')[0]))
	    print "src", src, "dst", dst
	    if not (src and dst):
		continue
	    if not (src in core.thesis_topo.graph.nodes() and dst in core.thesis_topo.graph.nodes()):
		continue

	    print "still here"
	    paths = list(nx.all_simple_paths(core.thesis_topo.graph, src, dst))
	    labels = [str(k) for k in paths]

	    chosen[(src,dst)] = LpVariable.dicts("x[{0},{1}]".format(src,dst),labels, None, None, 'Binary')
	    x = chosen[(src,dst)]
	    
	    selected = sum([x[str(k)] for k in paths])
	    mcf += selected == 1

	# "for all j in E" (per-link) constraints
	for link,capacity in core.thesis_topo.get_links().iteritems():
	    print "LINK", link, capacity
	    traffic = 0
	    result = 0

	    for flow,demand in self.flows.iteritems():
		src = core.thesis_topo.get_host(ip=flow.nw_src)
		dst = core.thesis_topo.get_host(ip=IPAddr(flow.nw_dst.split('/')[0]))
		if not (src and dst):
		    continue
		if not (src in core.thesis_topo.graph.nodes() and dst in core.thesis_topo.graph.nodes()):
		    continue

		x = chosen[(src,dst)]
		selected = 0
		for path in nx.all_simple_paths(core.thesis_topo.graph, src, dst):
		    edges = zip(path[:-1],path[1:])
		    a = 1 if link in edges or (link[1],link[0]) in edges else 0
		    traffic += (a * demand * x[str(path)])

	    mcf += traffic <= capacity
	    mcf += z <= capacity - traffic

	# solve
	mcf.writeLP("mcf.lp")
	mcf.solve(GLPK())
	print "Status:", LpStatus[mcf.status]
	for v in mcf.variables():
	    print v.name, "=", v.varValue
	print "z =", value(mcf.objective)

    def _update_flows(self):
	#self._get_network()
	#stats = core.thesis_stats.get_flows()
	#log.info("stats:" + str(stats))
	self._solve_mcf()

    def match_to_flow(self, match):
	d = match if type(match) == dict else match_to_dict(match)
	try:
            f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"] }
            flow = core.thesis_topo.Flow(**f)
	    return flow
        except KeyError:
            return None


def launch():
    core.registerNew(Multicommodity)
