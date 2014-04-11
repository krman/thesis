#!/bin/bash

mkdir /tmp/results 2>/dev/null

# start monitoring packets
tcpdump -i any -w /tmp/results/packet.dump &
pid_tcpdump=$!

# start pox controller
pox.py log.level --DEBUG thesis.base >/tmp/results/controller.log &
pid_pox=$!

# start mininet script
./flow_stats.py >/tmp/results/mininet.log &

# clean up
kill $pid_tcpdump 2>/dev/null
kill $pid_pox 2>/dev/null
