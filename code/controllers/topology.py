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


class Node(Entity):
    def __init__(self, id, ports=[], ips=[]):
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

    def _handle_HostEvent(self, event):
	e = event.entry
	if event.join:
	    if e.port == 65534: # controller port
		return
	    if not core.openflow_discovery.is_edge_port(e.dpid, e.port):
		return
	    print "host detected with ips", e.ipAddrs.keys(), type(e)
	    h = self.add_host(e.dpid, e.port, e.macaddr, ips=e.ipAddrs.keys())
	    s = self.get_switch(e.dpid)
	    self.add_link(h, None, s, e.port)

    def get_switch(self, dpid):
	try:
	    s = self._entities[dpid]
	except KeyError:
	    s = Switch(dpid)
	    self.addEntity(s)
	return s

    def add_host(self, dpid, port, mac, ips=[]):
	self._host_count += 1
	h = Host(self._host_count, ports=[mac], ips=ips)
	self._hosts[(dpid,port)] = h
	print "adding host with ips", ips, h
	return h

    def get_host(self, ip=None):
	print "trying to find host with ip", ip
	print [(h,h.ips) for k,h in self._hosts.items()]
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
	print self._hosts
	return self._links


def launch():
    core.registerNew(Network)
