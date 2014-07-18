POX Modules
===========

`POX <https://openflow.stanford.edu/display/ONL/POX+Wiki>`_ is an SDN controller written in Python. It allows extra modules to be plugged in. The core of this framework is three POX modules:

- network discovery
- flow statistics
- routing control

Network Discovery
-----------------

Network discovery (switches, hosts, links) is done using the existing POX modules `discovery <https://openflow.stanford.edu/display/ONL/POX+Wiki#POXWiki-openflow.discovery>`_ and `host_tracker <https://openflow.stanford.edu/display/ONL/POX+Wiki#POXWiki-host_tracker>`_. The ``topology`` module uses these two modules to build a `NetworkX <http://networkx.github.io/>`_ graph which is passed to the objective function for routing calculations.

The Topology Module
*******************

.. autoclass:: thesis.controllers.topology.Network
   :members:

Flow Statistics
---------------

OpenFlow provides a number of message types to query switch statistics, such as number of packets seen for particular flows. The ``statistics`` module sends FlowStatsRequest messages to each switch known by ``topology`` periodically.

The Statistics Module
*********************

.. autoclass:: thesis.controllers.statistics.Statistics
   :members:

Routing Control
---------------

Routing is controlled on two levels:

- When a new flow arrives, it is assigned an interim path and rules are installed on switches along this path
- Periodically (how often is configurable) the module runs an objective function, which calculates optimal routes for all current (recently-seen) flows, removes existing switch rules for these flows and installs the new ones.

The Multicommodity Module
*************************

.. autoclass:: thesis.controllers.multicommodity.Multicommodity
   :members:
