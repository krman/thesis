"""
Library of data structures shared in and out of pox
"""

from collections import namedtuple


Flow = namedtuple("Flow", "nw_proto nw_src nw_dst tp_src tp_dst")
Hop = namedtuple("Hop", "dpid port")
Entry = namedtuple("Entry", "switch id recent total")


def match_to_flow(self, match):
    d = match if type(match) == dict else match_to_dict(match)
    try:
	f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
	flow = Flow(**f)
	return flow
    except KeyError:
	return None

