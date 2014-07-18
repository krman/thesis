#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class FatTreeTopo(Topo):
    def __init__(self, k=4):
	super(FatTreeTopo, self).__init__()

	# core switches: (k/2)^2
	core = []
	for i in range((k/2)**2):
	    r,c = i/(k/2), i%(k/2)
	    label, opts = self.makeCoreSwitch(r,c,k)
	    core.append(self.addSwitch(label, **opts))

	for p in range(k):
	    # aggregation switches: k^2/2
	    aggregation = []
	    for s in range(k/2):
		label, opts = self.makePodSwitch(p,s)
		switch = self.addSwitch(label, **opts)
		aggregation.append(switch)
		[self.addLink(switch,c) for c in core[s:(k/2)**2:k/2]]

	    # edge switches: k^2/2
	    for s in range(k/2, k):
		label, opts = self.makePodSwitch(p,s)
		switch = self.addSwitch(label, **opts)
		[self.addLink(switch,a) for a in aggregation]

		# hosts: k/2 per edge switch
		for i in range(k/2):
		    label, opts = self.makeHost(p,s,i)
		    host = self.addHost(label, **opts)
		    self.addLink(switch, host)

    def makeCoreSwitch(self, i, j, k):
	label = 'cr{0}c{1}'.format(i,j)
	ip = '10.{0}.{1}.{2}'.format(k,i,j)
	return (label, {'ip':ip})

    def makePodSwitch(self, p, s):
	label = 'p{0}s{1}'.format(p,s)
	ip = '10.{0}.{1}.1'.format(p,s)
	return (label, {'ip':ip})

    def makeHost(self, p, s, i):
	label = 'h{2}p{0}s{1}'.format(p,s,i)
	ip = '10.{0}.{1}.{2}'.format(p,s,i)
	return (label, {'ip':ip})


def create_net(k=4, **kwargs):
    topo = FatTreeTopo(k=k)
    kwargs['link'] = TCLink
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = create_net(controller=RemoteController, k=2)
    net.start()
    CLI(net)
    net.stop()
