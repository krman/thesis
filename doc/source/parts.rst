.. _parts:

Injecting Mock Data
*******************
For the purposes of experiments and measuring, don't necessarily want to run thee full thing from starting up pox, discovering the network etc. mcfpox allows you to inject dummy data at certain points in the process, to replace calculated data, for example to guarantee that a particular result is only due to one part, or because only one specific section is of interest.


Injectable Parts
================
places you can inject things to pox (ooh grammar is hard):

- fake flows and flow statistics (todo)
- switch forwarding rules to preinstall on pox startup (todo)
- topology information, as an nx.Graph (todo)


A Simple Example
================
In this example, we want to examine the performance of the routes chosen by the shortest_path algorithm, using the pentagon topology from earlier:

.. figure:: ../images/diamond.png
   :alt: A 'pentagon' topology
   :scale: 40%

In a real-life situation, there is some delay caused in routing a new flow for the first time. While this is sometimes of interest, in this case we want to only test the actual routes installed and calculated by the algorithm.

mcfpox allows us to preinstall flow rules on switches, meaning that we can later start flows and not have to wait for routes to be calculated: the iperf results will only reflect the transmission times through the network. This is actually a lie, as I believe there is still ARP to consider, but let's ignore that.

The differences between this and the example in :ref:`experiment` are:

1. stuff
2. other stuff

So in summary, our process will be as follows:

- run objective function by itself, to get rules list
- start pox, passing the rules through to mcfpox
- start mininet with pentagon topo
- wait for pox to discover network
- start a (bidirectional) iperf flow between the two hosts
- check that the correct path was taken
- measure iperf performance

The rest of this page will explain how to build up a script to perform this experiment.


Precalculating Forwarding Rules
===============================
We start by running the objective function and getting the rules. On its own, objective functions must return the rules in a dictionary of a certain format. The function is given two arguments:

.. autofunction:: mcfpox.objectives.shortest_path.objective
   :noindex:

.. code:: python
   
    >>> from mcfpox.objectives.shortest_path import objective
    >>> from mcfpox.test.objectives.shortest_path import pentagon_graph
    >>> from mcfpox.controller.lib import Flow, Hop
    >>> graph = pentagon_graph()
    >>> f1 = Flow(6, '10.0.0.1', '10.0.0.2', 5001, 5002)
    >>> f2 = Flow(6, '10.0.0.2', '10.0.0.1', 5003, 5004)
    >>> flows = {
    ...     f1: [Hop(1,2), Hop(2,2), Hop(5,1)],
    ...     f2: [Hop(5,2), Hop(2,1), Hop(1,1)]
    ... }
    >>> objective(graph, flows)
    {Flow(nw_proto=6, nw_src='10.0.0.1', nw_dst='10.0.0.2', tp_src=5001, tp_dst=5002): [Hop(dpid=1, port=2), Hop(dpid=2, port=2), Hop(dpid=5, port=1)], Flow(nw_proto=6, nw_src='10.0.0.2', nw_dst='10.0.0.1', tp_src=5003, tp_dst=5004): [Hop(dpid=5, port=2), Hop(dpid=2, port=1), Hop(dpid=1, port=1)]}



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

    #!/usr/bin/python

    import subprocess
    import signal
    import sys
    import importlib

    from time import sleep

    from mininet.cli import CLI
    from mininet.log import setLogLevel
    from mininet.node import RemoteController

    import mcfpox.topos.pentagon as topo


    # Handle SIGINT
    def cleanup(signal=None, frame=None):
        try:
            controller.kill()
        except Exception:
            print "failed to stop controller"
            pass

        try:
            net.stop()
        except Exception:
            print "failed to stop net"
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)

    # Remove any running controllers and/or mininets
    clean = subprocess.call(['sudo', 'mn', '-c'])

    # Start POX, running the mcfpox controller module
    objective = 'mcfpox.objectives.shortest_path'
    controller = subprocess.Popen(['pox.py', 'log.level', '--CRITICAL',
                                   'mcfpox.controller.base',
                                   '--objective='+objective])

    # Start mininet with given topology
    setLogLevel('output')
    net = topo.create_net(controller=RemoteController)
    c = net.addController('c0')
    net.start()

    # Wait for network to be discovered
    sleep(15)

    # Start flows/perform experiments
    h1 = net.get('h1')
    h2 = net.get('h2')
    h1.cmd('ping -c1 ' + str(h2.IP()))
    h2.cmd('ping -c1 ' + str(h1.IP()))

    # Don't exit the script until the controller is killed
    controller.wait()


