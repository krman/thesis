"""
Some experiment boilerplate.
"""

import os
import sys
import time
import sched
import subprocess
from multiprocessing import Process

from pox.boot import boot

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController


def start_log():
    log_dir = 'log.{0}'.format(int(time.time()))
    subprocess.call(['mkdir', '-p', log_dir])
    return log_dir
    

def start_net(net, log_dir):
    print "\nCleaning up mininet"
    with open('/dev/null', 'w') as DEVNULL:
	subprocess.call(['sudo', 'mn', '-c'], stdout=DEVNULL, stderr=DEVNULL)

    print "Starting mininet"
    setLogLevel('output')
    net.start()
    return net


def start_pox(log_dir='.', log={}, module='mcfpox.controller.base',
              objective=None, rules=None):
    
    full_log = {
	'packet': 'WARN'
    }
    full_log.update(log)
    
    args = {module: [{
            'objective': objective
        }], 
	'log': [{
	    'no_default': True,
	    'file': os.path.join(log_dir, 'pox.log')
	}],
        'log.level': [ full_log ]
    }   
    
    print "\nStarting POX: output in pox.log"
    process = Process(target=boot, args=(args,))
    process.start()
    return process
    

def start_iperf(src, dst, port, bw, log_dir):
    server_log = 'server.{0}.{1}'.format(dst, port)
    client_log = 'client.{0}.server.{1}.{2}'.format(src, dst, port)
    
    server_cmd = 'iperf3 -s -p {0} &> {1} &'.format(
	    port, os.path.join(log_dir, server_log))

    client_cmd = 'iperf3 -c {0} -p {1} -b {2} -t 10 -J &> {3} &'.format(
	    dst.IP(), port, bw, os.path.join(log_dir, client_log))

    print 'Flow: {0} from {1} ({2}) to {3} ({4})'.format(
	    bw, src, src.IP(), dst, dst.IP())

    dst.cmd(server_cmd)
    src.cmd(client_cmd)


def start_flows(flow_schedule, net, log_dir):
    s = sched.scheduler(time.time, time.sleep)
    port = 5001

    for delay, flows in flow_schedule.iteritems():
        for flow in flows:
            src = net.get(flow[0])
            dst = net.get(flow[1])
            bw = flow[2]
            
            s.enter(delay, 1, start_iperf, ([src, dst, port, bw, log_dir]))
            port += 1

    time.sleep(1)
    print "\nStarting scheduled flows: iperf output in server/client logs"
    s.run()
    time.sleep(15)
                  
                  
def start(scenario, config, log_dir=None):
    try:
	if not log_dir:
	    log_dir = start_log()

	print "Starting experiment: log files in {0}".format(log_dir)

	net = start_net(scenario['net'], log_dir)
	controller = start_pox(log_dir=log_dir, **config)
	
	start_flows(scenario['flows'], net, log_dir)
	
	net.stop()
	controller.terminate()

    except (KeyboardInterrupt, EOFError):
	print "Exiting on user command"
    finally:
	print "End of experiment"
