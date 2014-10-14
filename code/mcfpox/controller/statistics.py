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
        log.info("REQUESTING STATS")
        for connection in core.openflow._connections.values():
            connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))


    def _handle_FlowStatsReceived(self, event):
        stats = flow_stats_to_list(event.stats)
        log.info("GOT STATS")
        #log.info(stats)
        switch = event.dpid
        local = [e for e in self.flows if e.switch == switch]
        
        for flow in stats:
            f = lib.match_to_flow(flow['match'])
            #log.info("{0} became {1}".format(flow,f))
            if not f:
                continue

            try:
                entry = next(e for e in local if e.flow == f)
                log.info("just getting old entry for {0}".format(f))
            except StopIteration:
                log.info("making a new entry for {0}".format(f))
                entry = lib.Entry(switch, f)
                self.flows.append(entry)

            bc = int(flow['byte_count'])
            log.info("old total: {0}, new total: {1}, diff: {2}, recent: {3}".format(entry.total, bc, bc-entry.total, (bc-entry.total)/self.period))
            entry.recent = (bc - entry.total) / self.period
            entry.total = bc
            #if entry.recent <= 0:
                #self.flows.remove(entry)


    def get_flows(self):
        flows = [e.flow for e in self.flows if e.recent]
        overall = []
        seen = []
        for f in flows:
            g = lib.Flow(f.nw_proto, f.nw_dst, f.nw_src, f.tp_dst, f.tp_src)
            if f in seen or g in seen:
                continue
            s = [e.recent for e in self.flows if e.flow == f]
            overall.append((f,max(s)))
            seen.append(f)
        log.info(overall)
        return overall



def launch(period=5, length=1):
    core.registerNew(Statistics, period=period, length=length)
