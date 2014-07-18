#!/usr/bin/python

import networkx as nx

def make_core_switch(i, j, k):
    label = 'c{0},{1}'.format(i,j)
    ip = '10.{0}.{1}.{2}'.format(k,i,j)
    return (label, ip)

def make_pod_switch(p, s):
    label = 'p{0},{1}'.format(p,s)
    ip = '10.{0}.{1}.1'.format(p,s)
    return (label, ip)

def make_host(p, s, i):
    label = 'h{0},{1}.{2}'.format(p,s,i+2)
    ip = '10.{0}.{1}.{2}'.format(p,s,i+2)
    return (label, ip)

def fat_tree_graph(k=4):
    G = nx.Graph()

    core = []
    for i in range((k/2)**2):
	r,c = i/(k/2), i%(k/2)
	label, ip = make_core_switch(r,c,k)
	G.add_node(label)
	G.node[label]['ip'] = ip
	core.append(label)

    for p in range(k):
	aggr = []
	for s in range(k/2):
	    label, ip = make_pod_switch(p,s)
	    G.add_node(label)
	    G.node[label]['ip'] = ip
	    aggr.append(label)
	    [G.add_edge(label,c,{'capacity':5}) for c in core[s:(k/2)**2:k/2]]

	for s in range(k/2, k):
	    switch, ip = make_pod_switch(p,s)
	    G.add_node(switch)
	    G.node[switch]['ip'] = ip
	    [G.add_edge(switch,a,{'capacity':5}) for a in aggr]

	    for i in range(k/2):
		host, ip = make_host(p,s,i)
		G.add_node(host)
		G.node[host]['ip'] = ip
		G.add_edge(switch, host,{'capacity':5})

    return G

def get_host_from_ip(G, ip):
    return next((i for i in G.nodes() if G.node[i].get('ip') == str(ip)), None)

if __name__ == '__main__':
    G = fat_tree_graph()
    for n in G.nodes():
	print n,G.node[n]['ip']
    h1 = get_host_from_ip(G, '10.1.3.2')
    h2 = get_host_from_ip(G, '10.3.2.3')
    min = 18
    for path in nx.all_simple_paths(G, h1, h2, cutoff=7):
	print len(path),
	if len(path) < min: 
	    min = len(path)
	    minpath = path
    print minpath

