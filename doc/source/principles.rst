Concepts, Principles and Processes
==================================
There are some things you should know about to understand the rest of the documentation and use this properly.


Software-Defined Networking
***************************
SDN is a centralised thing. Basically there are some controllers which install flows on switches centrally. Allows you to calculate optimal routes globally instead of just allocating them arbitrarily.


POX
---
POX is an SDN controller written in Python.


Linear Programming
******************
Objective functions are a thing. Actually we use objective function in two ways. Includes entire process not just the top bit. Involves expressing something as a mathematical formulation.

Most of the interesting objective functions use linear programming to find a solution.


Optimisation with PuLP
----------------------
PuLP is a thing. It has `incredible documentation <http://www.coin-or.org/PuLP/index.html>`_, including sections on the optimisation process in general and a series of case studies showing the mathematical derivation and then implementation in python for each problem.


Multicommodity Flow
-------------------
Same here, there are a number available such as shortest_path which you can choose.

* shortest_path
* max_spare_capacity
* widest_shortest_path
