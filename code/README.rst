=======
mcf-pox
=======
``mcf-pox`` is a framework for running experiments with multicommodity routing, which builds on the POX SDN controller. The framework consists of three POX modules, one each for topology discovery, flow statistics gathering, and routing coordination. Separate to POX, the user can define (by writing small python scripts) mininet topologies for testing, and objective functions which are used to assign routes to the current flows.

Installation
============
git clone this repository to anywhere. Run ``setup.py``.

Overview
========

.. code::
    mcfpox
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

POX components
==============

``topology.py``
The topology module uses POX's existing discovery and host_tracker modules to build a networkX graph of the network as seen by the controller.

``statistics.py``
The statistics module periodically sends out FlowStatsRequests to connected switches, and builds a dictionary mapping flows to their size (in Mbits/s, as seen in the last few seconds).

``multicommodity.py``
The multicommodity flow routing module runs the given long-term objective function every few seconds (configurable), and temporarily allocates new flows, as they arise, using the given interim allocation function.

Experiment setup
================
Write a script. You can use (and create new) topologies in the topologies directory, and the objective functions. The script will need to start mininet, and start pox with the correct options set (timing, objective functions etc). Depending on the experiment you can also run whatever you choose in terms of timing, performance measurements and so on, through the Mininet API.
