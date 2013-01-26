pyphlow
=======
A Python implementation of the Misiolek-Chen flow network simplification algorithms as seen [in these papers](http://www.journalogy.net/Publication/1848751/efficient-algorithms-for-simplifying-flow-networks). 

Dependencies
=======
Requires [NetworkX](http://networkx.lanl.gov).

Example
=======
    import networkx, pyphlow
    G = networkx.Graph()
    G.add_edges_from([(1,2),(2,6)])
    G.add_cycle([2,3,4,5])
    G.node[1]['source']=True
    G.node[6]['sink']=True
    S = pyphlow.simplify(G)
