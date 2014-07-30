#!/usr/bin/python

from time import sleep

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

from mcfpox.topos import pentagon
from mcfpox.test.objectives.test_shortest_path import pentagon_graph
from mcfpox.experiments.boilerplate import run_experiment, start_pox


@run_experiment
def experiment():
    # Start POX with the dedicated topology test module
    controller = start_pox(module='mcfpox.test.controller.pox_test_topology')
    
    # Start mininet with given topology
    setLogLevel('output')
    net = pentagon.create_net(controller=RemoteController)
    net.start()
    
    # Wait for long enough to discover the network, then die
    sleep(20)
    controller.kill()


class TestTopology:
    def test_empty(self):
	assert 1

    def test_pentagon(self):
	experiment()
	assert 1
