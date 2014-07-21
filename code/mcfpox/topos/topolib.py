"Library of potentially useful topologies for Mininet"

from mininet.topo import Topo
from mininet.net import Mininet
import random

class TreeTopo( Topo ):
    "Topology for a tree network with a given depth and fanout."

    def __init__( self, depth=1, fanout=2 ):
        super( TreeTopo, self ).__init__()
        # Numbering:  h1..N, s1..M
        self.hostNum = 1
        self.switchNum = 1
        # Build topology
        self.addTree( depth, fanout )

    def addTree( self, depth, fanout ):
        """Add a subtree starting with node n.
           returns: last node added"""
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch( 's%s' % self.switchNum )
            self.switchNum += 1
            for _ in range( fanout ):
                child = self.addTree( depth - 1, fanout )
                self.addLink( node, child )
        else:
            node = self.addHost( 'h%s' % self.hostNum )
            self.hostNum += 1
        return node


def TreeNet( depth=1, fanout=2, **kwargs ):
    "Convenience function for creating tree networks."
    topo = TreeTopo( depth, fanout )
    return Mininet( topo, **kwargs )



class PartialMeshTopo(Topo):
    """
    Partial mesh topology with n switches, m hosts, p% connected switches
    """
    def __init__(self, n=6, m=2, p=30):
        super(PartialMeshTopo, self).__init__()

        # Numbering:  h1..N, s1..M
        hostNum = 1
        switchNum = 1

        # Add and link switches
	switches = [self.addSwitch('s{}'.format(i+1)) for i in range(n)]
	for s1 in switches:
	    sel = int(round(n*(p/100.0)) / 2)
	    dist = [1]*sel + [0]*(n-sel)
	    random.shuffle(dist)
	    for i,s2 in enumerate(switches):
		if dist[i]:
		    t1,t2 = s1,s2
		    if s1 == s2:
			try:
			    t2 = switches[i+1]
			except Exception:   # i+1 is too big
			    t2 = switches[i-1]
		    print "link {0} -> {1}".format(t1,t2)
		    self.addLink(t1,t2)
	
	# Add and link hosts
	hosts = [self.addHost('h{}'.format(i+1)) for i in range(m)]
	dist = [1]*m + [0]*(n-m)
	random.shuffle(dist)
	a = [i for i,s in enumerate(dist) if s]
	for h,s in enumerate(a):
	    self.addLink(hosts[h],switches[s])
	    print "link {0} -> {1}".format(hosts[h],switches[s])
	    
	    
def PartialMeshNet(n=6, m=2, p=30, **kwargs):
    "Convenience function for creating partial mesh networks."
    topo = PartialMeshTopo(n, m, p)
    return Mininet(topo, **kwargs)



class GridTopo(Topo):
    """
    Manhattan-style m x n grid, 2 hosts connected to opposite corners
    """
    def __init__(self, m=2, n=6):
        super(GridTopo, self).__init__()

        # Numbering:  h1..N, s1..M
        hostNum = 1
        switchNum = 1

        # Add and link switches
	switches = [[self.addSwitch('s{0}-{1}'.format(j+1, i+1)) for i in range(n)] for j in range(m)]
	print switches
	for i,row in enumerate(switches):
	    for j,s in enumerate(row):
		r,c = i+1,j+1
		if r < m:
		    print "{0},{1} -> {2},{3}".format(r,c,r+1,c)
		    #print "link: {0} -> {1}".format(switches[r][c]. switches[r+1][c])
		    self.addLink(switches[i][j], switches[i+1][j])
		if c < n:
		    print "{0},{1} -> {2},{3}".format(r,c,r,c+1)
		    #print "link: {0} -> {1}".format(switches[r][c]. switches[r][c+1])
		    self.addLink(switches[i][j], switches[i][j+1])

	# Add and link hosts
	hosts = [self.addHost('h{}'.format(i+1)) for i in range(2)]
	self.addLink(hosts[0], switches[0][0])
	self.addLink(hosts[1], switches[m-1][n-1])
	    
	    
def GridNet(n=6, m=2, **kwargs):
    "Convenience function for creating partial mesh networks."
    topo = GridTopo(n, m)
    return Mininet(topo, **kwargs)
