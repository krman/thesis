from pulp import *
from pox.lib.addresses import IPAddr
import networkx as nx


def var2fh(var):
    var = var[2:]
    flow, x, hops = var.partition('_')
    hops = hops[1:-1].split(',_')[1:-1]
    flow = tuple(flow.split(','))
    return (flow, hops)


def objective(net, flows):
    print "FLOWS", flows
    net.refresh_network()

    mcf = LpProblem("routes", LpMaximize)

    # objective function
    z = LpVariable("z")
    mcf += z

    # "for all i in P" (per-commodity) constraints
    chosen = {}
    for flow in flows:
	src = net.get_host_from_ip(flow.nw_src)
	dst = net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
	if not (src and dst):
	    continue
	if not (src in net.graph.nodes() and dst in net.graph.nodes()):
	    continue

	paths = list(nx.all_simple_paths(net.graph, src, dst))
	labels = [str(k) for k in paths]

	chosen[(src,dst)] = LpVariable.dicts("x[{0},{1}]".format(src,dst),labels, None, None, 'Binary')
	x = chosen[(src,dst)]
	
	selected = sum([x[str(k)] for k in paths])
	mcf += selected == 1

    # "for all j in E" (per-link) constraints
    for link,capacity in net.get_links().iteritems():
	traffic = 0
	result = 0

	for flow,demand in flows.iteritems():
	    src = net.get_host_from_ip(flow.nw_src)
	    dst = net.get_host_from_ip(IPAddr(flow.nw_dst.split('/')[0]))
	    if not (src and dst):
		continue
	    if not (src in net.graph.nodes() and dst in net.graph.nodes()):
		continue

	    x = chosen[(src,dst)]
	    selected = 0
	    for path in nx.all_simple_paths(net.graph, src, dst):
		edges = zip(path[:-1],path[1:])
		a = 1 if link in edges or (link[1],link[0]) in edges else 0
		traffic += (a * demand * x[str(path)])

	mcf += traffic <= capacity
	mcf += z <= capacity - traffic

    # solve
    mcf.writeLP("mcf.lp")
    mcf.solve()
    print "Status:", LpStatus[mcf.status]

    # plot evil
    rules = {}
    a = net.get_adjacency()
    for v in mcf.variables():
	print v.name, "=", v.varValue
	if v.name != 'z':
	    flow, hops = var2fh(v.name)
	    s,d = flow
	    f = (net.get_ip_from_host(s[1:]), net.get_ip_from_host(d[1:]))
	    real = []
	    for i,s in enumerate(hops):
		dpid = int(s[1:]) # hope and pray
		if i != len(hops)-1:
		    s2 = hops[i+1]
		    dpid2 = int(s2[1:])
		    port = [l.port1 for l in a if l.dpid1==dpid and l.dpid2==dpid2][0]
		else:
		    port = 1
		real.append(net.Hop(dpid=dpid,port=port))
	    rules[f] = real
    print "z =", value(mcf.objective)
    return rules
