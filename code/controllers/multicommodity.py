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
from pox.lib.addresses import IPAddr

log = core.getLogger()


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")
Port = namedtuple("Port", "port_num mac_addr")


"""
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
"""


class Node:
    def __init__(self, id, type, ports=[], ips=[]):
	self.id = id
	self.type = type
	#log.info("new node: ports {0}, ips {1}".format(ports, ips))
	self.ports = set(ports)
	self.ips = set(ips)

    def __eq__(self, other):
	""" i don't actually know what it would mean for nodes to be
	equal. possibly only that one of the macs is the same, coz
	possibly this could happen at different stages of discovery.
	and macs are unlikely to suddenly switch... (vs ips).
	incidentally... do i care if the port numbers match? not for now. 
	actually, yeah, i kind of do. can relax if required (viewkeys)"""
	return (type(self) == type(other) and self.ports & other.ports)

    def __key(self):
	return (self.id, self.type)

    def __hash__(self):
	return hash(self.__key())

    def __repr__(self):
	string = "{0}{1}".format(self.type, self.id)
	"""if self.ports:
	    string += " ports={}".format(self.ports)
	if self.ips:
	    string += " ips={}".format(self.ips)
	"""
	return string

    def ports_overlap(self, ports):
	return self.ports & set([ports])

    def ips_overlap(self, ips):
	return self.ips & set([ips])

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

    def update(self, ports=[], ips=[]):
	self.ports.update(ports)
	self.ips.update(ips)


class Host(Node):
    def __init__(self, id, ports=[], ips=[]):
	Node.__init__(self, id, "h", ports, ips)


class Switch(Node):
    def __init__(self, id, ports=[], ips=[]):
	Node.__init__(self, id, "s", ports, ips)


class Link:
    """ capacity. """
    pass


class Topology:
    def __init__(self):
	self.graph = nx.Graph()
	self.ht = host_tracker.host_tracker()

	self.host_count = 0
	self.hosts = set()	# Host
	self.switches = dict()	# dpid:Switch
	self.links = dict()	# (n1,n2):capacity

    def _add_node(self, node):
	""" this is where ids are assigned. so the h1, s1 etc. """
	pass

    def get_host_from_ip(self, ip):
	try:
	    #log.info("trying to find ip {0}".format(ip))
	    host = next(h for h in self.hosts if ip in h.ips)
	    #log.info("found host {0} from ip {1}".format(host.id, ip))
	    return host
	except StopIteration:
	    return None

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
	try:
	    host = next(h for h in self.hosts if h.ports_overlap(ports))
	    #log.info("found host {0}".format(host.id))
	except StopIteration:
	    self.host_count += 1
	    host = Host(self.host_count, ports=[ports], ips=ips)
	    self.hosts.add(host)
	    #log.info("created host {0}: {1}".format(self.host_count, ports))
	return host

    def get_switch(self, dpid, ports=[], ips=[]):
	if dpid not in self.switches:
	    self.switches[dpid] = Switch(dpid)
	    #log.info("created switch {}".format(dpid))
	return self.switches[dpid]
    
    def mod_switch(self, dpid, ports=[], ips=[]):
	if dpid not in self.switches:
	    self.switches[dpid] = Switch(dpid)
	    #log.info("created switch {}".format(dpid))
	self.switches[dpid].update(ports=ports, ips=ips)

    def add_link(self, n1, p1, n2, p2):
	self.graph.add_edge(n1, n2)
	capacity = 5e6 if n1.type == 'h' or n2.type == 'h' else 1e6
	self.links[(n1,n2)] = capacity   # hardcode all links at 1 Mbps, except ones directly to hosts
	#log.info("adding link: {0} -> {1}, capacity {2}".format(n1,n2,capacity))

    def get_links(self):
	return self.links

    def refresh_network(self):
	self.graph.clear()

	# add switches
	for link in core.openflow_discovery.adjacency:
	    s1 = self.get_switch(link.dpid1)
	    s2 = self.get_switch(link.dpid2)
	    self.add_link(s1, link.port1, s2, link.port2)

	# add hosts
	for src, entry in self.ht.entryByMAC.items():
	    if entry.port == 65534: # controller port
		continue
	    if not core.openflow_discovery.is_edge_port(entry.dpid, entry.port):
		continue
	    h = self.get_host(entry.macaddr, ips=entry.ipAddrs.keys())
	    log.info("host {0} has ip {1}".format(h, entry.ipAddrs.keys()))
	    s = self.get_switch(entry.dpid)
	    self.add_link(h, None, s, entry.port)

	log.info("network nodes: {}".format(self.graph.nodes()))
	log.info("network edges: {}".format(self.graph.edges()))

	
