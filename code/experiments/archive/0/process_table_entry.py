#!/usr/bin/python

import sys
import re
from pylab import *

temp_dir = sys.argv[1]

stats = {}
for trial in ["flow-mod", "packet-out"]:

    trial_stats = []
    filename = "{0}/mininet-{1}.log".format(temp_dir, trial)

    f = open(filename)
    for line in f:
	match = re.match("^rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms$", line)
	if match:
	    min,avg,max,mdev = match.group(1,2,3,4)
	    trial_stats.append(float(avg))
    f.close()
    
    stats[trial] = [(i+1,avg) for i,avg in enumerate(trial_stats)]

fig = figure()
ax = fig.add_subplot(111)

for label,data in stats.items():
    scatter(*zip(*data), label=label)

savefig("{0}/results.png".format(temp_dir))
