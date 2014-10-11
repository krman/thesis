#!/usr/bin/python

"""
The fat-tree/Clos network topology, described in
http://ccr.sigcomm.org/online/files/p63-alfares.pdf
Parametrised by k, the number of ports per switch
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class AlFaresTopo(Topo):
    def __init__(self, k=4):
        super(AlFaresTopo, self).__init__()

        dpid = 0
        hcount = 0

        # Add core switches: (k/2)^2
        core = []
        for i in range((k/2)**2):
            r,c = i/(k/2), i%(k/2)
            dpid += 1
            label = "s{0}".format(dpid)
            core.append(self.addSwitch(label))

        for p in range(k):
            # Add aggregation switches: k^2/2
            aggregation = []
            for s in range(k/2):
                dpid += 1
                label = "s{0}".format(dpid)
                switch = self.addSwitch(label)
                aggregation.append(switch)
                [self.addLink(switch,c) for c in core[s:(k/2)**2:k/2]]

            # Add edge switches: k^2/2
            for s in range(k/2, k):
                dpid += 1
                label = "s{0}".format(dpid)
                switch = self.addSwitch(label)
                [self.addLink(switch,a) for a in aggregation]

                # Add hosts: k/2 per edge switch
                for i in range(k/2):
                    hcount += 1
                    label = "h{0}".format(hcount)
                    host = self.addHost(label)
                    self.addLink(switch, host)



def create_net(k=4, **kwargs):
    topo = AlFaresTopo(k=k)
    kwargs['link'] = TCLink
    return Mininet(topo, **kwargs)


if __name__ == "__main__":
    setLogLevel('output')
    net = create_net(controller=RemoteController, k=4)
    net.start()
    CLI(net)
    net.stop()
