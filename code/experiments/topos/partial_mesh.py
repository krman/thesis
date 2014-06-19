#!/usr/bin/python

"""
Partial mesh topology with n switches, m hosts, p% connected switches
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

import random

class PartialMeshTopo(Topo):
    def __init__(self, n=6, m=2, p=30):
        super(PartialMeshTopo, self).__init__()

        # Numbering:  h1..N, s1..M
        hostNum = 1
        switchNum = 1

        # Add and link switches
	switches = [self.addSwitch('s{}'.format(i+1)) for i in range(n)]
	for s1 in switches:
	    sel = int(round(n*(p/100.0)) / 2)
	    dist = [1]*sel + [0]*(n-sel)
	    random.shuffle(dist)
	    for i,s2 in enumerate(switches):
		if dist[i]:
		    t1,t2 = s1,s2
		    if s1 == s2:
			try:
			    t2 = switches[i+1]
			except Exception:   # i+1 is too big
			    t2 = switches[i-1]
		    self.addLink(t1,t2)
	
	# Add and link hosts
	hosts = [self.addHost('h{}'.format(i+1)) for i in range(m)]
	dist = [1]*m + [0]*(n-m)
	random.shuffle(dist)
	a = [i for i,s in enumerate(dist) if s]
	for h,s in enumerate(a):
	    self.addLink(hosts[h],switches[s])
	    
	    
def PartialMeshNet(n=6, m=2, p=30, **kwargs):
    topo = PartialMeshTopo(n, m, p)
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = PartialMeshNet(n=6, m=2, p=70, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()
