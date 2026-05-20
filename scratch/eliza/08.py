import networkx as nx

class PermutohedronManifold:
    """
    The Global Geometric Guardrail.
    Computes the full 24-chamber Cayley graph of A3 (S4) and strictly solves 
    for Shortlex geodesics and harmonic gradients.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.origin = (1, 2, 3, 4)  # Foundational Equilibrium
        self.w0 = (4, 3, 2, 1)      # Maximal Epistemic Displacement
        self.shortlex_paths = {}    # Exact canonical mapping
        self._build_manifold()
        self._compute_shortlex_geodesics()

    def _swap(self, state: tuple, i: int, j: int) -> tuple:
        """Applies an adjacent transposition (a Coxeter reflection)."""
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def apply_reflection(self, current_state: tuple, reflection: str) -> tuple:
        """Navigates exactly one edge along the Cayley graph."""
        if reflection == "s1": return self._swap(current_state, 0, 1)
        if reflection == "s2": return self._swap(current_state, 1, 2)
        if reflection == "s3": return self._swap(current_state, 2, 3)
        return current_state

    def _build_manifold(self):
        """Enumerates the 24 chambers and their geometric adjacencies."""
        queue = [self.origin]
        self.graph.add_node(self.origin)
        
        while queue:
            current = queue.pop(0)
            for gen in ["s1", "s2", "s3"]:
                next_state = self.apply_reflection(current, gen)
                if next_state not in self.graph:
                    self.graph.add_node(next_state)
                    queue.append(next_state)
                self.graph.add_edge(current, next_state, generator=gen)

    def _compute_shortlex_geodesics(self):
        """
        Guarantees True Shortlex Normal Forms.
        A strict BFS exploring s1 < s2 < s3 ensures the first path found 
        to any node is the absolute lexicographically lowest geodesic.
        """
        queue = [(self.origin, [])]
        self.shortlex_paths[self.origin] = []
        
        while queue:
            current, path = queue.pop(0)
            for gen in ["s1", "s2", "s3"]:
                next_state = self.apply_reflection(current, gen)
                # If unvisited, this strict ordering guarantees Shortlex
                if next_state not in self.shortlex_paths:
                    new_path = path + [gen]
                    self.shortlex_paths[next_state] = new_path
                    queue.append((next_state, new_path))

    def get_metrics(self, state: tuple) -> dict:
        """Computes the topological physics and local gradient of the chamber."""
        path = self.shortlex_paths[state]
        dist = len(path)
        
        # Calculate Local Gradient (Uphill vs Downhill available edges)
        uphill = 0
        downhill = 0
        for gen in ["s1", "s2", "s3"]:
            neighbor = self.apply_reflection(state, gen)
            if len(self.shortlex_paths[neighbor]) > dist:
                uphill += 1
            else:
                downhill += 1
                
        return {
            "coordinate": state,
            "shortlex_word": path,
            "bruhat_distance": dist,
            "epistemic_potential": dist / 6.0,
            "gradient_up": uphill,
            "gradient_down": downhill
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

class DynamicalSemantics:
    """
    Meaning emerges from the scalar field over the manifold.
    Responses are governed by both Position (Distance) and Momentum (Delta).
    """
    def generate(self, metrics: dict, prev_dist: int) -> str:
        dist = metrics["bruhat_distance"]
        momentum = dist - prev_dist # +1 Escalating, -1 Relaxing
        
        if dist == 0:
            return "The tension has completely dispersed. We are back at the origin. Where to next?"
            
        if momentum < 0:
            # The conversation is flowing "downhill" toward equilibrium.
            if dist <= 2: return "We are unraveling the complexity. It seems simpler now. What remains?"
            return "We are pulling back from the extreme edge. Let's ground this a bit more."
            
        else:
            # The conversation is flowing "uphill" toward maximal inversion.
            if dist <= 2:
                return "We are just beginning to push the boundaries of this idea. Go further."
            elif dist <= 4:
                return "The tension is building. We are intersecting some difficult assumptions here. Keep going."
            elif dist == 5:
                return "We are on the absolute precipice. One more shift and the entire foundational premise inverses."
            else:
                return "Total Epistemic Inversion reached. We are looking at this from the absolute opposite perspective of where we began. What do you see?"

class CoalgebraicELIZA:
    def __init__(self):
        self.manifold = PermutohedronManifold()
        self.nn = NeuralHeuristic()
        self.semantics = DynamicalSemantics()
        self.current_chamber = self.manifold.origin
        self.current_metrics = self.manifold.get_metrics(self.current_chamber)
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        # 1. Heuristic Emission
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Emitted Reflection: {s_i}")
        
        # 2. Geometric Traversal
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, s_i)
        
        # 3. Physics Computation
        prev_dist = self.current_metrics["bruhat_distance"]
        self.current_metrics = self.manifold.get_metrics(self.current_chamber)
        
        word_str = '*'.join(self.current_metrics['shortlex_word']) if self.current_metrics['shortlex_word'] else 'Identity'
        momentum_str = "Escalating (+1)" if self.current_metrics['bruhat_distance'] > prev_dist else "Relaxing (-1)"
        
        print(f"[Topology] Coordinate: {self.current_metrics['coordinate']}")
        print(f"[Algebra]  Shortlex Geodesic: {word_str}")
        print(f"[Physics]  Potential: {self.current_metrics['epistemic_potential']:.2f} | Momentum: {momentum_str} | Gradient (Up/Down): {self.current_metrics['gradient_up']}/{self.current_metrics['gradient_down']}")
        
        # 4. Harmonic Semantic Realization
        response = self.semantics.generate(self.current_metrics, prev_dist)
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