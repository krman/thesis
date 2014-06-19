#!/usr/bin/python

""" Diamond topology:

         c
         |
         s2
       /    \
h1 -- s1    s4 -- h2
       \    /
         s3

"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class DiamondTopo(Topo):
    def __init__(self):
	super(DiamondTopo, self).__init__()
	
	# add hosts
	hosts = [self.makeHost(i+1) for i in xrange(2)]
	h = [0] + [self.addHost(label, **opts) for label,opts in hosts]

	# add switches
	switches = [self.makeSwitch(i+1) for i in xrange(4)]
	s = [0] + [self.addSwitch(label, **opts) for label,opts in switches]

	# link them up
	linkopts = dict(bw=1)
	self.addLink(h[1],s[1], **linkopts)
	self.addLink(h[2],s[4], **linkopts)
	self.addLink(s[1],s[2], **linkopts)
	self.addLink(s[1],s[3], **linkopts)
	self.addLink(s[2],s[4], **linkopts)
	self.addLink(s[3],s[4], **linkopts)

    def makeHost(self, i):
	label = 'h{}'.format(i)
	ip = '10.0.0.{}'.format(i)
	return (label, {'ip':ip})

    def makeSwitch(self, i):
	label = 's{}'.format(i)
	return (label, {})


def DiamondNet(**kwargs):
    topo = DiamondTopo()
    kwargs['link'] = TCLink
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = DiamondNet(controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()
