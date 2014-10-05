#!/usr/bin/python

from mcfpox.topos import diamond
from mcfpox.objectives import shortest_path, max_spare_capacity
from boilerplate import start

import os
import json
import matplotlib.pyplot as plt
import itertools


def experiment(bw, module):
	pairs = [('h1','h2')]
	flows = {
		15: [(i,j,bw) for i,j in pairs]
	}

	net = diamond.create_net()

	scenario = {
		'net': net,
		'flows': flows
	}

	controller = {
		'objective': module.objective
	}

	logs = start(scenario, controller)
	return results(logs)


def results(logs):
	log_dir = logs['log_dir']
	recv = []

	for slog, clog in logs['flows']:
		server_log = os.path.join(log_dir, slog)
		client_log = os.path.join(log_dir, clog)

	with open(client_log, 'r') as f:
		try:
			j = json.load(f)
			r = j['end']['sum_received']['bits_per_second']
			recv.append(r)
		except ValueError:
			recv.append(0)

	return recv


if __name__ == '__main__':
	sp = [0]
	msc = [0]
	bw = [0]

	for i in [1,5,10,20]:
		j = '{0}m'.format(i)
		recv = experiment(j, shortest_path)
		sp.append(sum(recv))
		recv = experiment(j, max_spare_capacity)
		msc.append(sum(recv))
		bw.append(i)

	print bw
	print sp
	print msc

	done = False
	while not done:
		try:
			plt.figure()
			plt.plot(bw, [i/1e6 for i in sp], 'g-o', label='Shortest path')
			plt.plot(bw, [i/1e6 for i in msc], 'b-o', label='Max spare capacity')
			plt.axis(eval(raw_input("axis? ")))
			#plt.xlabel(raw_input("xlabel? "))
			#plt.ylabel(raw_input("ylabel? "))
			plt.xlabel("Aggregate offered load (Mbps)")
			plt.ylabel("Aggregate throughput (Mbps)")
			plt.title(raw_input("title? "))
			plt.legend()
			plt.show()
		except Exception:
			done = False
			continue

		ask = raw_input("done yet? ")
		if ask == "y":
			done = True
