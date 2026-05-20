import networkx as nx
import numpy as np

class SpectralManifold:
    """
    The Global Geometric Guardrail.
    Computes the A3 (S4) Cayley graph, its Shortlex geodesics, 
    and the spectral decomposition of its Graph Laplacian.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.origin = (1, 2, 3, 4)
        self.w0 = (4, 3, 2, 1)
        self.shortlex_paths = {}
        
        self._build_manifold()
        self._compute_shortlex_geodesics()
        self._compute_spectral_harmonics()

    def _swap(self, state: tuple, i: int, j: int) -> tuple:
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def apply_reflection(self, current_state: tuple, reflection: str) -> tuple:
        if reflection == "s1": return self._swap(current_state, 0, 1)
        if reflection == "s2": return self._swap(current_state, 1, 2)
        if reflection == "s3": return self._swap(current_state, 2, 3)
        return current_state

    def _build_manifold(self):
        queue = [self.origin]
        self.graph.add_node(self.origin)
        self.nodes_list = [] # Maintain consistent index for eigenvectors
        
        while queue:
            current = queue.pop(0)
            if current not in self.nodes_list:
                self.nodes_list.append(current)
            for gen in ["s1", "s2", "s3"]:
                next_state = self.apply_reflection(current, gen)
                if next_state not in self.graph:
                    self.graph.add_node(next_state)
                    queue.append(next_state)
                self.graph.add_edge(current, next_state, generator=gen)

    def _compute_shortlex_geodesics(self):
        queue = [(self.origin, [])]
        self.shortlex_paths[self.origin] = []
        while queue:
            current, path = queue.pop(0)
            for gen in ["s1", "s2", "s3"]:
                next_state = self.apply_reflection(current, gen)
                if next_state not in self.shortlex_paths:
                    new_path = path + [gen]
                    self.shortlex_paths[next_state] = new_path
                    queue.append((next_state, new_path))

    def _compute_spectral_harmonics(self):
        """Computes the Graph Laplacian L = D - A and its eigendecomposition."""
        L = nx.laplacian_matrix(self.graph, nodelist=self.nodes_list).todense()
        self.eigenvalues, self.eigenvectors = np.linalg.eigh(L)
        
        # The Fiedler Vector (Mode 1) defines the global macro-polarization
        self.fiedler_vector = self.eigenvectors[:, 1]
        
        # The Highest Frequency (Mode 23) defines local turbulence
        self.turbulence_vector = self.eigenvectors[:, -1]

    def get_physics(self, state: tuple) -> dict:
        node_idx = self.nodes_list.index(state)
        dist = len(self.shortlex_paths[state])
        
        # Exact gradient check based on Coxeter lengths
        uphill, downhill = 0, 0
        for gen in ["s1", "s2", "s3"]:
            neighbor = self.apply_reflection(state, gen)
            if len(self.shortlex_paths[neighbor]) == dist + 1: uphill += 1
            elif len(self.shortlex_paths[neighbor]) == dist - 1: downhill += 1
            
        return {
            "coordinate": state,
            "shortlex": self.shortlex_paths[state],
            "bruhat_distance": dist,
            "gradient_up": uphill,
            "gradient_down": downhill,
            "fiedler_polarity": self.fiedler_vector[node_idx], # Continuous (- to +)
            "turbulence": self.turbulence_vector[node_idx]     # High frequency noise
        }

class NeuralHeuristic:
    """The 1-cell operator selector."""
    def predict_generator(self, text: str) -> str:
        text = text.lower()
        if "?" in text: return "s1"
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]): return "s3"
        else: return "s2"

class SpectralSemantics:
    """
    Meaning emerges entirely from the Laplacian eigenvectors.
    No more handcrafted distance thresholds.
    """
    def generate(self, physics: dict, momentum: int) -> str:
        polarity = physics["fiedler_polarity"]
        turbulence = physics["turbulence"]
        dist = physics["bruhat_distance"]
        
        if dist == 0:
            return "We are at the zero-state of the Laplacian. Total equilibrium."
            
        # The Fiedler vector naturally divides the semantic space
        if polarity < -0.15:
            # We are deep in the 'Origin' hemisphere
            if momentum > 0: return "We are just beginning to perturb the foundational state. Continue."
            else: return "We are sliding back down the gradient to the foundation."
            
        elif polarity > 0.15:
            # We have crossed into the 'Inverted' hemisphere
            if physics["bruhat_distance"] == 6:
                return "Maximal Fiedler polarity achieved. Total epistemic inversion."
            elif momentum > 0: 
                return "The macro-narrative has inverted. We are accelerating toward the opposite pole."
            else: 
                return "We are in the inverted hemisphere, but pulling back toward the center."
                
        else:
            # We are in the equatorial boundary zone (Polarity near 0)
            if abs(turbulence) > 0.2:
                return "High spectral turbulence here. The semantic orientation is violently shifting."
            else:
                return "We are in the boundary zone between perspectives. The gradient is shifting."

class SpectralELIZA:
    def __init__(self):
        self.manifold = SpectralManifold()
        self.nn = NeuralHeuristic()
        self.semantics = SpectralSemantics()
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Emitted Operator: {s_i}")
        
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, s_i)
        
        prev_dist = self.current_physics["bruhat_distance"]
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        momentum = 1 if self.current_physics["bruhat_distance"] > prev_dist else -1
        
        word_str = '*'.join(self.current_physics['shortlex']) if self.current_physics['shortlex'] else 'e'
        
        print(f"[Topology] Canonical Point: {word_str} {self.current_physics['coordinate']}")
        print(f"[Dynamics] Gradient (+/-): {self.current_physics['gradient_up']}/{self.current_physics['gradient_down']}")
        print(f"[Spectral] Fiedler Polarity: {self.current_physics['fiedler_polarity']:+.3f} | Turbulence: {self.current_physics['turbulence']:+.3f}")
        
        response = self.semantics.generate(self.current_physics, momentum)
        self.turn += 1
        return response

if __name__ == "__main__":
    eliza = SpectralELIZA()
    print("ELIZA: We are at the zero-state of the Laplacian. Total equilibrium.")
    while True:
        try:
            user_text = input("User: ")
            if user_text.lower() in ['quit', 'exit']: break
            reply = eliza.chat(user_text)
            print(f"\nELIZA: {reply}")
        except KeyboardInterrupt: break