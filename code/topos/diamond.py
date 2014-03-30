#!/usr/bin/python

""" Diamond topology:

         c
         |
         s2
       /    \
h1 -- s1    s3 -- h2
       \    /
         s4

When run directly, connects to remote controller already running
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import lg
from mininet.node import Node, RemoteController
from mininet.util import dumpNodeConnections
from mininet.link import Link

class DiamondTopo(Topo):
    def __init__(self):
	Topo.__init__(self)

	# add hosts and switches
	h = [self.addHost('h{}'.format(i+1)) for i in xrange(2)]
	s = [self.addSwitch('s{}'.format(i+1)) for i in xrange(4)]

	# link them up
	self.addLink('h1','s1')
	self.addLink('h2','s3')

def makeDiamond():
    topo = DiamondTopo()
    network = Mininet(topo, controller=RemoteController)
    return network

def testDiamond(net):

    # configure network
    switch = net['s1']
    ip = '10.123.123.1/32'
    routes = ['10.0.0.0/24']

    # start network
    root = Node('root', inNamespace=False)
    intf = Link(root, switch).intf1
    root.setIP(ip, intf=intf)
    net.start()
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )

    # start tests
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    #net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    lg.setLogLevel('info')
    net = makeDiamond()
    testDiamond(net)
else:
    topos = {'diamond': (lambda: DiamondTopo())}
