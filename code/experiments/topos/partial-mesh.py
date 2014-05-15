#!/usr/bin/python

from mininet.cli import CLI
from mininet.log import setLogLevel
from topolib import PartialMeshNet

if __name__ == '__main__':
    setLogLevel('output')
    net = PartialMeshNet(n=6, m=2, p=30)
    net.start()
    CLI(net)
    net.stop()
