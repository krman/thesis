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
        """
        Initialise topology module.
        """
        self.graph = nx.Graph()
        self.ht = host_tracker.host_tracker()

        core.openflow_discovery.addListeners(self)
        self.listenTo(self.ht)
        core.addListeners(self)


    def refresh_network(self):
        """
        Update view of network from discovery and host_tracker adjacency lists.
        """
        G = nx.DiGraph()
        G.clear()
        self.host_count = 0

        # add switches
        for link in core.openflow_discovery.adjacency:
            s1 = "s{0}".format(link.dpid1)
            s2 = "s{0}".format(link.dpid2)
            G.add_nodes_from([s1,s2])
            G.add_edge(s1, s2, {'capacity':10e6, 'port':link.port1})
            G.add_edge(s2, s1, {'capacity':10e6, 'port':link.port2})

        # add hosts
        for src, entry in self.ht.entryByMAC.items():
            if entry.port == 65534: # controller port
                continue
            if not core.openflow_discovery.is_edge_port(entry.dpid, entry.port):
                continue

            self.host_count += 1
            h = "h{0}".format(self.host_count)
            s = "s{0}".format(entry.dpid)
            G.add_nodes_from([h,s])
            if entry.ipAddrs.keys():
                G.node[h]['ip'] = str(next(iter(entry.ipAddrs.keys())))
            G.add_edge(h, s, {'capacity':20e6})
            G.add_edge(s, h, {'capacity':20e6, 'port':entry.port})

        self.graph = G



def launch():
    core.registerNew(Network)
