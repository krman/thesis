from pulp import *
from collections import namedtuple
import networkx as nx
import itertools
from mcfpox.controller.lib import Flow, Hop


def get_host_from_ip(G, ip):
    return next((i for i in G.nodes() if G.node[i].get('ip') == str(ip)), None)


# https://docs.python.org/2/library/itertools.html#recipes
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def objective(graph, flows):
    """ Return a list of paths through the graph for each flow.

    Args:
	graph: 
	    A nx.Graph, annotated with network information including
	    IP addresses for hosts and port numbers for each link.
	flows: 
	    A list of mcfpox.controller.lib.Flow objects representing
	    5-tuples of flows to route through the network
    
    Returns:
	A dict mapping each flow in flows to a valid path through the graph.
	The path is expressed as a list of mcfpox.controller.lib.Hop objects.
	If no valid path can be found, the value for that entry is None.
    """

    G = graph
    rules = {}

    for flow in flows:
	src = get_host_from_ip(G, flow.nw_src)
	dst = get_host_from_ip(G, flow.nw_dst)

	if not (src and dst):
	    continue
	if not (src in G.nodes() and dst in G.nodes()):
	    continue

	path = nx.shortest_path(G, src, dst)[1:]
	hops = [Hop(dpid=int(a[1:]), port=G.edge[a][b]['port']) 
		for a,b in pairwise(path)]
	rules[flow] = hops

    return rules
