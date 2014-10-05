#!/usr/bin/python

from mcfpox.topos import fat_tree
from mcfpox.objectives import shortest_path, max_spare_capacity
from boilerplate import start

import os
import json
import matplotlib.pyplot as plt
import itertools


def experiment():

    hosts = ['h{0}'.format(i+1) for i in range(8)]
    pairs = itertools.combinations(hosts, 2)
    flows = {
	15: [(i,j,'4m') for i,j in pairs]
    }

    for module in [shortest_path]:
	net = fat_tree.create_net()

	scenario = {
	    'net': net,
	    'flows': flows
	}

	controller = {
	    'objective': module.objective
	}

	logs = start(scenario, controller)
	print module.__name__
	results(logs)


def results(logs):
    log_dir = logs['log_dir']
    sent = []
    recv = []

    for slog, clog in logs['flows']:
	server_log = os.path.join(log_dir, slog)
	client_log = os.path.join(log_dir, clog)

	with open(client_log, 'r') as f:
	    j = json.load(f)
	    s = j['end']['sum_sent']['bits_per_second']
	    r = j['end']['sum_received']['bits_per_second']
	    sent.append(s)
	    recv.append(r)

    print sent
    print recv

    print "Average sent:", sum(sent)/len(sent)
    print "Average recv:", sum(recv)/len(recv)


if __name__ == '__main__':
    experiment()
