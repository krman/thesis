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


def start_log(log_dir):
    if not log_dir:
	log_dir = 'log.{0}'.format(int(time.time()))
    subprocess.call(['mkdir', '-p', log_dir])
    return {'log_dir': log_dir}
    

def start_net(net, logs):
    #print "\nCleaning up mininet"
    #with open('/dev/null', 'w') as DEVNULL:
	#subprocess.call(['sudo', 'mn', '-c'], stdout=DEVNULL, stderr=DEVNULL)

    print "Starting mininet: no logs"
    net.start()

    return net


def start_pox(logs, level={}, module='mcfpox.controller.base',
              objective=None, rules=None):
    
    log_level = {
	'packet': 'WARN'
    }
    log_level.update(level)
    
    args = {module: [{
            'objective': objective
        }], 
        'log.level': [ log_level ]
    }   
    
    logs['pox'] = {'out':'pox.out', 'err':'pox.err'}
    print "Starting POX: stdout in {out}, stderr in {err}".format(
	    **logs['pox'])

    def start_with_log(components, out_log, err_log):
	sys.stdout = open(out_log, 'w')
	sys.stderr = open(err_log, 'w')
	boot(components)
    
    out_log = os.path.join(logs['log_dir'], logs['pox']['out'])
    err_log = os.path.join(logs['log_dir'], logs['pox']['err'])
    process = Process(target=start_with_log, args=(args,out_log,err_log,))
    process.start()
    return process
    

def start_iperf(src, dst, port, bw, server_log, client_log):
    server_cmd = "iperf3 -s -p {0} &> {1} &".format(
	    port, server_log)

    client_cmd = "iperf3 -c {0} -p {1} -b {2} -t 10 -J &> {3} &".format(
	    dst.IP(), port, bw, client_log)

    print "Flow: {0} from {1} ({2}) to {3} ({4})".format(
	    bw, src, src.IP(), dst, dst.IP())

    dst.cmd(server_cmd)
    src.cmd(client_cmd)


def start_flows(flow_schedule, net, logs):
    s = sched.scheduler(time.time, time.sleep)
    port = 5001
    flow_logs = []
    log_dir = logs['log_dir']

    for delay, flows in flow_schedule.iteritems():
        for flow in flows:
            src = net.get(flow[0])
            dst = net.get(flow[1])
            bw = flow[2]
	    
	    server_log = 'server.{0}.{1}'.format(dst, port)
	    client_log = 'client.{0}.server.{1}.{2}'.format(src, dst, port)
	    flow_logs.append((server_log, client_log))
            
            s.enter(delay, 1, start_iperf, (src, dst, port, bw, 
		    os.path.join(log_dir, server_log), 
		    os.path.join(log_dir, client_log),))
            port += 1

    logs['flows'] = flow_logs
    time.sleep(1)
    print "\nStarting scheduled flows: iperf output in server/client logs"
    s.run()
    print
    time.sleep(15)
                  
                  
def start(scenario, config, log_dir=None):
    logs = start_log(log_dir)
    print "Starting experiment: log files in {0}".format(logs['log_dir'])

    try:
	net = start_net(scenario['net'], logs)
	controller = start_pox(logs, **config)
	
	start_flows(scenario['flows'], net, logs)
	
	net.stop()
	controller.terminate()

    except KeyboardInterrupt as e:
	print "Exiting on user command"
	raise
    finally:
	print "End of experiment"

    return logs
