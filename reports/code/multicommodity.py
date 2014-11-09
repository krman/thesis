#!/usr/bin/python

"""
Multicommodity flow module: route flows according to an objective function
"""

from pox.core import core
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from pox.lib.addresses import IPAddr

from mcfpox.controller import topology
from mcfpox.controller.lib import Flow, Hop, Entry
from mcfpox.objectives import shortest_path

from collections import namedtuple
import time

log = core.getLogger()

        
class Multicommodity:
    _core_name = "thesis_mcf"


    def __init__(self, objective, preinstall):
        """
        Initialise multicommodity module.
        objective: objective function for calculating routes
        preinstall: list of flow rules to preinstall on switches
        """
        Timer(30, self._update_flows)

        self.flows = {}
        self.net = core.thesis_topo
        self.stats = core.thesis_stats
        self.objective = objective

        self.preinstall = preinstall
        self.log_rules = False
        self.done = False

        core.openflow.addListeners(self)
        core.addListeners(self)


    def _handle_PacketIn(self, event):
        """
        Handle arrival of new flow.
        Install routes in both directions using the shortest path metric.
        """
        try:
            if self.done:
                return
            self.net.refresh_network()
            packet = event.parsed
            if packet.find('tcp'):
                ip = packet.next
                tcp = ip.next
                if str(ip.srcip) != '0.0.0.0':
                    log.info("packetin {1}:{3} to {2}:{4} at {0}".format(
                            time.clock(), str(ip.srcip), str(ip.dstip),
                            tcp.srcport, tcp.dstport))
                    there = Flow(6, str(ip.srcip), str(ip.dstip), 
                            tcp.srcport, tcp.dstport)
                    back = Flow(6, str(ip.dstip), str(ip.srcip), 
                            tcp.dstport, tcp.srcport)
                    rules = shortest_path.objective(self.net.graph,
                            [(back,0), (there,0)])
                    self._install_rule_list(rules)
        except Exception as e:
            print str(e)


    def _install_forward_rule(self, msg, hops):
        """
        Install forwarding rule for all ports listed in hops.
        """
        for switch in hops:
            msg.actions = []
            msg.actions.append(of.ofp_action_output(port = switch.port))
            if self.log_rules:
                print "{0}.{1}".format(switch.dpid, switch.port),
            core.thesis_base.switches[switch.dpid].connection.send(msg)
        if self.log_rules:
            print


    def _install_rule_list(self, rules):
        """
        Install forwarding rules for all flows listed in rules.
        """
        for flow,hops in rules.items():
            msg = of.ofp_flow_mod()
            msg.command = of.OFPFC_MODIFY
            msg.match.dl_type = 0x800
            msg.match.nw_proto = 6
            msg.match.nw_src = flow.nw_src
            msg.match.nw_dst = flow.nw_dst
            msg.match.tp_src = int(flow.tp_src)
            msg.match.tp_dst = int(flow.tp_dst)
            if self.log_rules:
                print "Installing rule for {0}:".format(flow, time.clock()),
            self._install_forward_rule(msg, hops)
        

    def _preinstall_rules(self):
        """
        Log and then install preinstall rule list.
        """
        log.info("Preinstalling rules...")
        log.info("Rules are:")
        log.info(self.preinstall)
        self._install_rule_list(self.preinstall)


    def _solve_mcf(self):
        """
        Recalculate routes using the provided objective, then install them.
        """
        self.log_rules = True
        log.info("Flows are " + str(self.flows))
        print "Starting objective with flows:"
        for flow, demand in self.flows:
            print "{0}: {1:.2f} Mbps".format(flow, demand/1e6)
        rules = self.objective(self.net.graph, self.flows)
        log.info("Rules are " + str(rules))
        print
        self._install_rule_list(rules)
        self.done = True


    def _update_flows(self):
        """
        Update view of network and statistics, then begin recalculating routes.
        """
        self.net.refresh_network()
        self.flows = self.stats.get_flows()
        self._solve_mcf()



def default_objective(net, flows):
    print "Default objective function, given:"
    print "net:", net
    print "flows:", flows



def launch(objective=default_objective, pre={}):
    core.registerNew(Multicommodity, objective=objective, preinstall=pre)
