#!/usr/bin/python

from pulp import *
from collections import namedtuple
import networkx as nx
import itertools

from mcfpox.controller.lib import Flow, Hop


def get_host_from_ip(G, ip):
    for i in G.nodes():
        #print type(G.node[i].get('ip')), type(str(ip)), G.node[i].get('ip') == str(ip)
        pass
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


def var2flow(G, var):
    #x_h2_41660_h1_5001_6_0
    var = var[2:]
    src, p1, dst, p2, proto, num = var.split('_')
    n1 = G.node[src].get('ip', None)
    n2 = G.node[dst].get('ip', None)
    return Flow(nw_src=n1, tp_src=p1, nw_dst=n2, tp_dst=p2, nw_proto=proto)


def objective(graph, flows, cutoff=None):
    G = graph
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
    pair2paths = {}
    path2edges = {}

    #print "for all i in P"
    for flow,demand in flows:
        #print flow.nw_src, flow.nw_dst, demand
        src = get_host_from_ip(G, flow.nw_src)
        dst = get_host_from_ip(G, flow.nw_dst.split('/')[0])

        if not (src and dst):
            continue
        if not (src in G.nodes() and dst in G.nodes()):
            continue

        hosts[flow.nw_src] = src
        hosts[flow.nw_dst] = dst
        pair2flow[(src,dst)] = flow

        paths = list(nx.all_simple_paths(G, src, dst, cutoff=cutoff))
        pair2paths[(src,dst)] = paths
        for i,path in enumerate(paths):
            path2edges[(src,dst,i)] = zip(path[:-1],path[1:])
        prefix = "_".join([str(i) for i in ["x", src, flow.tp_src, dst, flow.tp_dst, flow.nw_proto]])
        label2path.update({"_".join([prefix,str(i)]):path[1:] for i,path in enumerate(paths)})

        labels = [i for i in range(len(paths))]
        chosen[(src,dst)] = LpVariable.dicts(prefix,labels,None,None,'Binary')
        x = chosen[(src,dst)]

        selected = sum([x[i] for i,k in enumerate(paths)])
        mcf += selected == 1

    # "for all j in E" (per-link) constraints
    done = []
    #print "for all j in E"
    for a,b in G.edges():
        if (b,a) in done:
            continue
        done.append((a,b))

        capacity = G.edge[a][b]['capacity']
        link = (a,b)
        #print "link",link,capacity

        traffic = 0
        result = 0

        #print "(for all j in E) for all i in P"
        for flow,demand in flows:
            #print flow.nw_src, flow.nw_dst, demand
            src = hosts.get(flow.nw_src)
            dst = hosts.get(flow.nw_dst)

            if not (src and dst):
                continue

            x = chosen[(src,dst)]
            selected = 0
            #paths = nx.all_simple_paths(G, src, dst, cutoff=cutoff)
            paths = pair2paths[(src,dst)]
            for i,path in enumerate(paths):
                #print path
                #edges = zip(path[:-1],path[1:])
                edges = path2edges[(src,dst,i)]
                #print edges
                a = 1 if link in edges or (link[1],link[0]) in edges else 0
                traffic += (a * demand * x[i])

        mcf += traffic <= capacity
        mcf += z <= capacity - traffic

    # solve
    mcf.writeLP("mcf.lp")
    mcf.solve()

    # calculate hops
    for v in mcf.variables():
        if v.name != 'z' and v.varValue > 0.99:
            flow = var2flow(G, v.name)
            path = label2path[v.name]
            hops = [Hop(dpid=int(a[1:]), port=G.edge[a][b]['port']) 
                                         for a,b in pairwise(path)]
            rules[flow] = hops

    return rules
