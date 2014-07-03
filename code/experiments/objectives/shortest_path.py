from pulp import *
from collections import namedtuple
import networkx as nx
import itertools


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")


def get_host_from_ip(G, ip):
    return next((i for i in G.nodes() if G.node[i].get('ip') == str(ip)), None)


# https://docs.python.org/2/library/itertools.html#recipes
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def objective(net, flows):
    G = net.graph
    rules = {}

    for flow in flows:
	src = get_host_from_ip(G, flow.nw_src)
	dst = get_host_from_ip(G, flow.nw_dst)

	if not (src and dst):
	    continue
	if not (src in G.nodes() and dst in G.nodes()):
	    continue

	path = nx.shortest_path(G, src, dst)
	hops = [Hop(dpid=a, port=G.edge[a][b]) for a,b in pairwise(path)]
	rules[flow] = hops

    return rules
