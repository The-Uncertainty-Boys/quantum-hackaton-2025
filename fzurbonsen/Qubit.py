import networkx as nx

interaction_nodes = [(1, 1), (1, 3), (3, 1), (3, 3), (1, 5), (3, 5)]

class Qubit:
    def __init__(self, node, graph):
        self.node = node
        self.graph = graph
        self.free = 1
        self.idle = 0
        self.path = []

    def next_tick(self):
        self.free = 1

    def set_idle(self, pos):
        # check if we can idle in the current position
        i, j = self.node
        if (i, j, "idle") in pos or not self.free:
            # we cannot idle the node
            return None # return to indicate that the attempt to idle failed
        else:
            self.idle = 1
            self.free = 0
            pos.remove((i, j))
            pos.append((i, j, "idle"))
            return pos
        
    def set_active(self, pos):
        if self.node not in pos and self.free:
            self.idle = 0
            self.free = 0
            i, j = self.node
            pos.remove((i, j, "idle"))
            pos.append(self.node)
            return pos
        return None

    def find_next_idle(self, pos):
        i, j = self.node
        for k in range(7):
            if (i+k, j, "idle") in self.graph and (i+k, j, "idle") not in pos:
                return (i+k, j)
            if (i-k, j, "idle") in self.graph and (i-k, j, "idle") not in pos:
                return (i-k, j)
            if (i, j+k, "idle") in self.graph and (i, j+k, "idle") not in pos:
                return (i, j+k)
            if (i, j-k, "idle") in self.graph and (i, j-k, "idle") not in pos:
                return (i, j-k)
        raise AssertionError("error while searching for idle, none available")

    def find_path_to_idle(self, pos):
        i, j = self.find_next_idle(pos)
        path = self.find_path((i, j))
        return path
    
    def move(self, end, pos):
        # check if end is in the graph
        if end in self.graph and self.free:
            # check if the move is allowed
            if self.graph.has_edge(self.node, end):
                # check if there already is a node at the target position
                if end not in pos:
                    pos.remove(self.node)
                    pos.append(end)
                    self.node = end
                    self.free = 0
                    return pos
                elif end in interaction_nodes and pos.count(end) < 2:
                    pos.remove(self.node)
                    pos.append(end)
                    self.node = end
                    self.free = 0
                    return pos
        return None # the move is not legal so we return None to indicate that
        
    def find_path(self, end):
        global interaction_nodes
        try:
            # Make a copy of the graph so we can safely modify it
            temp_graph = self.graph.copy()

            # Remove all edges from no_passthrough_nodes, except if node is self.node or end
            for node in interaction_nodes:
                if node != self.node and node != end:
                    temp_graph.remove_edges_from(list(temp_graph.edges(node)))

            # Find the shortest path on the modified graph
            path = nx.shortest_path(temp_graph, source=self.node, target=end)
            return path

        except nx.NetworkXNoPath:
            print(f"No path found from {self.node} to {end}.")
            return None
        except nx.NodeNotFound as e:
            print(f"Node error: {e}")
            return None
        
    def set_path(self, path):
        self.path = path
        self.path.pop(0)

    def try_next_move(self, pos):
        if len(self.path) == 0:
            return None
        else:
            new_pos = self.move(self.path[0], pos)
            if new_pos != None:
                pos = new_pos
                self.path.pop(0)
        return pos
    

        
