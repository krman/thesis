"""
Library of data structures shared across the framework
"""


class EqualityMixin(object):
    """
    Mixin to add equality comparators based on class fields.
    """
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Hop(EqualityMixin):
    """
    A network hop, represented by the source switch and port to exit from.
    """
    def __init__(self, dpid, port):
        self.dpid = dpid
        self.port = port
    
    def __repr__(self):
        return "{0}.{1}".format(self.dpid, self.port)


class Flow(EqualityMixin):
    """
    A network flow, represented by the 5-tuple of information.
    """
    def __init__(self, nw_proto, nw_src, nw_dst, tp_src, tp_dst):
        self.nw_proto = nw_proto
        self.nw_src = nw_src
        self.nw_dst = nw_dst
        self.tp_src = tp_src
        self.tp_dst = tp_dst

    def __repr__(self):
        return "(proto {0}) {1}:{2} -> {3}:{4}".format(self.nw_proto,
                self.nw_src, self.tp_src, self.nw_dst, self.tp_dst)
        

class Entry(EqualityMixin):
    """
    A flow statistics entry, summarising the recent size of a flow.
    """
    def __init__(self, switch, flow):
        self.switch = switch
        self.flow = flow
        self.recent = 0
        self.total = 0

    def __repr__(self):
        return "flow {0} on switch {1}: {2} bytes recently, {3} total".format(
                self.flow, self.switch, self.recent, self.total)


def match_to_flow(match):
    """
    Convert POX representation of statistics match to Flow class, if possible.
    """
    d = match if type(match) == dict else match_to_dict(match)
    try:
        f = { k:d[k] for k in ["nw_proto", "nw_src", "nw_dst", "tp_src", "tp_dst"]}
        f['nw_src'] = str(f['nw_src']).split('/')[0]
        f['nw_dst'] = str(f['nw_dst']).split('/')[0]
        flow = Flow(**f)
        return flow
    except KeyError:
        return None

