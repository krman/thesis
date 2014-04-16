#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

import pox.openflow.discovery as discovery

import networkx as nx

log = core.getLogger()


class Multicommodity:
    def __init__(self, period=5, length=1):
	core.openflow.addListeners(self)

    #def _handle_PortStatsReceived(self, event):
	#stats = flow_stats_to_list(event.stats)
	#log.info("port stats: %s" % (stats))
    def 


def launch():
    core.registerNew(Multicommodity)
