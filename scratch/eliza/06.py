import networkx as nx

class PermutohedronManifold:
    """
    Computes the full 24-chamber Cayley graph of A3 (S4).
    Replaces string-matching semantics with graph-theoretic metrics.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.origin = (1, 2, 3, 4)
        self.w0 = (4, 3, 2, 1) # Length 6
        self._build_manifold()

    def _swap(self, state, i, j):
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def _build_manifold(self):
        # Enumerate all 24 states and edges via BFS
        queue = [self.origin]
        self.graph.add_node(self.origin)
        
        while queue:
            current = queue.pop(0)
            
            # Generators: s1, s2, s3
            moves = {
                "s1": self._swap(current, 0, 1),
                "s2": self._swap(current, 1, 2),
                "s3": self._swap(current, 2, 3)
            }
            
            for gen, next_state in moves.items():
                if next_state not in self.graph:
                    self.graph.add_node(next_state)
                    queue.append(next_state)
                self.graph.add_edge(current, next_state, generator=gen)

    def measure_tension(self, current_state: tuple) -> dict:
        """
        Calculates the exact geometric semantics of the current chamber.
        """
        dist_from_origin = nx.shortest_path_length(self.graph, self.origin, current_state)
        dist_to_w0 = nx.shortest_path_length(self.graph, current_state, self.w0)
        
        # Harmonic Potential (0.0 at origin, 1.0 at w0)
        potential = dist_from_origin / 6.0 
        
        return {
            "bruhat_distance": dist_from_origin,
            "w0_proximity": dist_to_w0,
            "epistemic_potential": round(potential, 3),
            "chamber_coordinates": current_state
        }