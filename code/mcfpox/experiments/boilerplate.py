"""
Some experiment boilerplate.
"""

import subprocess

def start_pox(cmd='pox.py', log='--CRITICAL', objective=None, rules=None):
    args = [cmd, 'log.level', log, 'mcfpox.controller.base']
    if objective:
	args.append('--objective='+objective)
    if rules:
	args.append('--preinstall='+str(rules))
    return subprocess.Popen(args)


def run_mnc():
    subprocess.call(['sudo', 'mn', '-c'])


def run_experiment(function):
    def handle_cleanup():
	try:
	    run_mnc()
	    function()
	except (KeyboardInterrupt, EOFError):
	    print "Exiting on user command"
	finally:
	    print "End of experiment"
    return handle_cleanup
