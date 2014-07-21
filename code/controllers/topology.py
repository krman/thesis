#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from pox.topology.topology import Entity, Topology

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
	self.ports = set(ports)
	self.ips = set(ips)
	Entity.__init__(self, id)

    def ports_overlap(self, ports):
	return self.ports & set([ports])

    def ips_overlap(self, ips):
	return self.ips & set([ips])

    def combine(self, other):
	self.ports.update(other.ports)
	self.ips.update(other.ips)
	return self

    def update(self, ports=[], ips=[]):
	self.ports.update(ports)
	self.ips.update(ips)


class Host(Node):
    def __init__(self, id, ports=[], ips=[]):
	Node.__init__(self, -id, ports, ips)

    def __repr__(self):
	return "h{0}".format(-self.id)
	

class Switch(Node):
    def __init__(self, id, ports=[], ips=[]):
	Node.__init__(self, id, ports, ips)

    def __repr__(self):
	return "s{0}".format(self.id)


class Link:
    """ capacity. """
    pass


class Network(Topology):
    _core_name = "thesis_topo"

    Flow = Flow
    Hop = Hop
    Port = Port

    def __init__(self):
	self.graph = nx.Graph()
	self.ht = host_tracker.host_tracker()

	core.openflow_discovery.addListeners(self)
	self.listenTo(self.ht)
	core.addListeners(self)

	self._host_count = 0
	self._hosts = dict()	# (dpid,port):Host
	self._links = dict()	# (n1,n2):capacity
	Topology.__init__(self)
	print "starting entities"
	print self._entities

    def _handle_LinkEvent(self, event):
	"""
	l = event.link
	if event.added:
	    s1 = self.get_switch(l.dpid1)
	    s2 = self.get_switch(l.dpid2)

	    # delete any switches masquerading as hosts
	    for dpid,port in [(l.dpid1,l.port1), (l.dpid2,l.port2)]:
		h = self._hosts.get((dpid,port), None)
		if h:
		    del self._hosts[(dpid,port)]

		# and their associated links
		for n1,n2 in self._links.keys():
		    if h == n1 or h == n2:
			del self._links[(n1,n2)]

	    self.add_link(s1, l.port1, s2, l.port2)
	"""

    def _handle_HostEvent(self, event):
	"""
	e = event.entry
	if event.join:
	    if e.port == 65534: # controller port
		return
	    if not core.openflow_discovery.is_edge_port(e.dpid, e.port):
		return
	    print "host detected with ips", e.ipAddrs.keys(), type(e)
	    h = self.get_host(e.dpid, e.port, e.macaddr, ips=e.ipAddrs.keys())
	    s = self.get_switch(e.dpid)
	    self.add_link(h, None, s, e.port)
	"""

    def get_switch(self, dpid):
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
	    h = next(h for k,h in self._hosts.items() if ip in h.ips)
	except StopIteration:
	    h = None
	return h

    def add_link(self, n1, p1, n2, p2):
	self.graph.add_edge(n1, n2)
	capacity = 5e6 if type(n1) == Host or type(n2) == Host else 1e6
	self._links[(n1,n2)] = capacity   # hardcode all links at 1 Mbps, except ones directly to hosts

    def get_links(self):
	return self.links

    def get_adjacency(self):
	return core.openflow_discovery.adjacency

    def refresh_network(self):
	G = nx.DiGraph()
	G.clear()
	self.host_count = 0

	# add switches
	for link in core.openflow_discovery.adjacency:
	    s1 = "s{0}".format(link.dpid1)
	    s2 = "s{0}".format(link.dpid2)
	    G.add_nodes_from([s1,s2])
	    G.add_edge(s1, s2, {'capacity':1e6, 'port':link.port1})
	    G.add_edge(s2, s1, {'capacity':1e6, 'port':link.port2})

	# add hosts
	for src, entry in self.ht.entryByMAC.items():
	    if entry.port == 65534: # controller port
		continue
	    if not core.openflow_discovery.is_edge_port(entry.dpid, entry.port):
		continue

	    self.host_count += 1
	    h = "h{0}".format(self.host_count)
	    s = "s{0}".format(entry.dpid)
	    print "HOST", h, "ON SWITCH", s, "ADDRESS", entry.macaddr
	    G.add_nodes_from([h,s])
	    if entry.ipAddrs.keys():
		G.node[h]['ip'] = str(next(iter(entry.ipAddrs.keys())))
	    G.add_edge(h, s, {'capacity':1e6})
	    G.add_edge(s, h, {'capacity':1e6, 'port':entry.port})

	self.graph = G


def launch():
    core.registerNew(Network)
