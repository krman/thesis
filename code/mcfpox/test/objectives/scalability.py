#/usr/bin/python

import random
import ipaddr
import time

from mcfpox.test.graphlib import alfares_graph
from mcfpox.objectives.shortest_path import objective
from mcfpox.controller.lib import Flow


P_EDGE = 0.1
P_POD = 0.3
P_OTHER = 1 - P_EDGE - P_POD


def categories(n):
    hpe = k/2
    if k > 2:
        div = n/hpe
        same_edge = [i for i in range(div*hpe, (div+1)*hpe) if i != n]
        div = n/k
        same_pod = [i for i in range(div*k, (div+1)*k) if i != n]
    else:
        same_edge = []
        same_pod = []

    div = n/k
    seen = same_edge + same_pod + [n]
    others = [i for i in range(k**3/4) if i not in seen]

    return same_edge, same_pod, others


def gen_flows(k):
    num_hosts = k**3 / 4
    base_ip = ipaddr.IPAddress("10.0.0.1")
    port = 5001
    
    flows = []
    for n in random.sample(range(num_hosts), 16):
        same_edge, same_pod, others = categories(n)

        if k > 2:
            which = random.random()
        else:
            which = 1

        if which < P_EDGE:
            options = same_edge
        elif which < P_POD:
            options = same_pod
        else:
            options = others

        nw_src = base_ip + n
        nw_dst = base_ip + random.choice(options)
        tp_src = port
        tp_dst = port + 1
        
        port = port + 2

        f = Flow(6, str(nw_src), str(nw_dst), tp_src, tp_dst)
        flows.append((f, 1000))

    return flows



for k in range(4,51,2):
    max_paths = (k**3) * (1 + (k/2-1)**2 + (k/2-1)*(k-1))
    print "k =", k, "max paths =", max_paths
    graph = alfares_graph(k)
    for i in range(15):
        flows = gen_flows(k)
        start = time.clock()
        objective(graph, flows)
        end = time.clock()
        print end - start
