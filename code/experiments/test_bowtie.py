#!/usr/bin/python

from topos import bowtie
from time import sleep

net = bowtie.makeBowtie()
net.start()
h1 = net.get("h1")
h2 = net.get("h2")
h3 = net.get("h3")
h4 = net.get("h4")
sleep(12) # give everything a chance to connect to the controller
h1.cmd("ping {}&".format(h2.IP()))
h3.cmd("ping {}&".format(h4.IP()))
net.stop()

"""
NOTE
This doesn't work. Timing is off. Switches die too soon.
"""
