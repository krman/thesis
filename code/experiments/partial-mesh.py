#!/usr/bin/python

import subprocess
import signal
import sys

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController
from topos.partial_mesh import PartialMeshNet

def startup():
    subprocess.Popen(['./controller.sh', 'start'])

def cleanup(signal, frame):
    subprocess.Popen(['./controller.sh', 'stop'])
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
startup()

setLogLevel('output')
net = PartialMeshNet(n=6, m=2, p=70, controller=RemoteController)
c = net.addController('c0')

net.start()
h1 = net.get('h1')
h2 = net.get('h2')
h1.cmd('ping {} &'.format(h2.IP()))

from time import sleep
sleep(20)
net.stop()

