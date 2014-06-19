from pulp import *
from pox.lib.addresses import IPAddr
import networkx as nx

def objective(net, flows):
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
    for v in mcf.variables():
	print v.name, "=", v.varValue
    print "z =", value(mcf.objective)
