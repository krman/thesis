#!/usr/bin/python

"""
exp 0
Is it faster to:
 - install a flow table rule (ofp_flow_mod), or
 - have the controller send on packets manually (ofp_packet_out)?
"""

from topos import diamond
from time import sleep

net = diamond.makeDiamond()
net.start()
h1 = net.get("h1")
h2 = net.get("h2")
sleep(15) # give everything a chance to connect to the controller
print h1.cmd("ping -c10 {}".format(h2.IP()))
net.stop()
