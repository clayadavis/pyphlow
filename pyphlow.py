"""
G = pyphlow.Graph()
G.add_edges_from([(1,2),(2,6)])
G.add_cycle([2,3,4,5])
G.node[1]['source']=True
G.node[6]['sink']=True
G.nodes(True)
S = pyphlow.simplify(G)
S

"""
import networkx as nx
from networkx.algorithms import bipartite
import itertools
try:
    import simplejson as json
except ImportError:
    import json
    
# import matplotlib.pyplot as plt


class Graph(nx.Graph):
    """This is a trivial extension of networkx.Graph which adds a 
    better __repr__."""
    def __repr__(self):
        return "G"+str(self.nodes())

### Undirected
### TODO: Add weights.
def block_cutpoint_tree(G, projected=False, verbose=False):
    input_graph = Graph(G)
    top_nodes = []
    bottom_nodes = []
    articulation_points = set(nx.articulation_points(input_graph))
    if verbose:
        print "Articulation points:", articulation_points
    for biconnected_component in nx.biconnected_components(input_graph):
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
    bc_tree = Graph()
    bc_tree.add_edges_from(edges)
    if projected:
        return Graph(bipartite.projected_graph(bc_tree, top_nodes))
    else:
        return bc_tree
        
def find_source_and_sink(G, as_dict=False):
    sources = []
    sinks = []
    for node, attrs in G.nodes(True):
        if attrs.get('source', False):
            sources.append(node)
        if attrs.get('sink', False):
            sinks.append(node)
    if as_dict:
        return {'source':sources, 'sink':sinks}
    else:
        return (sources, sinks)
        
def get_matching_nodes(pattern, G, with_json=True):
    matches = []
    for node in G:
        if with_json:
            seq = json.loads(node)
        else:
            seq = node
        if pattern in seq:
            matches.append(node)
    return matches
    
def simplify(G, with_apsp=True, verbose=False):
    bc_tree = block_cutpoint_tree(G, projected=True)
    (sources, sinks) = find_source_and_sink(G)
    apsp = None
    if with_apsp:
        apsp = nx.shortest_path(bc_tree)
    essential_paths = []
    for (source, sink) in itertools.product(sources, sinks):
        if verbose:
            print "Looking for shortest path from %s to %s..." % (source, sink)
        source_bccs = get_matching_nodes(source, bc_tree)
        sink_bccs = get_matching_nodes(sink, bc_tree)
        shortest_path = None
        for (source_bcc, sink_bcc) in itertools.product(source_bccs, sink_bccs):
            if with_apsp:
                possible_path = apsp[source_bcc][sink_bcc]
            else:
                possible_path = nx.shortest_path(bc_tree, source_bcc, sink_bcc)
            if verbose:
                print "... possible path from %s to %s has length %i: %s" % \
                    (source_bcc, sink_bcc, len(possible_path), possible_path)
            # This might be less than ideal, in case there are more than one
            if not shortest_path or len(possible_path) < len(shortest_path):
                shortest_path = possible_path
        essential_paths.append(shortest_path)
        if verbose:
            print "--> shortest path from %s to %s: %s" % \
                (source, sink, shortest_path)
        
    essential_nodes = set()
    for e_path in essential_paths:
        for e_node in e_path:
            for node in json.loads(e_node):
                essential_nodes.add(node)
    if verbose:
        print "Essential nodes:", sorted(essential_nodes)
    return G.subgraph(essential_nodes)
            

#Find the shortest path on block_cutpoint_tree from s to t
#Prune everything not on that path, then project graph

### Directed

### Work-in-progress
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
                
                
