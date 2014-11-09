#!/usr/bin/python

"""
Statistics-gathering module: track size of flows in the network
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
        """
        Initialise statistics module.
        period: number of seconds between switch statistics requests
        length: window size for moving-window estimation, unused
        """
        self.period = 2.0
        Timer(self.period, self._request_stats, recurring=True)
        self.flows = []
        core.openflow.addListeners(self)


    def _request_stats(self):
        """
        Send OFPT_STATS_REQUEST messages to every known switch.
        """
        for connection in core.openflow._connections.values():
            connection.send(
                    of.ofp_stats_request(body=of.ofp_flow_stats_request()))


    def _handle_FlowStatsReceived(self, event):
        """
        Handle OFPT_STATS_REPLY messages from switches.
        Add a new entry if flow is previously unseen, else update the old.
        """
        stats = flow_stats_to_list(event.stats)
        switch = event.dpid
        local = [e for e in self.flows if e.switch == switch]
        log.info("stats on switch {0}".format(switch))
        log.info(stats)
        
        for flow in stats:
            f = lib.match_to_flow(flow['match'])
            if not f:
                continue

            try:
                entry = next(e for e in local if e.flow == f)
            except StopIteration:
                entry = lib.Entry(switch, f)
                self.flows.append(entry)

            bc = int(flow['byte_count']) * 8  # want everything in bits
            entry.recent = (bc - entry.total) / self.period
            entry.total = bc
            if entry.recent <= 20000:
                self.flows.remove(entry)


    def get_flows(self):
        """
        Combine flows from all switches into single list of (flow,size) pairs.
        """
        self.flows.sort(key=lambda e: e.recent, reverse=True)
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
