import json
import os
import time
from pathlib import Path

import networkx as nx
import numpy as np


STATE_DIR = Path(os.environ.get("ELIZA_STATE_DIR", Path(__file__).parent / "state"))


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
        if self.eigenvectors[origin_idx, 1] > 0:
            self.eigenvectors[:, 1] = -self.eigenvectors[:, 1]
        self.fiedler_vector = self.eigenvectors[:, 1]
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


class HolonomyEngine:
    """G→C→S→G round-trip in the macro 2D spectral embedding (modes 1,2)."""

    def __init__(self, manifold, modes=(1, 2)):
        self.M = manifold
        self.modes = tuple(modes)
        phi = np.asarray(self.M.eigenvectors[:, list(modes)])
        self.phi = phi
        n = phi.shape[0]
        self.centroids = np.zeros_like(phi)
        for i, x in enumerate(self.M.nodes_list):
            nbrs = [self.M.apply_reflection(x, g) for g in ["s1", "s2", "s3"]]
            nbr_idxs = [self.M.nodes_list.index(y) for y in nbrs]
            self.centroids[i] = phi[nbr_idxs].mean(axis=0)
        diffs = phi[:, None, :] - self.centroids[None, :, :]
        sq = (diffs ** 2).sum(axis=2)
        self.holonomy_target_idx = sq.argmin(axis=0)
        self.curvature = np.linalg.norm(phi - self.centroids, axis=1)
        sorted_kappa = np.sort(self.curvature)
        self.kappa_low_thresh = float(sorted_kappa[n // 3])
        self.kappa_high_thresh = float(sorted_kappa[2 * n // 3])

    def band(self, kappa):
        if kappa < self.kappa_low_thresh: return "low"
        if kappa < self.kappa_high_thresh: return "mid"
        return "high"

    def at(self, state):
        i = self.M.nodes_list.index(state)
        h_idx = int(self.holonomy_target_idx[i])
        h_state = self.M.nodes_list[h_idx]
        return {
            "closes": h_state == state,
            "target_state": h_state,
            "target_word": self.M.shortlex_paths[h_state],
            "curvature": float(self.curvature[i]),
            "band": self.band(float(self.curvature[i])),
        }


class NeuralHeuristic:
    """The 1-cell operator selector."""
    def predict_generator(self, text):
        text = text.lower()
        if "?" in text: return "s1"
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]): return "s3"
        else: return "s2"


def _word_str(path):
    return "·".join(path) if path else "e"


class SessionRecorder:
    """Per-session JSONL log + rolling aggregate state. No behaviour changes —
    purely accumulates traces. Aggregate is atomic-rewritten after each turn so
    a Ctrl-C only risks partial events in the JSONL, never aggregate corruption.
    """

    SCHEMA_VERSION = 1

    def __init__(self, state_dir=None):
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.aggregate_file = self.state_dir / "state.json"
        self.sessions_dir = self.state_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.aggregate = self._load_aggregate()
        ts_filename = f"{time.strftime('%Y%m%dT%H%M%S')}_{os.getpid()}"
        self.session_log = open(
            self.sessions_dir / f"{ts_filename}.jsonl", "a", buffering=1
        )
        self.session_start_ts = time.strftime("%Y-%m-%dT%H:%M:%S")

    def _load_aggregate(self):
        if self.aggregate_file.exists():
            with open(self.aggregate_file) as f:
                return json.load(f)
        return {
            "schema_version": self.SCHEMA_VERSION,
            "session_count": 0,
            "turn_count": 0,
            "chamber_visits": {},
            "edge_traversals": {},
            "holonomy_closes": 0,
            "holonomy_drifts": 0,
            "last_chamber": None,
            "last_session_ended": None,
        }

    def _save_aggregate(self):
        tmp = self.aggregate_file.with_suffix(".json.tmp")
        with open(tmp, "w") as f:
            json.dump(self.aggregate, f, indent=2)
        tmp.replace(self.aggregate_file)

    def _emit(self, event):
        self.session_log.write(json.dumps(event) + "\n")

    def session_start(self, start_word):
        self.aggregate["session_count"] += 1
        self.aggregate["chamber_visits"][start_word] = (
            self.aggregate["chamber_visits"].get(start_word, 0) + 1
        )
        self._emit({
            "event": "session_start",
            "ts": self.session_start_ts,
            "start_chamber": start_word,
        })
        self._save_aggregate()

    def record_turn(self, *, n, user_input, generator, from_word, to_word,
                    bruhat, fiedler, turbulence, h_closes, h_target_word,
                    h_curvature, h_band):
        self.aggregate["turn_count"] += 1
        self.aggregate["chamber_visits"][to_word] = (
            self.aggregate["chamber_visits"].get(to_word, 0) + 1
        )
        edges = self.aggregate["edge_traversals"].setdefault(from_word, {})
        edges[generator] = edges.get(generator, 0) + 1
        if h_closes:
            self.aggregate["holonomy_closes"] += 1
        else:
            self.aggregate["holonomy_drifts"] += 1
        self.aggregate["last_chamber"] = to_word
        self._emit({
            "event": "turn",
            "n": n,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "user_input": user_input,
            "generator": generator,
            "chamber_from": from_word,
            "chamber_to": to_word,
            "bruhat": bruhat,
            "fiedler": fiedler,
            "turbulence": turbulence,
            "holonomy_closes": h_closes,
            "holonomy_target": h_target_word,
            "curvature": h_curvature,
            "curvature_band": h_band,
        })
        self._save_aggregate()

    def session_end(self):
        self.aggregate["last_session_ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._emit({"event": "session_end", "ts": self.aggregate["last_session_ended"]})
        self._save_aggregate()
        self.session_log.close()


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

H_CLOSES = {
    "low":  ["the interpretive round-trip closes cleanly",
             "the macro round-trip lands back here",
             "ℋ closes on itself"],
    "mid":  ["the round-trip closes through measurable curvature",
             "the local cell is non-trivial, but ℋ still closes",
             "curvature is present, yet the round-trip lands back here"],
    "high": ["high curvature, but ℋ closes",
             "the round-trip closes only because the shadow nearly coincides",
             "strong local curvature, and yet no drift"],
}

H_DRIFTS = {
    "low":  ["the round-trip drifts gently to {target}",
             "a faint shadow at {target}",
             "ℋ lands one chamber off, at {target}"],
    "mid":  ["the round-trip drifts to the shadow chamber {target}",
             "the interpretive cell points to {target}, not here",
             "ℋ falls toward {target}"],
    "high": ["ℋ drifts hard to the shadow at {target}",
             "the interpretive cell strongly favours {target} over this chamber",
             "the round-trip lands far off, at {target}"],
}


def _pick(options, key):
    return options[hash(key) % len(options)]


def _band(value, table):
    for lo, hi, label in table:
        if lo <= value < hi:
            return label
    return table[-1][2]


class SemanticReadout:
    """Four-clause output: G/C/S/H layer fragments composed per turn."""

    def __init__(self, holonomy_engine):
        self.H = holonomy_engine

    def generate(self, physics, momentum, state):
        dist = physics["bruhat_distance"]
        word = physics["shortlex"]
        word_str = _word_str(word)
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

        h = self.H.at(state)
        if h["closes"]:
            h_template = _pick(H_CLOSES[h["band"]], ("H", "close", h["band"], word_key))
            h_clause = h_template
        else:
            target_word = _word_str(h["target_word"])
            h_template = _pick(H_DRIFTS[h["band"]], ("H", "drift", h["band"], word_key))
            h_clause = h_template.format(target=target_word)

        return f"{g_clause}. {c_clause}; {s_clause}; {h_clause}."


class SpectralELIZA:
    def __init__(self, state_dir=None):
        self.manifold = SpectralManifold()
        self.holonomy = HolonomyEngine(self.manifold)
        self.nn = NeuralHeuristic()
        self.semantics = SemanticReadout(self.holonomy)
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.turn = 1
        self.recorder = SessionRecorder(state_dir=state_dir)
        self.recorder.session_start(_word_str(self.current_physics["shortlex"]))

    def opening(self):
        base = self.semantics.generate(
            self.current_physics, momentum=1, state=self.current_chamber
        )
        agg = self.recorder.aggregate
        # session_count is already incremented for THIS session; >1 means there
        # was at least one prior session in the persisted state.
        if agg["session_count"] <= 1:
            return base
        visits = agg["chamber_visits"]
        top_chamber, top_count = max(visits.items(), key=lambda kv: kv[1])
        return (
            f"{base}\n"
            f"[Memory] {agg['session_count']} sessions, "
            f"{agg['turn_count']} turns logged; "
            f"most-visited chamber: {top_chamber} ({top_count}× visits); "
            f"ℋ-closes {agg['holonomy_closes']} / drifts {agg['holonomy_drifts']}; "
            f"last session ended at {agg['last_chamber']}."
        )

    def chat(self, user_input):
        print(f"\n--- Turn {self.turn} ---")
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Emitted Operator: {s_i}")

        from_word = _word_str(self.current_physics["shortlex"])
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, s_i)
        prev_dist = self.current_physics["bruhat_distance"]
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        momentum = 1 if self.current_physics["bruhat_distance"] > prev_dist else -1

        h = self.holonomy.at(self.current_chamber)
        to_word = _word_str(self.current_physics["shortlex"])
        h_word = _word_str(h["target_word"])

        print(f"[Topology] Canonical Point: {to_word} {self.current_physics['coordinate']}")
        print(f"[Dynamics] Gradient (+/-): {self.current_physics['gradient_up']}/{self.current_physics['gradient_down']}")
        print(f"[Spectral] Fiedler Polarity: {self.current_physics['fiedler_polarity']:+.3f} | Turbulence: {self.current_physics['turbulence']:+.3f}")
        print(f"[Holonomy] κ={h['curvature']:.3f} ({h['band']}), target={h_word}, "
              f"{'closes' if h['closes'] else 'drifts'}")

        self.recorder.record_turn(
            n=self.turn,
            user_input=user_input,
            generator=s_i,
            from_word=from_word,
            to_word=to_word,
            bruhat=self.current_physics["bruhat_distance"],
            fiedler=self.current_physics["fiedler_polarity"],
            turbulence=self.current_physics["turbulence"],
            h_closes=h["closes"],
            h_target_word=h_word,
            h_curvature=h["curvature"],
            h_band=h["band"],
        )

        response = self.semantics.generate(self.current_physics, momentum, self.current_chamber)
        self.turn += 1
        return response

    def end(self):
        self.recorder.session_end()


if __name__ == "__main__":
    eliza = SpectralELIZA()
    try:
        print(f"ELIZA: {eliza.opening()}")
        while True:
            try:
                user_text = input("User: ")
            except KeyboardInterrupt:
                break
            if user_text.lower() in ["quit", "exit"]: break
            reply = eliza.chat(user_text)
            print(f"\nELIZA: {reply}")
    finally:
        eliza.end()
