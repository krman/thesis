#!/usr/bin/python

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController
from topolib import GridNet

if __name__ == '__main__':
    import sys

    try:
	m = int(sys.argv[1])
	n = int(sys.argv[2])
    except Exception:
	print "usage: grid.py n m"
	exit()

    setLogLevel('output')
    net = GridNet(n, m, controller=RemoteController)
    c = net.addController('c0')

    net.start()
    h1 = net.get('h1')
    h2 = net.get('h2')
    h1.cmd('ping {} &'.format(h2.IP()))

    from time import sleep
    sleep(20)
    net.stop()
