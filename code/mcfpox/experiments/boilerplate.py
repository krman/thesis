"""
Some experiment boilerplate.
"""

import subprocess
from pox.boot import boot
from mcfpox.objectives.shortest_path import objective as obj


def start_pox(cmd='pox.py', log='--packet=WARN', module='mcfpox.controller.base',
	      objective=None, rules=None):
    argv = [cmd, 'log.level', log, module]
    if objective:
	argv.append('--objective='+objective)
    if rules:
	argv.append('--preinstall='+str(rules))
    #boot(argv[1:])
    #args = {module:[{
		#'objective': obj,
		#'rules': rules
	    #}], 
	    #'log.level':[{log: True}]}
    #boot(args)
    return subprocess.Popen(argv)


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


if __name__ == '__main__':
    start_pox(objective='mcfpox.objectives.shortest_path')
