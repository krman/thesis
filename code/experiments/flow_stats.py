#!/usr/bin/python

"""
First stats experiment - do flow stats reflect the actual traffic on the network?
"""

import sys
import subprocess

try:
    retval = subprocess.call("../topos/diamond.py")
except OSError as e:
    print >>sys.stderr, "Failed to start Mininet:", e
