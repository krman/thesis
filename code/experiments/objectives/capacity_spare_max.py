#!/usr/bin/python

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


def var2fh(var):
    var = var[2:].replace("'","")
    flow, x, hops = var.partition('_')
    hops = hops[1:-1].split(',_')[1:-1]
    flow = tuple(flow.split(','))
    return (flow, hops)


def objective(net, flows, cutoff=None):
    G = net.graph
    rules = {}

    mcf = LpProblem("routes", LpMaximize)

    # objective function
    z = LpVariable("z")
    mcf += z

    # "for all i in P" (per-commodity) constraints
    chosen = {}
    hosts = {}
    pair2flow = {}
    label2path = {}

    for flow in flows:
	src = get_host_from_ip(G, flow.nw_src)
	dst = get_host_from_ip(G, flow.nw_dst)

	if not (src and dst):
	    continue
	if not (src in net.graph.nodes() and dst in net.graph.nodes()):
	    continue

	print "madeit"
	hosts[flow.nw_src] = src
	hosts[flow.nw_dst] = dst
	pair2flow[(src,dst)] = flow
	
	paths = list(nx.all_simple_paths(net.graph, src, dst, cutoff=cutoff))
	labels = [i for i in range(len(paths))]
	
	# TODO make labels not be path names - i only use in this function

	chosen[(src,dst)] = LpVariable.dicts("x_{0},{1}".format(src,dst),labels, None, None, 'Binary')
	x = chosen[(src,dst)]
	
	selected = sum([x[i] for i,k in enumerate(paths)])
	mcf += selected == 1

    # "for all j in E" (per-link) constraints
    done = []
    for a,b in G.edges():
	if (b,a) in done:
	    continue
	done.append((a,b))

	capacity = G.edge[a][b]['capacity']
	link = (a,b)

	traffic = 0
	result = 0

	for flow,demand in flows.iteritems():
	    src = hosts.get(flow.nw_src)
	    dst = hosts.get(flow.nw_dst)

	    if not (src and dst):
		continue

	    x = chosen[(src,dst)]
	    selected = 0
	    paths = nx.all_simple_paths(net.graph, src, dst, cutoff=cutoff)
	    for i,path in enumerate(paths):
		edges = zip(path[:-1],path[1:])
		a = 1 if link in edges or (link[1],link[0]) in edges else 0
		traffic += (a * demand * x[i])

	mcf += traffic <= capacity
	mcf += z <= capacity - traffic

    # solve
    mcf.writeLP("mcf.lp")
    mcf.solve()

    # calculate hops
    for v in mcf.variables():
	if v.name != 'z' and v.varValue == 1:
	    pair, path = var2fh(v.name)
	    hops = [Hop(dpid=a, port=G.edge[a][b]['port']) 
				for a,b in pairwise(path)]
	    rules[flow] = hops

    return rules
