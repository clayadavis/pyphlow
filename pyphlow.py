import networkx as nx
from networkx.algorithms import bipartite
try:
    import simplejson as json
except ImportError:
    import json
# import matplotlib.pyplot as plt
"""
G = Graph()
G.add_edges_from([(1,2),(2,6)])
G.add_cycle([2,3,4,5])
G.node[1]['source']=True
G.node[6]['sink']=True
G.nodes(True)

"""

class Graph(nx.Graph):
    def __repr__(self):
        return "G"+str(self.nodes())

### Undirected
def block_cutpoint_tree(G, projected=False, verbose=False):
    in_graph = Graph(G)
    top_nodes = []
    bottom_nodes = []
    articulation_points = set(nx.articulation_points(in_graph))
    if verbose:
        print "Articulation points:", articulation_points
    for biconnected_component in nx.biconnected_components(in_graph):
        inter = biconnected_component.intersection(articulation_points)
        if verbose:
            print "Inter:", inter
        top_nodes.extend(
            [json.dumps(sorted(biconnected_component)) for _ in inter]
            )
        #top_nodes.extend([G.subgraph(bcc) for _ in inter])
        bottom_nodes.extend([x for x in inter])
        #bottom_nodes.extend([G.subgraph(x) for x in inter])
    if verbose:
        print "Top nodes:", top_nodes
        print "Bottom nodes:", bottom_nodes
    edges = zip(top_nodes, bottom_nodes)
    if verbose:
        print "Edges:", edges
    bct = Graph()
    bct.add_edges_from(edges)
    if projected:
        return Graph(bipartite.projected_graph(bct, top_nodes))
    else:
        return bct

#bct = block_cutpoint_tree(G)
#Find the shortest path on block_cutpoint_tree from s to t
#Prune everything not on that path, then project graph

### Directed

def triangle_squash(G):
    done = False
    while not done:
        done = True
        for cycle in nx.cycle_basis(G):
            if len(cycle) == 3:
                neigh = [set(G.neighbors(x)) for x in cycle]
                neigh_to_add = neigh[1].union(neigh[2])
                neigh_to_add.difference_update(set((cycle[1], cycle[2])))
                edges_to_add = [[cycle[0], x] for x in neigh_to_add]
                #for n in cycle:
                #    neigh_to_add.discard(c)
                G.remove_node(cycle[1])
                G.remove_node(cycle[2])
                G.add_edges_from(edges_to_add)
                done = False
    return G
                
                
