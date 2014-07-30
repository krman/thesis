Introduction to mcfpox
**********************
mcfpox is a collection of modules for the POX controller that make it easier to conduct network experiments using linear programming techniques. It also consists of several prewritten objective functions and Mininet topology scripts.


Requirements
============
.. note::
   mcfpox, in its entirety, has a number of dependencies. It is possible to get some use out of individual components of mcfpox without others, so none of the below-listed 'requirements' are *absolutely* necessary - but they are highly recommended so that the software can run as intended.

POX
---
`POX <http://www.noxrepo.org/pox/about-pox/>`_ is a framework, written in Python, to help you write an OpenFlow controller. It's aimed at research and education and consists of reusable components (for topology discovery, host tracking and so on) as well as the core libraries for communicating with switches using OpenFlow. Installation instructions are available `on the wiki <https://openflow.stanford.edu/display/ONL/POX+Wiki#POXWiki-InstallingPOX>`_, including links to various tutorials to get started with SDN, but basically:

.. code:: bash

   $ git clone http://github.com/noxrepo/pox
   $ cd pox

**Why?** POX uses a component-based structure. At startup, components selected by the user are registered in order, and afterwards run in parallel and can communicate with each other. **The core of mcfpox is three POX components** - one each for network discovery, flow statistics gathering and routing control. Obviously, these components sit on top of POX and are unable to be run without it.

Some experiment scripts in mcfpox assume that ``pox.py`` is available on the $PATH. This won't be the case unless you add it. Alternatively, just change those scripts...

NetworkX
--------
`NetworkX <http://networkx.github.io/>`_ is a Python package for the "creation, manipulation, and study of the structure, dynamics, and functions of complex networks". It is available `here <https://pypi.python.org/pypi/networkx/>`_ and should be able to be installed (assuming ``pip`` is present) with

.. code:: bash

   $ sudo pip install networkx

**Why?** mcfpox uses NetworkX to store a representation of the network as discovered by the controller. The network discovery module builds a NetworkX graph, which is passed to the objective function so it can make use of mathematical functions provided by NetworkX.

PuLP
----
pulp

Mininet
-------
mininet

Matplotlib
----------
One day I'm going to produce a graph, and when I do...


Installation/Usage
==================
mcfpox can either be installed (to site-packages) or run locally, in which case you need to add the directory containing the ``mcfpox`` package to the $PYTHONPATH or move it to the ``ext/`` directory in POX (to allow POX to find the components).

To install:

.. code:: bash

   $ git clone the mesh-sources repo
   $ cd mesh-sources/Kimberley
   $ sudo python setup.py install


Testing
=======
.. code:: bash

    $ python setup.py test

to run tests, if there are import errors then it has failed
