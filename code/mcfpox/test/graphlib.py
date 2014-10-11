import networkx as nx
import ipaddr


class Switch:
    def __init__(self, label):
        self.label = label
        self.next_port = 0

    def __repr__(self):
        return self.label

    def add_link(self):
        self.next_port += 1
        return self.next_port



def base_graph(links):
    UG = nx.Graph()
    UG.add_edges_from(links.keys())
    G = nx.DiGraph(UG)

    for a,b in G.edges():
        G.edge[a][b]['capacity'] = 1e6
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


def alfares_graph(k=4):
    dpid = 0
    hcount = 0

    links = {}

    # Add core switches: (k/2)^2
    core = []
    for i in range((k/2)**2):
        r,c = i/(k/2), i%(k/2)
        dpid += 1
        label = "s{0}".format(dpid)
        core.append(Switch(label))

    for p in range(k):
        # Add aggregation switches: k^2/2
        aggregation = []
        for s in range(k/2):
            dpid += 1
            label = "s{0}".format(dpid)
            switch = Switch(label)
            aggregation.append(switch)
            for c in core[s:(k/2)**2:k/2]:
                links[(switch.label,c.label)] = (switch.add_link(),c.add_link())

        # Add edge switches: k^2/2
        for s in range(k/2, k):
            dpid += 1
            label = "s{0}".format(dpid)
            switch = Switch(label)
            for a in aggregation:
                links[(switch.label,a.label)] = (switch.add_link(),a.add_link())

            # Add hosts: k/2 per edge switch
            for i in range(k/2):
                hcount += 1
                label = "h{0}".format(hcount)
                links[(label, switch.label)] = (1, switch.add_link())

    G = base_graph(links)

    base_ip = ipaddr.IPAddress('10.0.0.0')
    for h in range(1, hcount+1):
        label = "h{0}".format(h)
        G.node[label]["ip"] = base_ip + h

    return G
