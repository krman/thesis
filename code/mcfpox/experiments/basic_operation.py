#!/usr/bin/python

from mcfpox.topos import diamond
from mcfpox.objectives import shortest_path
from boilerplate import start

import os
import json
import matplotlib.pyplot as plt


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

    logs = start(scenario, controller)
    results(logs)


def results(logs):
    log_dir = logs['log_dir']
    for slog, clog in logs['flows']:
	server_log = os.path.join(log_dir, slog)
	client_log = os.path.join(log_dir, clog)
	
	print "Client log:", client_log
	with open(client_log, 'r') as f:
	    for line in f:
		print line,
	print


if __name__ == '__main__':
    experiment()
