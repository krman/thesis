from mcfpox.objectives.longest_path import objective
from mcfpox.controller.lib import Flow, Hop
import networkx as nx

def pentagon_graph():
    links = {('h1','s1'):(1,1),
	     ('s1','s2'):(2,1),
	     ('s1','s3'):(3,1),
	     ('s2','s5'):(2,2),
	     ('s3','s4'):(2,1),
	     ('s4','s5'):(2,3),
	     ('s5','h2'):(1,1)}

    UG = nx.Graph()
    UG.add_edges_from(links.keys())
    G = nx.DiGraph(UG)

    for a,b in G.edges():
	try:
	    G.edge[a][b]['port'] = links[(a,b)][0]
	except KeyError:
	    G.edge[a][b]['port'] = links[(b,a)][1]

    G.node['h1']['ip'] = '10.0.0.1'
    G.node['h2']['ip'] = '10.0.0.2'
    return G


class TestLongestPath:
    def test_empty_graph_empty_flows(self):
	assert objective(nx.Graph(), {}) == {}

    def test_empty_graph_one_flow(self):
	f = Flow(nw_proto=6, nw_src='10.0.0.1', nw_dst='10.0.0.2',
		 tp_src=5001, tp_dst=5002)
	assert objective(nx.Graph(), {f: 1e6}) == {}

    def test_valid_graph_empty_flows(self):
	assert objective(pentagon_graph(), {}) == {}

    def test_pentagon_graph_two_flows(self):
	G = pentagon_graph()
	f1 = Flow(6, '10.0.0.1', '10.0.0.2', 5001, 5002)
	f2 = Flow(6, '10.0.0.2', '10.0.0.1', 5003, 5004)
	expected = {
	    f1: [Hop(1,3), Hop(3,2), Hop(4,2), Hop(5,1)], 
	    f2: [Hop(5,3), Hop(4,1), Hop(3,1), Hop(1,1)]
	}
	assert objective(G, {f1: 1e6, f2: 1e6}) == expected
