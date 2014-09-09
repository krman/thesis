.. _experiment:

Writing Experiment Scripts
**************************
Every experiment is different. ``mcfpox.experiments`` contains some to get started but you would normally write your own. They are in the experiments directory by convention but they can run anywhere, you just need to import the right packages.


A Simple Example
================
In this example we want to measure the performance of the "shortest path" method for route allocation. Consider a 'pentagon' topology: one of the simplest topologies where shortest-path has multiple different paths to choose from:

.. figure:: ../images/diamond.png
   :alt: A 'pentagon' topology
   :scale: 40%

Every experiment will have a slightly different structure. In this case we want to measure the overall throughput, allowing the entire system to discover everything. The steps for this particular experiment will be as follows:

- start pox
- start mininet with pentagon topo
- wait for pox to discover network
- start a (bidirectional) iperf flow between the two hosts
- check that the correct path was taken
- measure iperf performance

The rest of this page will explain how to build up a script to perform this experiment.

.. note::
   In later sections we will talk about substituting mock objects for certain parts of the system, for example preinstalling flows on all switches, or generating fake flow statistics to be passed to the objective function.


Mininet Topologies
==================
You can select one to be used.

.. note::
   In this example we will just be using prewritten topologies but you can write your own. See :ref:`mininet` for more details.


Objective Functions
===================
Same here, there are a number available such as shortest_path which you can choose.

* shortest_path
* max_spare_capacity
* widest_shortest_path


Starting POX
============
.. warning::
    This script will launch POX itself. Sometimes it can be desirable to have POX and mininet running in separate windows, especially to see debug output or to interact with both separately. In this case there is no interaction and most of POX's output is suppressed.


The Full Script
===============
This script is also available as ``mcfpox/experiments/basic_operation.py``.

.. code:: python

    
