#!/usr/bin/python

from mcfpox.topos import fat_tree
from mcfpox.objectives import shortest_path, max_spare_capacity
from boilerplate import start

import os
import json
import matplotlib.pyplot as plt
import itertools


def experiment(bw, module):
    pairs = [('h1','h7'), ('h2','h8')]
    flows = {
	15: [(i,j,bw) for i,j in pairs]
    }

    net = fat_tree.create_net()

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
	    j = json.load(f)
	    r = j['end']['sum_received']['bits_per_second']
	    recv.append(r)

    return recv


if __name__ == '__main__':
    sum_sp = [0]
    avg_sp = [0]
    all_sp = [[]]
    sum_msc = [0]
    avg_msc = [0]
    all_msc = [[]]
    bw = [0]
    for i in [125,250,375,500,625,1000,1500]:
	j = '{0}k'.format(i)
	recv = experiment(j, shortest_path)
	all_sp.append(recv)
	sum_sp.append(sum(recv))
	avg_sp.append(sum(recv)/len(recv))
	recv = experiment(j, max_spare_capacity)
	all_msc.append(recv)
	sum_msc.append(sum(recv))
	avg_msc.append(sum(recv)/len(recv))
	bw.append(i*2)
	print all_msc, sum_msc, avg_msc
    print bw
    print sum_sp, avg_sp
    print sum_msc, avg_msc

    for sp,msc in [(sum_sp,sum_msc),(avg_sp,avg_msc)]:
	plt.figure()
	plt.plot(bw, [i/1e3 for i in sp], 'g-o', label='Shortest path')
	plt.plot(bw, [i/1e3 for i in msc], 'b-o', label='Max spare capacity')
	plt.axis([0,3000,0,3000])
	plt.xlabel('Aggregate offered load (kbps)')
	plt.ylabel('Aggregate throughput (kbps)')
	plt.title('Flows from h1-h7, h2-h8, equal offered load')
	plt.legend()
	plt.show()

