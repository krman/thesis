#!/usr/bin/python

""" Diamond topology:

         c
         |
         s2
       /    \
h1 -- s1    s4 -- h2
       \    /
         s3

When run directly, connects to remote controller already running
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def makeHost(i):
    # note, there are some issues when i is large (>250 or so)
    label = 'h{}'.format(i)
    ip = '10.0.0.{}'.format(i)
    full = '{:012x}'.format(i)
    mac = ':'.join(full[j:j+2] for j in xrange(0,12,2))
    opts = {'ip':ip, 'mac':mac}
    return (label, opts)


def makeSwitch(i):
    label = 's{}'.format(i)
    return (label, {})


def makeDiamond():
    net = Mininet(controller=RemoteController)
    c = net.addController('c0')

    # add hosts
    hosts = [makeHost(i+1) for i in xrange(2)]
    h = [0] + [net.addHost(label, **opts) for label,opts in hosts]

    # add switches
    switches = [makeSwitch(i+1) for i in xrange(4)]
    s = [0] + [net.addSwitch(label, **opts) for label,opts in switches]

    # link them up
    net.addLink(h[1],s[1])
    net.addLink(h[2],s[4])
    net.addLink(s[1],s[2])
    net.addLink(s[1],s[3])
    net.addLink(s[2],s[4])
    net.addLink(s[3],s[4])

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    makeDiamond()
