#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from collections import deque, namedtuple

log = core.getLogger()

Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")

class Entry:
    def __init__(self, switch, id, recent=0, total=0):
	self.switch = switch
	self.id = id
	self.recent = recent
	self.total = total

    def __repr__(self):
	return "Flow on switch {0}, matching {1} with {2} bytes total, {3} bytes/sec recently".format(self.switch, self.id, self.total, self.recent)

    def __str__(self):
	return self.__repr__()

class Statistics:
    _core_name = "thesis_stats"
    Entry = Entry
    Flow = Flow

    def __init__(self, period=5, length=1):
	#Timer(period, self._update_time, recurring=True)
	#Timer(period, self._request_stats, recurring=True)
	self.window = deque([0]*length)
	self.time = 0
	self.flows = []
	self.period = float(period)
	core.openflow.addListeners(self)

    def _update_time(self):
	self.time += self.period

    def _request_stats(self):
	for connection in core.openflow._connections.values():
	    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

    def _handle_FlowStatsReceived(self, event):
	stats = flow_stats_to_list(event.stats)
	switch = event.dpid
	local = [e for e in self.flows if e.switch == switch]
	
	for flow in stats:
	    if flow['match']['dl_type'] == 'IP':
		log.info("switch {0}, src {1}, output on port {2}".format(event.dpid, flow['match']['nw_src'], flow['actions'][0]['port']))
	    id = core.thesis_mcf.match_to_flow(flow['match'])
	    if not id: continue

	    try:
		entry = next(e for e in local if e.id == id)
	    except StopIteration:
		entry = Entry(switch, id)
		self.flows.append(entry)
	    bc = int(flow['byte_count'])

	    entry.recent = (bc - entry.total) / self.period
	    entry.total = bc

    def get_flows(self):
	return self.flows


def launch(period=5, length=1):
    core.registerNew(Statistics, period=period, length=length)
