#!/usr/bin/python

"""
Multicommodity flow module: decides where different flows should go
"""

from pox.core import core
from pox.lib.addresses import IPAddr
from pox.lib.recoco import Timer
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.openflow.discovery as discovery
import pox.host_tracker.host_tracker as host_tracker

from collections import namedtuple
import networkx as nx
from pulp import *

log = core.getLogger()


class Network(EventMixin):
    _core_name = "thesis_topo"

    def __init__(self):
	self.graph = nx.Graph()
	self.ht = host_tracker.host_tracker()

	core.openflow_discovery.addListeners(self)
	self.listenTo(self.ht)
	core.addListeners(self)

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
	    #print "HOST", h, "ON SWITCH", s, "ADDRESS", entry.macaddr
	    G.add_nodes_from([h,s])
	    if entry.ipAddrs.keys():
		G.node[h]['ip'] = str(next(iter(entry.ipAddrs.keys())))
	    G.add_edge(h, s, {'capacity':1e6})
	    G.add_edge(s, h, {'capacity':1e6, 'port':entry.port})

	self.graph = G


def launch():
    core.registerNew(Network)
