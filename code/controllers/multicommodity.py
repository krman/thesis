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
	chosen = {}
	for flow in self.flows:
	    src = self.net.get_host_from_ip(flow.nw_src)
	    dst = self.net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
	    if not (src and dst):
		continue
	    if not (src in self.net.graph.nodes() and dst in self.net.graph.nodes()):
		continue

	    paths = list(nx.all_simple_paths(self.net.graph, src, dst))
	    labels = [str(k) for k in paths]

	    chosen[(src,dst)] = LpVariable.dicts("x[{0},{1}]".format(src,dst),labels, None, None, 'Binary')
	    x = chosen[(src,dst)]
	    
	    selected = sum([x[str(k)] for k in paths])
	    mcf += selected == 1

	# "for all j in E" (per-link) constraints
	for link,capacity in self.net.get_links().iteritems():
	    traffic = 0
	    result = 0

	    for flow,demand in self.flows.iteritems():
		src = self.net.get_host_from_ip(flow.nw_src)
		dst = self.net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
		if not (src and dst):
		    continue
		if not (src in self.net.graph.nodes() and dst in self.net.graph.nodes()):
		    continue

		x = chosen[(src,dst)]
		selected = 0
		for path in nx.all_simple_paths(self.net.graph, src, dst):
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
            f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
            flow = core.thesis_mcf.Flow(**f)
	    return flow
        except KeyError:
            return None


def launch():
    core.registerNew(Multicommodity)
