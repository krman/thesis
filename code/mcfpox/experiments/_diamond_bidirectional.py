#!/usr/bin/python

from mcfpox.topos import diamond
from mcfpox.objectives import shortest_path, max_spare_capacity
from boilerplate import start

import os
import json
import matplotlib.pyplot as plt
import itertools


def experiment(bw, module):
	pairs = [('h1','h2'), ('h2','h1')]
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
	sum_sp = [0]
	sum_msc = [0]
	bw = [0]

	for i in [1,5,10,20]:
		j = '{0}m'.format(i)
		recv = experiment(j, shortest_path)
		sum_sp.append(sum(recv))
		#recv = experiment(j, max_spare_capacity)
		#sum_msc.append(sum(recv))
		bw.append(i*2)

	for sp,msc in [(sum_sp,sum_msc)]:
		plt.figure()
		plt.plot(bw, [i/1e3 for i in sp], 'g-o', label='Shortest path')
		#plt.plot(bw, [i/1e3 for i in msc], 'b-o', label='Max spare capacity')
		plt.axis([0,3000,0,3000])
		plt.xlabel('Aggregate offered load (kbps)')
		plt.ylabel('Aggregate throughput (kbps)')
		plt.title('All flows, equal offered load')
		plt.legend()
		plt.show()

