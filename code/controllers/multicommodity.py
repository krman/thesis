#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.openflow.discovery as discovery
import pox.host_tracker.host_tracker as host_tracker

import networkx as nx
from collections import namedtuple
from pulp import *

log = core.getLogger()


Flow = namedtuple("Flow", ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"])
Hop = namedtuple("Hop", ["dpid", "port"])


class Host(namedtuple("Host", ["mac", "ip"])):
    def __new__(self, mac, ip=None):
	return super(Host, self).__new__(self, mac, ip)

    def __eq__(self, other):
	return self.mac == other.mac



class Switch(namedtuple("Switch", ["dpid", "ip"])):
    def __new__(self, dpid=None, ip=None):
	return super(Switch, self).__new__(self, dpid, ip)

    def __repr__(self):
	return "s{0}".format(self.dpid)
    
    def __str__(self):
	return self.__repr__()


class Node:
    def __init__(self, id, type, ports=[], ips=[]):
	self.type = type
	self.ports = dict().update(ports) # whatever it is for dicts
	# ports is dict[EthAddr] = int ? or would the other way be better?
	self.ips = set().update(ips)

    def __eq__(self, other):
	""" i don't actually know what it would mean for nodes to be
	equal. possibly only that one of the macs is the same, coz
	possibly this could happen at different stages of discovery.
	and macs are unlikely to suddenly switch... (vs ips).
	incidentally... do i care if the port numbers match? not for now. 
	actually, yeah, i kind of do. can relax if required (viewkeys)"""
	return self.ports.viewitems() & other.ports.viewitems()

    def combine(self, other):
	self.ports.update(other.ports)
	self.ips.update(other.ips)
	return self
	""" ugh. does this mean a single node can have multiple ids?! 
	would it though? the ids are more for humans. at each stage
	when the rules are being applied, the commodities are listed
	as 5-tuples, and i just look up at that exact moment and see
	the man of my dreams? no. i look up the associated Node, not
	even mac address required. so ids are really just for printing
	and it doesn't matter if some get lost/subsumed. """


class Topology:
    def __init__(self):
	self.graph = nx.Graph()

    def _add_node(self, node):
	""" this is where ids are assigned. so the h1, s1 etc. """
	pass

    def get_host(self, ports=[], ips=[]):
	""" Returns a Node for the host matching the macs/ips given.
	either macs or ips can be an empty list but not both
	ideally this should only match one Node (eg if multiple macs/ips
	are specified, they'll all be associated with one thing).
	i guess if they're not, ips will be unassociated with the existing
	Node/s and reassigned to this one. i can't imagine a world where
	you'd put in two macs from different nodes but i guess the only
	logical effect is to combine them into one single node.
	either way, a message/info thing is printed. """
	# add to the set of hosts
	h = Node("switch", ports, ips)
	pass

    def get_switch(self, dpid):
	pass

    def add_link(self, n1, n2):
	self.graph.add_edge(s1, s2)

    def get_network(self):
	self.graph.clear()

	# add switches
	for link in core.openflow_discovery.adjacency:
	    s1 = self.get_switch(link.dpid1)
	    s2 = self.get_switch(link.dpid2)
	    self.add_link(s1, link.port1, s2, link.port2)

	# add hosts
	for src, entry in self.ht.entryByMAC:
	    if entry.port == 65534: # controller port
		continue
	    if not core.openflow_discovery.is_edge_port(entry.dpid, entry.port):
		continue

	    h = self.get_host(entry.macaddr)
	    s = self.get_switch(entry.dpid)
	    self.add_link(h, None, s, entry.port)


	
	
class Multicommodity:
    _core_name = "thesis_mcf"

    Flow = Flow
    Hop = Hop
    Switch = Switch
    Host = Host
    Node = Node

    def __init__(self):
	#Timer(5, self._update_flows, recurring=True)
	Timer(15, self._solve_mcf)
	self.flows = {}
	self.graph = nx.Graph()
	self.nodes = set()

	# hosts attached to switches
	self.ht = host_tracker.host_tracker()

	core.openflow.addListeners(self)
	core.addListeners(self)

    def _handle_core_ComponentRegistered(self, event):
	log.info("component up: {}".format(event.name))
	if event.name == "host_tracker":
	    event.component.addListenerByName("HostEvent", self._handle_host_tracker_HostEvent) 
    def _handle_host_tracker_HostEvent(self, event):
	log.info("host detected")
	log.info(event)

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
	    self.flows[flow] = 0

    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    core.thesis_base.switches[switch.dpid].connection.send(msg)

    def _get_network(self):
	self.net.get_network()

	
	"""
	# add switches
	for link in core.openflow_discovery.adjacency:
	    self.nodes.add
	    s1 = Switch(dpid=link.dpid1)
	    s2 = Switch(dpid=link.dpid2)
	    #self.nodes.update(Node(type="switch",data=s1), Node(type="switch",data=s2))
	    self.graph.add_edge(s1, s2)
	
	# add hosts
	log.info("senthtent")
	log.info(self.ht.entryByMAC)
	for e in self.ht.entryByMAC:
	    entry = self.ht.entryByMAC[e]
	    if entry.port == 65534: continue
	    log.info("general port: {}".format(entry))
	    ep = core.openflow_discovery.is_edge_port(entry.dpid, entry.port)
	    if ep:
		log.info("edge port: {}".format(entry))
	    if ep:
		ip = None
		for key in entry.ipAddrs:
		    ip = key
		if not ip: continue
		host = Host(mac=entry.macaddr, ip=ip)
		self.graph.add_edge(host, Switch(dpid=entry.dpid))
		self.nodes.add(host)
	    code i want to write
	    get_{host,switch} will create them if it can't find them
	    wait, but entry.macaddr is the macaddr of the switch on that port, isn't it?

	    h = self.net.get_host(mac=entry.macaddr, ip)
	    s = self.net.get_switch(dpid=entry.dpid)
	    self.net.add_link(h, s)
	"""

	#log.info("edges:" + str(self.graph.edges()))

    def _solve_mcf(self):
	log.info("solving... getting network edges:");
	log.info("nodes: {}".format(self.nodes))
	self._get_network()
	edges = self.graph.edges()
	log.info("edges: {}".format(edges))
	log.info("nodes: {}".format(self.nodes))

	mcf = LpProblem("routes", LpMaximize)

	# objective function
	z = LpVariable("z")
	mcf += z

	# constraints
	mcf += z <= 10
	log.info("constraints: src/dst pairs")
	for flow in self.flows:
	    nw_src = flow.nw_src
	    nw_dst = flow.nw_dst.split('/')[0]
	    log.info(self.nodes)
	    dl_src = next((h for h in self.nodes if h.ip==nw_src), None)
	    dl_dst = next((h for h in self.nodes if h.ip==nw_dst), None)
	    if not (dl_src and dl_dst): continue

	    log.info("{0} -> {1} becomes {2} -> {3}".format(nw_src, nw_dst, dl_src.mac, dl_dst.mac))
	    for i in nx.all_simple_paths(self.graph, dl_src, dl_dst):
		log.info(i)

	# solve
	mcf.writeLP("mcf.lp")
	mcf.solve(GLPK())
	print "Status:", LpStatus[mcf.status]
	for v in mcf.variables():
	    print v.name, "=", v.varValue
	print "z =", value(mcf.objective)

    def _solve_blending_problem(self):
	log.info("calling pulp")
	log.info(self.mcf)
	Ingredients = ['CHICKEN', 'BEEF', 'MUTTON', 'RICE', 'WHEAT', 'GEL']
	costs = {'CHICKEN': 0.013, 'BEEF': 0.008, 'MUTTON': 0.010, 'RICE': 0.002, 'WHEAT': 0.005, 'GEL': 0.001}
	proteinPercent = {'CHICKEN': 0.100, 'BEEF': 0.200, 'MUTTON': 0.150, 'RICE': 0.000, 'WHEAT': 0.040, 'GEL': 0.000}
	fatPercent = {'CHICKEN': 0.080, 'BEEF': 0.100, 'MUTTON': 0.110, 'RICE': 0.010, 'WHEAT': 0.010, 'GEL': 0.000}
	fibrePercent = {'CHICKEN': 0.001, 'BEEF': 0.005, 'MUTTON': 0.003, 'RICE': 0.100, 'WHEAT': 0.150, 'GEL': 0.000}
	saltPercent = {'CHICKEN': 0.002, 'BEEF': 0.005, 'MUTTON': 0.007, 'RICE': 0.002, 'WHEAT': 0.008, 'GEL': 0.000}
	prob = LpProblem("The Whiskas Problem", LpMinimize)
	ingredient_vars = LpVariable.dicts("Ingr",Ingredients,0)
	prob += lpSum([costs[i]*ingredient_vars[i] for i in Ingredients]), "Total Cost of Ingredients per can"
	prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100, "PercentagesSum"
	prob += lpSum([proteinPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 8.0, "ProteinRequirement"
	prob += lpSum([fatPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 6.0, "FatRequirement"
	prob += lpSum([fibrePercent[i] * ingredient_vars[i] for i in Ingredients]) <= 2.0, "FibreRequirement"
	prob += lpSum([saltPercent[i] * ingredient_vars[i] for i in Ingredients]) <= 0.4, "SaltRequirement"
	prob.writeLP("WhiskasModel2.lp")
	prob.solve(GLPK())
	print "Status:", LpStatus[prob.status]
	for v in prob.variables():
	    print v.name, "=", v.varValue
	print "Total Cost of Ingredients per can = ", value(prob.objective)

    def _update_flows(self):
	#self._get_network()
	#stats = core.thesis_stats.get_flows()
	#log.info("stats:" + str(stats))
	self._solve_mcf()

    def match_to_flow(self, match):
	d = match if type(match) == dict else match_to_dict(match)
	try:
            f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
            flow = core.thesis_mcf.Flow(**f)
	    return flow
        except KeyError:
            return None


def launch():
    core.registerNew(Multicommodity)
