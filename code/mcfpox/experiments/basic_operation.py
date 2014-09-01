#!/usr/bin/python

from mcfpox.topos import diamond
from mcfpox.objectives import shortest_path
from boilerplate import start

import matplotlib.pyplot as plt
import json


def experiment():
    net = diamond.create_net()

    flows = {
	13: [
	    ('h2', 'h1', '3m')
	],
	15: [
	    ('h1', 'h2', '4m'),
	    ('h2', 'h1', '4m')
	]
    }

    scenario = {
	'net': net,
	'flows': flows
    }

    controller = {
	'objective': shortest_path.objective
    }

    start(scenario, controller)


if __name__ == '__main__':
    experiment()
