from mcfpox.objectives.widest_path import objective
from mcfpox.controller.lib import Flow, Hop
from mcfpox.test.graphlib import diamond_graph
import networkx as nx


def uneven_diamond_graph():
    G = diamond_graph()
    for a,b in [('s1','s3'), ('s3','s4')]:
        G.edge[a][b]['capacity'] /= 2
        G.edge[b][a]['capacity'] /= 2
    return G


class TestShortestWidestPath:
    def test_empty_graph_empty_flows(self):
        assert objective(nx.Graph(), []) == {}

    def test_empty_graph_one_flow(self):
        f = Flow(nw_proto=6, nw_src='10.0.0.1', nw_dst='10.0.0.2',
                 tp_src=5001, tp_dst=5002)
        assert objective(nx.Graph(), [(f,1e6)]) == {}

    def test_valid_graph_empty_flows(self):
        assert objective(uneven_diamond_graph(), []) == {}

    def test_diamond_graph_two_flows(self):
        G = uneven_diamond_graph()
        f1 = Flow(6, '10.0.0.1', '10.0.0.2', 5001, 5002)
        f2 = Flow(6, '10.0.0.2', '10.0.0.1', 5003, 5004)
        expected = {
            f1: [Hop(1,3), Hop(3,2), Hop(4,1)], 
            f2: [Hop(4,2), Hop(2,1), Hop(1,1)]
        }
        assert objective(G, [(f1,0.5e6), (f2,0.75e6)]) == expected
