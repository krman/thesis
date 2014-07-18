#!/usr/bin/python

""" Diamond topology
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class DiamondTopo(Topo):
    """ This is the DiamondTopo class """

    def __init__(self):
	""" This creates it """
	super(DiamondTopo, self).__init__()
	
	# add hosts
	hosts = [self.makeHost(i+1) for i in xrange(2)]
	h = [0] + [self.addHost(label, **opts) for label,opts in hosts]

	# add switches
	switches = [self.makeSwitch(i+1) for i in xrange(4)]
	s = [0] + [self.addSwitch(label, **opts) for label,opts in switches]

	# link them up
	linkopts = dict(bw=10)
	self.addLink(h[1],s[1], **linkopts)
	self.addLink(h[2],s[4], **linkopts)
	self.addLink(s[1],s[2], **linkopts)
	self.addLink(s[1],s[3], **linkopts)
	self.addLink(s[2],s[4], **linkopts)
	self.addLink(s[3],s[4], **linkopts)

    def makeHost(self, i):
	""" Convenience function to make hosts """
	label = 'h{}'.format(i)
	ip = '10.0.0.{}'.format(i)
	return (label, {'ip':ip})

    def makeSwitch(self, i):
	""" Convenience function to make switches """
	label = 's{}'.format(i)
	return (label, {})


def create_net(**kwargs):
    topo = DiamondTopo()
    kwargs['link'] = TCLink
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = create_net(controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()
