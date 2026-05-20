import networkx as nx
import numpy as np


class SpectralManifold:
    """Cayley graph of S4 with shortlex geodesics and Laplacian harmonics."""
    def __init__(self):
        self.graph = nx.Graph()
        self.origin = (1, 2, 3, 4)
        self.w0 = (4, 3, 2, 1)
        self.shortlex_paths = {}
        self._build_manifold()
        self._compute_shortlex_geodesics()
        self._compute_spectral_harmonics()

    def _swap(self, state, i, j):
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def apply_reflection(self, current_state, reflection):
        if reflection == "s1": return self._swap(current_state, 0, 1)
        if reflection == "s2": return self._swap(current_state, 1, 2)
        if reflection == "s3": return self._swap(current_state, 2, 3)
        return current_state

    def _build_manifold(self):
        queue = [self.origin]
        self.graph.add_node(self.origin)
        self.nodes_list = []
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
        L = nx.laplacian_matrix(self.graph, nodelist=self.nodes_list).todense()
        self.eigenvalues, self.eigenvectors = np.linalg.eigh(L)
        origin_idx = self.nodes_list.index(self.origin)
        # eigh sign is arbitrary; orient so origin sits at the negative end of
        # Fiedler, then "origin hemisphere" / "inverted hemisphere" line up
        # with where the origin and w0 actually are.
        fiedler = self.eigenvectors[:, 1]
        if fiedler[origin_idx] > 0:
            fiedler = -fiedler
        self.fiedler_vector = fiedler
        # Mode 23 on this graph is just (-1)^length (bipartite parity) — already
        # captured by Bruhat distance, so it gives zero variation as a readout.
        # Mode 2 is the next-lowest-frequency global mode after Fiedler and
        # varies across the chamber set.
        self.turbulence_vector = self.eigenvectors[:, 2]

    def get_physics(self, state):
        node_idx = self.nodes_list.index(state)
        dist = len(self.shortlex_paths[state])
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
            "fiedler_polarity": float(self.fiedler_vector[node_idx]),
            "turbulence": float(self.turbulence_vector[node_idx]),
        }


class NeuralHeuristic:
    """The 1-cell operator selector."""
    def predict_generator(self, text):
        text = text.lower()
        if "?" in text: return "s1"
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]): return "s3"
        else: return "s2"


# Three-clause readout: G (shortlex path) + C (gradient + momentum) + S (spectral
# band). Each clause quotes structure the manifold already computes, so output
# variety grows from the physics, not from a synonym table.

G_FRAGMENTS = {
    0: ["From rest at the foundational point",
        "At the zero-state, the empty word",
        "At the origin chamber, before any reflection"],
    1: ["One reflection in: {word}",
        "A single step along {word}",
        "After {word} alone"],
    2: ["Two reflections along {word}",
        "The path {word} has unfolded",
        "Having traversed {word}"],
    3: ["Midway, along {word}",
        "Through the three-step word {word}",
        "The geodesic {word} brings us here"],
    4: ["Four steps deep along {word}",
        "The longer path {word} now lies behind us",
        "Having walked {word}"],
    5: ["Near the far end, after {word}",
        "The five-step geodesic {word} carries us close to the antipode",
        "Almost the longest word, {word}"],
    6: ["The longest word {word} has been spelled out",
        "The full diameter, {word}, behind us",
        "At the antipodal chamber, having said {word}"],
}

C_GRADIENT = {
    (3, 0): ["every neighbour ascends",
             "the local cone opens uniformly upward",
             "all three reflections lead away from rest"],
    (2, 1): ["two ways forward, one back",
             "the gradient leans uphill",
             "the local cone tilts away from the origin"],
    (1, 2): ["one way forward, two back",
             "the gradient leans downhill",
             "the local cone tilts back toward rest"],
    (0, 3): ["every neighbour descends",
             "the local cone closes downward",
             "all three reflections lead back toward rest"],
}

C_MOMENTUM = {
    +1: ["and we just stepped up",
         "carried upward this turn",
         "with the last step ascending"],
    -1: ["and we just stepped down",
         "relaxed downward this turn",
         "with the last step descending"],
}

S_POLARITY = [
    (-1.00, -0.20, "rooted deep in the origin hemisphere"),
    (-0.20, -0.05, "still in the origin hemisphere"),
    (-0.05, +0.05, "on the equatorial seam"),
    (+0.05, +0.20, "in the inverted hemisphere"),
    (+0.20, +1.00, "close to the inverted pole"),
]

S_TURBULENCE = [
    (0.00, 0.05, "the harmonics are quiet"),
    (0.05, 0.15, "low harmonics ride underneath"),
    (0.15, 0.25, "the harmonics are ringing"),
    (0.25, 1.00, "the high-frequency harmonics are turbulent"),
]


def _pick(options, key):
    return options[hash(key) % len(options)]


def _band(value, table):
    for lo, hi, label in table:
        if lo <= value < hi:
            return label
    return table[-1][2]


class SemanticReadout:
    """Three-clause output: G/C/S layer fragments composed per turn."""

    def generate(self, physics, momentum):
        dist = physics["bruhat_distance"]
        word = physics["shortlex"]
        word_str = "·".join(word) if word else "e"
        word_key = tuple(word)

        g_template = _pick(G_FRAGMENTS[dist], ("G", word_key))
        g_clause = g_template.format(word=word_str)

        grad_key = (physics["gradient_up"], physics["gradient_down"])
        c_left = _pick(C_GRADIENT[grad_key], ("C", grad_key, word_key))
        if dist > 0:
            c_right = _pick(C_MOMENTUM[momentum], ("CM", momentum, word_key))
            c_clause = f"{c_left}, {c_right}"
        else:
            c_clause = c_left
        c_clause = c_clause[0].upper() + c_clause[1:]

        s_clause = (f"{_band(physics['fiedler_polarity'], S_POLARITY)}; "
                    f"{_band(abs(physics['turbulence']), S_TURBULENCE)}")

        return f"{g_clause}. {c_clause}; {s_clause}."


class SpectralELIZA:
    def __init__(self):
        self.manifold = SpectralManifold()
        self.nn = NeuralHeuristic()
        self.semantics = SemanticReadout()
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.turn = 1

    def opening(self):
        return self.semantics.generate(self.current_physics, momentum=1)

    def chat(self, user_input):
        print(f"\n--- Turn {self.turn} ---")
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Emitted Operator: {s_i}")

        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, s_i)
        prev_dist = self.current_physics["bruhat_distance"]
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        momentum = 1 if self.current_physics["bruhat_distance"] > prev_dist else -1

        word_str = "·".join(self.current_physics["shortlex"]) if self.current_physics["shortlex"] else "e"
        print(f"[Topology] Canonical Point: {word_str} {self.current_physics['coordinate']}")
        print(f"[Dynamics] Gradient (+/-): {self.current_physics['gradient_up']}/{self.current_physics['gradient_down']}")
        print(f"[Spectral] Fiedler Polarity: {self.current_physics['fiedler_polarity']:+.3f} | Turbulence: {self.current_physics['turbulence']:+.3f}")

        response = self.semantics.generate(self.current_physics, momentum)
        self.turn += 1
        return response


if __name__ == "__main__":
    eliza = SpectralELIZA()
    print(f"ELIZA: {eliza.opening()}")
    while True:
        try:
            user_text = input("User: ")
            if user_text.lower() in ["quit", "exit"]: break
            reply = eliza.chat(user_text)
            print(f"\nELIZA: {reply}")
        except KeyboardInterrupt: break
