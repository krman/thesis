#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import flow_stats_to_list
from collections import namedtuple

import mcfpox.controller.lib as lib

log = core.getLogger()


class Statistics:
    _core_name = "thesis_stats"

    def __init__(self, period=5, length=1):
	Timer(period, self._request_stats, recurring=True)
	self.flows = []
	self.period = float(period)
	core.openflow.addListeners(self)

    def _request_stats(self):
	for connection in core.openflow._connections.values():
	    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

    def _handle_FlowStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	switch = event.dpid
	local = [e for e in self.flows if e.switch == switch]
	
	for flow in stats:
	    if flow['match']['dl_type'] == 'IP':
		#log.info("switch {0}, src {1}, output on port {2}".format(event.dpid, flow['match']['nw_src'], flow['actions'][0]['port']))
		pass
	    id = lib.match_to_flow(flow['match'])
	    if not id: continue

	    try:
		entry = next(e for e in local if e.id == id)
	    except StopIteration:
		entry = lib.Entry(switch, id, 0, 0)
		self.flows.append(entry)
	    bc = int(flow['byte_count'])

	    entry.recent = (bc - entry.total) / self.period
	    entry.total = bc

    def get_flows(self):
	return self.flows


def launch(period=5, length=1):
    core.registerNew(Statistics, period=period, length=length)
