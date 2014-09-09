#!/usr/bin/python

"""
Manhattan-style m x n grid, 2 hosts connected to opposite corners
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

import sys


class GridTopo(Topo):
    def __init__(self, m=2, n=6):
        super(GridTopo, self).__init__()

        # Numbering:  h1..N, s1..M
        hostNum = 1
        switchNum = 1

        # Add switches
	switches = []
	for j in range(m):
	    these = []
	    for i in range(n):
		label, opts = self.makeSwitch(i,j)
		these.append(self.addSwitch(label, **opts))
	    switches.append(these)

	# Link switches
        for i,row in enumerate(switches):
            for j,s in enumerate(row):
                r,c = i+1,j+1
                if r < m:
                    self.addLink(switches[i][j], switches[i+1][j])
                if c < n:
                    self.addLink(switches[i][j], switches[i][j+1])

        # Add and link hosts
        hosts = [self.addHost('h{}'.format(i+1)) for i in range(2)]
        self.addLink(hosts[0], switches[0][0])
        self.addLink(hosts[1], switches[m-1][n-1])

    def makeHost(self, i):
	""" Convenience function to make hosts """
	label = 'h{}'.format(i)
	ip = '10.0.0.{}'.format(i)
	return (label, {'ip':ip})

    def makeSwitch(self, r, c):
	""" Convenience function to make switches """
	label = 'sr{0}c{1}'.format(r, c)
	return (label, {})


def create_net(**kwargs):
    m = kwargs.get('m', 2)
    n = kwargs.get('n', 6)
    topo = GridTopo(m, n)
    kwargs['link'] = TCLink
    del kwargs['m']
    del kwargs['n']
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    try:
	m = int(sys.argv[1])
	n = int(sys.argv[2])
    except Exception as e:
	print "usage: grid.py n m"
	exit()

    setLogLevel('output')
    net = create_net(controller=RemoteController, m=m, n=n)
    net.start()
    CLI(net)
    net.stop()
