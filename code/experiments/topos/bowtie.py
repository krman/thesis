#!/usr/bin/python

""" Bowtie topology:
    
		h1
		|
         s1     s2
        / | \  /
h2 -- s3  |  s4 -- h5 -- h3
          | /  \
         s6     s7
	  |
	 h4

When run directly, connects to remote controller already running
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


def makeHost(i):
    label = 'h{}'.format(i)
    ip = '10.0.0.{}'.format(i)
    return (label, {'ip':ip})


def makeSwitch(i):
    label = 's{}'.format(i)
    return (label, {})


def makeBowtie():
    net = Mininet(controller=RemoteController)
    c = net.addController('c0')

    # add hosts
    hosts = [makeHost(i+1) for i in xrange(4)]
    h = [0] + [net.addHost(label, **opts) for label,opts in hosts]

    # add switches
    switches = [makeSwitch(i+1) for i in xrange(7)]
    s = [0] + [net.addSwitch(label, **opts) for label,opts in switches]

    # link them up
    TCLink(h[1],s[1], bw=1)
    TCLink(h[2],s[3], bw=1)
    TCLink(h[3],s[5], bw=1)
    TCLink(h[4],s[7], bw=1)

    TCLink(s[1],s[2], bw=1)
    TCLink(s[1],s[4], bw=1)
    TCLink(s[1],s[6], bw=1)
    TCLink(s[2],s[5], bw=1)
    TCLink(s[2],s[7], bw=1)
    TCLink(s[3],s[4], bw=1)
    TCLink(s[3],s[6], bw=1)
    TCLink(s[4],s[5], bw=1)
    TCLink(s[4],s[7], bw=1)
    TCLink(s[6],s[7], bw=1)

    return net


if __name__ == '__main__':
    setLogLevel('output')
    net = makeBowtie()
    net.start()
    #CLI(net)
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h1.cmd('ping {} &'.format(h4.IP()))
    h2.cmd('ping {} &'.format(h3.IP()))

    from time import sleep
    sleep(20)

    net.stop()