class Multicommodity:
    _core_name = "thesis_mcf"

    Flow = Flow
    Hop = Hop
    Switch = Switch
    Host = Host
    Node = Node

    def __init__(self):
	#Timer(5, self._update_flows, recurring=True)
	Timer(18, self._solve_mcf)
	self.flows = {}
	self.net = Topology()

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
	    self.flows[flow] = 500000	# set demand to 0.5 Mbps for shiggles

    def _install_forward_rule(self, msg, hops):
	for switch in hops:
	    msg.actions = []
	    msg.actions.append(of.ofp_action_output(port = switch.port))
	    core.thesis_base.switches[switch.dpid].connection.send(msg)

    def _solve_mcf(self):
	self.net.refresh_network()

	mcf = LpProblem("routes", LpMaximize)

	# objective function
	z = LpVariable("z")
	mcf += z

	# "for all i in P" (per-commodity) constraints
	chosen = {}	# x[flow][path]: whether path is selected for flow
	for flow in self.flows:
	    #log.info("")
	    #log.info("new flow: {}".format(flow))
	    src = self.net.get_host_from_ip(flow.nw_src)
	    dst = self.net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
	    if not (src and dst):
		continue
	    #log.info("continuing! a good flow!")
	    if src in self.net.graph.nodes() and dst in self.net.graph.nodes():
		#log.info("yes, src {0} and dst {1} are in self.net.graph".format(src, dst))
		pass
	    else:
		#log.info("src {0} and dst {1} not in graph, skipping".format(src, dst))
		continue
	    log.info("possible routes for {0} -> {1}:".format(src,dst))

	    chosen[(src,dst)] = LpVariable.dicts("x[{0},{1}]".format(src,dst),[str(i) for i in nx.all_simple_paths(self.net.graph, src, dst)], None, None, 'Binary')
	    x = chosen[(src,dst)]
	    selected = 0
	    
	    for path in nx.all_simple_paths(self.net.graph, src, dst):
		log.info(path)
		selected += (x[str(path)])

	    mcf += selected == 1

	# "for all j in E" (per-link) constraints
	for link,capacity in self.net.get_links().iteritems():
	    #log.info(" ")
	    log.info("link {0}: {1} Mbps".format(link, capacity/1e6))
	    traffic = 0

	    # calculate capacity
	    result = 0
	    for flow,demand in self.flows.iteritems():
		#log.info("new flow: {}".format(flow))
		src = self.net.get_host_from_ip(flow.nw_src)
		dst = self.net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
		#log.info("flow: {0} -> {1}".format(src, dst))
		if not (src and dst):
		    continue
		#log.info("continuing! a good flow!")
		if src in self.net.graph.nodes() and dst in self.net.graph.nodes():
		    #log.info("yes, src {0} and dst {1} are in self.net.graph".format(src, dst))
		    pass
		else:
		    #log.info("src {0} and dst {1} not in graph, skipping".format(src, dst))
		    continue
		#log.info("possible routes for this flow:")
		#for i in nx.all_simple_paths(self.net.graph, src, dst):
		#log.info(i)

		x = chosen[(src,dst)]
		selected = 0
		for path in nx.all_simple_paths(self.net.graph, src, dst):
		    edges = zip(path[:-1],path[1:])
		    #log.info(edges)
		    #log.info("link {0}{1} in path".format(link, " not" if link not in edges and (link[1],link[0]) not in edges else ""))
		    a = 1 if link in edges or (link[1],link[0]) in edges else 0
		    #log.info("a={0}, d={1}, x={2}".format(a, demand/1e6, x[str(path)]))
		    traffic += (a * demand * x[str(path)])


		    #subtotal = 1
		    #subtotal *= 1 if link in path else 0
		    #subtotal *= LpVariable('xik')
		    #subtotal *= flow.demand


	    #log.info("TERMS FOR LINK {0}".format(link))
	    #log.info(traffic)
	    mcf += traffic <= capacity
	    mcf += z <= capacity - traffic

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
