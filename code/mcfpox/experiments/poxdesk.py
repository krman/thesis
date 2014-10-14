#!/usr/bin/python

from mcfpox.topos import diamond
from mcfpox.objectives import max_spare_capacity
from boilerplate import start, results

import matplotlib.pyplot as plt


def experiment(bw, module):
    pairs = [('h1','h2')]
    flows = {
        15: [(i,j,bw) for i,j in pairs]
    }

    scenario = {
        'net': diamond,
        'flows': flows
    }

    controller = {
        'objective': module.objective,
        'poxdesk': True
    }

    return start(scenario, controller)


if __name__ == '__main__':
    bw = [0]
    sp = [0]

    for i in [5]:
        j = '{0}m'.format(i)
        recv = experiment(j, max_spare_capacity)
        sp.append(sum(recv))
        bw.append(i)

    plt.figure()
    plt.plot(bw, [i/1e6 for i in sp], 'g-x',label='Max spare capacity')
    plt.axis([0,10,0,10])
    plt.xlabel("Aggregate offered load (Mbps)")
    plt.ylabel("Aggregate throughput (Mbps)")
    plt.title("mcfpox demonstration")
    plt.legend()
    save = "demo.png"
    plt.savefig(save)
    plt.show()
