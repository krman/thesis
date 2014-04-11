#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

log = core.getLogger()


class Statistics:
    def __init__(self, period=5, window=1):
	Timer(period, self._request_stats, recurring=True)
	core.openflow.addListeners(self)

    def _request_stats(self):
	for connection in core.openflow._connections.values():
	    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
	    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def _handle_FlowStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	log.info("flow stats: %s" % (stats))

    def _handle_PortStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	log.info("port stats: %s" % (stats))



def launch(period=5, window=1):
    core.registerNew(Statistics, period=period, window=window)
