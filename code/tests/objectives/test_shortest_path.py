from thesis.experiments.objectives.shortest_path import objective
from thesis.controllers.lib import Flow, Hop
import networkx as nx


class TestShortestPath:

    def pentagon_graph(self):
	links = {('h1','s1'):(1,1),
		 ('s1','s2'):(2,1),
		 ('s1','s4'):(3,1),
		 ('s2','s3'):(2,1),
		 ('s3','s5'):(2,2),
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


    def test_empty_graph_empty_flows(self):
	assert objective(nx.Graph(), {}) == {}


    def test_empty_graph_one_flow(self):
	f = Flow(nw_proto=6, nw_src='10.0.0.1', nw_dst='10.0.0.2',
		 tp_src=5001, tp_dst=5002)
	assert objective(nx.Graph(), {f: 1e6}) == {}


    def test_valid_graph_empty_flows(self):
	assert objective(self.pentagon_graph(), {}) == {}
