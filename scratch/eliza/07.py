import networkx as nx

class PermutohedronManifold:
    """
    The Global Geometric Guardrail.
    Computes the full 24-chamber Cayley graph of A3 (S4).
    The conversational state is a strict point on this manifold.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.origin = (1, 2, 3, 4)  # Foundational Equilibrium
        self.w0 = (4, 3, 2, 1)      # Maximal Epistemic Displacement
        self._build_manifold()

    def _swap(self, state: tuple, i: int, j: int) -> tuple:
        """Applies an adjacent transposition (a Coxeter reflection)."""
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def _build_manifold(self):
        """Enumerates the 24 chambers and their geometric adjacencies via BFS."""
        queue = [self.origin]
        self.graph.add_node(self.origin)
        
        while queue:
            current = queue.pop(0)
            
            # The three foundational discourse moves
            moves = {
                "s1": self._swap(current, 0, 1),
                "s2": self._swap(current, 1, 2),
                "s3": self._swap(current, 2, 3)
            }
            
            for gen, next_state in moves.items():
                if next_state not in self.graph:
                    self.graph.add_node(next_state)
                    queue.append(next_state)
                # Add edge with generator label for canonical pathfinding
                self.graph.add_edge(current, next_state, generator=gen)

    def apply_reflection(self, current_state: tuple, reflection: str) -> tuple:
        """Navigates exactly one edge along the Cayley graph."""
        if reflection == "s1": return self._swap(current_state, 0, 1)
        if reflection == "s2": return self._swap(current_state, 1, 2)
        if reflection == "s3": return self._swap(current_state, 2, 3)
        return current_state

    def get_canonical_path(self, state: tuple) -> list[str]:
        """
        Extracts the Shortlex geodesic from the Origin to the current chamber.
        This replaces the string-rewriting engine completely.
        """
        path_nodes = nx.shortest_path(self.graph, self.origin, state)
        path_generators = []
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i+1]
            path_generators.append(self.graph[u][v]['generator'])
        return path_generators

    def get_metrics(self, state: tuple) -> dict:
        """Computes the topological physics of the current discourse state."""
        bruhat_distance = nx.shortest_path_length(self.graph, self.origin, state)
        
        # Harmonic Potential (0.0 at origin, 1.0 at w0)
        potential = bruhat_distance / 6.0 
        
        return {
            "bruhat_distance": bruhat_distance,
            "epistemic_potential": potential,
            "coordinate": state
        }

class NeuralHeuristic:
    """The Coalgebraic Unfolder (The 1-cell selector)."""
    def predict_generator(self, text: str) -> str:
        text = text.lower()
        if "?" in text:
            return "s1" # Epistemic Inversion
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]):
            return "s3" # Introspective Reflection
        else:
            return "s2" # Contextual Dilation

class TopologicalSemantics:
    """
    Functorial semantics strictly derived from graph metrics.
    Meaning emerges from the epistemic potential (distance / max distance).
    """
    def generate(self, metrics: dict, last_move: str) -> str:
        dist = metrics["bruhat_distance"]
        potential = metrics["epistemic_potential"]
        
        if dist == 0:
            return "We have resolved the tension and returned to the origin. Where to next?"
            
        elif potential <= 0.33: # Dist 1-2 (Shallow perturbation)
            if last_move == "s1": return "Why do you ask that?"
            elif last_move == "s2": return "Let's zoom out. How does this fit into the broader picture?"
            else: return "How does that make you feel deep down?"
            
        elif potential <= 0.66: # Dist 3-4 (Deep displacement / Parabolic intersections)
            if last_move == "s1": return "But fundamentally, what is the exact core of your questioning here?"
            elif last_move == "s2": return "Are you questioning how all of this fits into the wider context?"
            else: return "Zooming out, how does grappling with this impact you internally?"
            
        elif dist == 5: # The boundary before w0
            return "We are on the absolute edge of a perspective shift. If we push one step further, what changes?"
            
        else: # Dist 6 (The w0 Chamber)
            return "We have completely inverted the foundation of where we started. Looking at this from the absolute opposite perspective, what do you see?"

class CoalgebraicELIZA:
    def __init__(self):
        self.manifold = PermutohedronManifold()
        self.nn = NeuralHeuristic()
        self.semantics = TopologicalSemantics()
        self.current_chamber = self.manifold.origin
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        # 1. Heuristic Emission
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Emitted Reflection: {s_i}")
        
        # 2. Geometric Traversal (Permutation Action)
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, s_i)
        
        # 3. Metric Computation (Graph Physics)
        metrics = self.manifold.get_metrics(self.current_chamber)
        canonical_word = self.manifold.get_canonical_path(self.current_chamber)
        word_str = '*'.join(canonical_word) if canonical_word else 'Identity'
        
        print(f"[Topology] Chamber Coordinate: {metrics['coordinate']}")
        print(f"[Geometry] Canonical Geodesic: {word_str}")
        print(f"[Physics]  Bruhat Distance: {metrics['bruhat_distance']} | Epistemic Potential: {metrics['epistemic_potential']:.2f}")
        
        # 4. Semantic Functor Realization
        response = self.semantics.generate(metrics, s_i)
        self.turn += 1
        return response

# --- Execution ---
if __name__ == "__main__":
    eliza = CoalgebraicELIZA()
    print("ELIZA: I am ready to listen. Tell me more.")
    
    while True:
        try:
            user_text = input("User: ")
            if user_text.lower() in ['quit', 'exit']:
                break
            reply = eliza.chat(user_text)
            print(f"\nELIZA: {reply}")
        except KeyboardInterrupt:
            break