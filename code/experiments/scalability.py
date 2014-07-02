#!/usr/bin/python

import subprocess
import signal
import sys
import os
import importlib

from time import sleep
from datetime import datetime

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

import networkx as nx

TOPOLOGY = 'fat_tree'
OBJECTIVE = 'max_spare_capacity'
RESULTS = 'results'

def cleanup(signal=None, frame=None):
    try:
	net.stop()
    except Exception:
	pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def mnc():
    clean = subprocess.Popen(['sudo', 'mn', '-c'])
    clean.wait()

sys.path.append(os.path.abspath('/home/imz/src/pox'))
topo = importlib.import_module('topos.' + TOPOLOGY)
obj = importlib.import_module('objectives.' + OBJECTIVE)

class TestTopology:
    def __init__(self):
        self.graph = nx.Graph()
        self.ht = host_tracker.host_tracker()

        self.host_count = 0
        self.hosts = set()      # Host
        self.switches = dict()  # dpid:Switch
        self.links = dict()     # (n1,n2):capacity

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

    def add_link(self, n1, p1, n2, p2):
        self.graph.add_edge(n1, n2)

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


print "run,setup time,pulp time"
for i in range(5):
    print "{},".format(i),
    mnc()
    start = datetime.now()
    net = topo.create_net(controller=RemoteController, k=2)
    end = datetime.now()
    net.stop()
    print "{},".format(end-start),
    net = nx.Graph()
    flows = {}
    print obj.objective(net, flows),
    print

cleanup()
