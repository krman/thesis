import networkx as nx


def base_graph(links):
    UG = nx.Graph()
    UG.add_edges_from(links.keys())
    G = nx.DiGraph(UG)

    for a,b in G.edges():
	try:
	    G.edge[a][b]['port'] = links[(a,b)][0]
	except KeyError:
	    G.edge[a][b]['port'] = links[(b,a)][1]

    return G


def diamond_graph():
    links = {('h1','s1'):(1,1),
	     ('s1','s2'):(2,1),
	     ('s1','s3'):(3,1),
	     ('s2','s4'):(2,2),
	     ('s3','s4'):(2,3),
	     ('s4','h2'):(1,1)}

	G = base_graph(links)

    G.node['h1']['ip'] = '10.0.0.1'
    G.node['h2']['ip'] = '10.0.0.2'
    return G


def pentagon_graph():
    links = {('h1','s1'):(1,1),
	     ('s1','s2'):(2,1),
	     ('s1','s3'):(3,1),
	     ('s2','s5'):(2,2),
	     ('s3','s4'):(1,2),
	     ('s4','s5'):(2,3),
	     ('s5','h2'):(1,1)}

	G = base_graph(links)

    G.node['h1']['ip'] = '10.0.0.1'
    G.node['h2']['ip'] = '10.0.0.2'
    return G
