# mcfpox: Optimal Routing in Software-Defined Networking

This repository contains all code and associated documents that made up my undergraduate Bachelor of Engineering honours thesis - roughly as it stood at the time of submission. The file `thesis.pdf` in the root directory is the final submitted report.

# Abstract
Software-defined networking (SDN) is a relatively new concept in networking which aims to give network operators greater programmability and control over their networks, through separation of the control and data planes. A centralised controller sends network control packets to other switches on the network, usually along a separate, parallel control network. With this new, centralised view of the network, it is possible to apply well-understood mathematical techniques from optimisation and operations research, possibly improving routing efficiency.

This thesis presents a framework to facilitate comparison of different routing metrics. The framework includes a controller, consisting of modules for topology discovery, flow statistics and routing control, and an experiment module to run network experiments on virtual networks, including several prewritten topologies. Three routing metrics (shortest path, widest path and residual capacity) are implemented.

Additionally, this thesis presents the results of network experiments performed using this framework, comparing the performance of the three metrics above on two topologies with different flow patterns. The residual capacity metric, which attempts to find a globally-optimal solution, improved on the performance of shortest path by up to 57% in some trials, with widest path only improving shortest path by 34%.  However, residual capacity performed significantly worse when no solution could be found, such as for experiments with many flows. There, widest path improved on shortest path by up to 91%, while residual capacity was worse by 36%.

# Framework
mcfpox is a framework for running experiments with multicommodity routing, which builds on the POX SDN controller. The framework consists of three POX modules, one each for topology discovery, flow statistics gathering, and routing coordination. Separate to POX, the user can define (by writing small python scripts) mininet topologies for testing, and objective functions which are used to assign routes to the current flows.

## Installation
git clone this repository to anywhere. Run setup.py.

## Overview

```
framework
-- controllers
   -- base.py
   -- topology.py
   -- statistics.py
   -- multicommodity.py
-- experiments
   -- topologies
      -- diamond.py
      -- fat_tree.py
   -- objectives
      -- shortest_path.py
      -- spare_capacity.py
   -- start.py
```

## POX components

### topology.py
The topology module uses POX's existing discovery and host_tracker modules to build a networkX graph of the network as seen by the controller.

### statistics.py
The statistics module periodically sends out FlowStatsRequests to connected switches, and builds a dictionary mapping flows to their size (in Mbits/s, as seen in the last few seconds).

### multicommodity.py
The multicommodity flow routing module runs the given long-term objective function every few seconds (configurable), and temporarily allocates new flows, as they arise, using the given interim allocation function.

## Experiment setup
Write a script. You can use (and create new) topologies in the topologies directory, and the objective functions. The script will need to start mininet, and start pox with the correct options set (timing, objective functions etc). Depending on the experiment you can also run whatever you choose in terms of timing, performance measurements and so on, through the Mininet API.
