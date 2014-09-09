#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class FatTreeTopo(Topo):
    def __init__(self):
        super(FatTreeTopo, self).__init__()
	self.dpid_count = 1
	print "dpid: label"

        # Create hosts
	h = [0]
	for i in range(1,9):
	    label, opts = self.makeHost(i)
	    h.append(self.addHost(label, **opts))

        # Create switches
	s = [0]
	for i in range(1,8):
	    label, opts = self.makeSwitch(i)
	    s.append(self.addSwitch(label, **opts))
       
        # Connect hosts to switches 
	self.addLink(h[1], s[4])
	self.addLink(h[2], s[4])
	self.addLink(h[3], s[5])
	self.addLink(h[4], s[5])
	self.addLink(h[5], s[6])
	self.addLink(h[6], s[6])
	self.addLink(h[7], s[7])
	self.addLink(h[8], s[7])

        # Connect switches to switches
	self.addLink(s[1], s[2])
	self.addLink(s[1], s[3])
	self.addLink(s[2], s[4])
	self.addLink(s[2], s[5])
	self.addLink(s[2], s[6])
	self.addLink(s[2], s[7])
	self.addLink(s[3], s[4])
	self.addLink(s[3], s[5])
	self.addLink(s[3], s[6])
	self.addLink(s[3], s[7])

    def addSwitch(self, label, **opts):
        print "dpid {0}: {1}".format(self.dpid_count, label)
        self.dpid_count += 1
        return super(FatTreeTopo, self).addSwitch(label, **opts)

    def makeSwitch(self, i):
        label = 's{0}'.format(i)
        ip = '10.1.0.{0}'.format(i)
        mac = 'aa:00:00:00:00:{0:02d}'.format(i)
        return (label, {'ip':ip, 'mac':mac})

    def addHost(self, label, **opts):
        print "{0}: {1}".format(label, opts['ip'])
        return super(FatTreeTopo, self).addSwitch(label, **opts)

    def makeHost(self, i):
        label = 'h{0}'.format(i)
        ip = '10.0.0.{0}'.format(i)
        mac = 'ff:00:00:00:00:{0:02d}'.format(i)
        return (label, {'ip':ip, 'mac':mac})




def create_net(**kwargs):
    topo = FatTreeTopo()
    kwargs['link'] = TCLink
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = create_net(controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()
