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


def widest_path(G, src, dst):
    S = set([src])
    T = set([n for n in G.nodes() if n != src])
    print S, T

    N = G.nodes()
    B = {}
    for n in N:
        b = {}
        for k in N:
            if k == n:
                continue
            try:
                b[k] = G.edge[n][k]['capacity']
            except KeyError:
                b[k] = 0
        B[n] = b
    P = {n:[] for n in N}

    while True:
        k = None
        highest = 0
        neighbors = set([])

        for n in S:
            for m in G[n]:
                if m in S:
                    continue
                B[src][m] = G.edge[n][m]['capacity']
                if B[src][m] > highest:
                    k = m
                    highest = B[src][m]
                    P[k] = P[n] + [k]

        S.add(k)
        T.remove(k)
        if not T:
            break

        for n in T:
            old = B[src][n]
            new = min(B[src][k], B[k][n])
            B[src][n] = max(old, new)
            if new > old:
                P[n] = P[k] + [n]

    return P[dst]


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

    G = graph.copy()
    rules = {}
    flows.sort(key=lambda a: a[1], reverse=True)

    for flow,demand in flows:
        src = get_host_from_ip(G, flow.nw_src)
        dst = get_host_from_ip(G, flow.nw_dst)

        if not (src and dst):
            continue
        if not (src in G.nodes() and dst in G.nodes()):
            continue

        path = widest_path(G, src, dst)

        hops = []
        for a,b in pairwise(path):
            hops.append(Hop(dpid=int(a[1:]), port=G.edge[a][b]['port']))
            G.edge[a][b]['capacity'] -= demand
            G.edge[b][a]['capacity'] -= demand

        rules[flow] = hops

    return rules
