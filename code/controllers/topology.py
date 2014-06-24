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
    _core_name = "thesis_topo"

    Flow = Flow
    Hop = Hop
    Port = Port

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
    
    def get_ip_from_host(self, hid):
	try:
	    host = next(next(iter(h.ips)) for h in self.hosts if h.id==int(hid))
	    print hid, host
	    return host
	except StopIteration:
	    print hid, None
	    return none

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

    def get_adjacency(self):
	return core.openflow_discovery.adjacency

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



def launch():
    core.registerNew(Topology)
