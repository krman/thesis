#!/usr/bin/python

""" Simple topology:

h1 -- s1 -- h2

When run directly, starts up a remote pox controller
of my own design and connects to that.
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import lg
from mininet.node import Node, RemoteController
from mininet.link import Link

class SimpleTopo(Topo):
    def __init__(self):
	Topo.__init__(self)

	# add hosts and switches
	h1 = self.addHost('h1')
	h2 = self.addHost('h2')
	s1 = self.addSwitch('s1')

	# link them up
	self.addLink(h1,s1)
	self.addLink(h2,s1)

def startNetwork(network, switch, ip, routes):
    root = Node('root', inNamespace=False)
    intf = Link(root, switch).intf1
    root.setIP(ip, intf=intf)
    network.start()
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )

def makeSimple():
    topo = SimpleTopo()
    network = Mininet(topo, controller=RemoteController)
    return network

def startSimple(network):
    switch = network['s1']
    ip = '10.123.123.1/32'
    routes = ['10.0.0.0/24']
    startNetwork(network, switch, ip, routes)
    CLI(network)
    print "*** Type 'exit' or ctrl-D to shut down network"
    network.stop()

if __name__ == '__main__':
    lg.setLogLevel('info')
    network = makeSimple()
    startSimple(network)
else:
    topos = {'simple': (lambda: SimpleTopo())}
