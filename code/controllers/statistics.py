#!/usr/bin/python

"""
Statistics-gathering module: stats for ports, flows and queues (eventually)
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from collections import deque

from lib import *

log = core.getLogger()

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

    def match_to_flow(self, match):
        d = match if type(match) == dict else match_to_dict(match)
        try:
            f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
            flow = core.thesis_topo.Flow(**f)
            return flow
        except KeyError:
            return None

    def get_flows(self):
	return self.flows

    def get_fake_flows(self):
	f = [(6, '10.0.0.1', '10.0.0.2', None, 5001),
	     (6, '10.0.0.1', '10.0.0.2', None, 5002),
	     (6, '10.0.0.2', '10.0.0.1', None, 5003),
	     (6, '10.0.0.2', '10.0.0.1', None, 5004)]

	f = [(None, '10.0.0.1', '10.0.0.2', None, None),
	     (None, '10.0.0.2', '10.0.0.1', None, None)]
	d = {Flow(nw_proto=p, nw_src=ns, nw_dst=nd, tp_src=ts, tp_dst=td):2e5
		for p,ns,nd,ts,td in f}
	return d


def launch(period=5, length=1):
    core.registerNew(Statistics, period=period, length=length)
