"""16.py: SQLite persistence + branched syntheses.

  * Persistence moves to a single state.db (SQLite in WAL mode). One-shot
    migration imports any existing state.json + trigrams.json on first run;
    legacy sessions/*.jsonl is left alone for archival inspection. All writes
    are small UPSERTs into the journal — no more full-file rewrites.

  * Branched syntheses: alongside the actual trigram-sampled continuation,
    three biased continuations are generated, one per non-identity sign
    flip in (Fiedler, turbulence). At each step the actual generator's
    spectral delta is sign-flipped, the generator whose delta best matches
    is chosen, and a char from the trigram context that emits that
    generator is sampled — falling back to unbiased sampling when no char
    in the context produces the right generator.

Usage:
    python 16.py                        # interactive
    python 16.py path/to/file.txt       # stream the file
    python 16.py file.txt --rate 30     # stream at 30 chars/sec
    python 16.py --smoke                # no-UI smoke check
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np


STATE_DIR = Path(os.environ.get("ELIZA_STATE_DIR", Path(__file__).parent / "state"))
DB_FILENAME = "state.db"


# --- Manifold + holonomy + analytics: identical to 15.py. ---


class SpectralManifold:
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
        # Cache index lookup — used heavily in branched synthesis.
        self._node_to_idx = {n: i for i, n in enumerate(self.nodes_list)}

    def node_index(self, state):
        return self._node_to_idx[state]

    def get_physics(self, state):
        node_idx = self._node_to_idx[state]
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
    def __init__(self, manifold, modes=(1, 2)):
        self.M = manifold
        phi = np.asarray(self.M.eigenvectors[:, list(modes)])
        self.phi = phi
        n = phi.shape[0]
        self.centroids = np.zeros_like(phi)
        for i, x in enumerate(self.M.nodes_list):
            nbrs = [self.M.apply_reflection(x, g) for g in ["s1", "s2", "s3"]]
            nbr_idxs = [self.M.node_index(y) for y in nbrs]
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
        i = self.M.node_index(state)
        h_idx = int(self.holonomy_target_idx[i])
        h_state = self.M.nodes_list[h_idx]
        return {
            "closes": h_state == state,
            "target_state": h_state,
            "target_word": self.M.shortlex_paths[h_state],
            "curvature": float(self.curvature[i]),
            "band": self.band(float(self.curvature[i])),
        }


class SpectralAnalytics:
    def __init__(self, manifold, reflection_modes=(1, 2)):
        self.M = manifold
        self.reflection_modes = tuple(reflection_modes)
        self.phi_refl = np.asarray(manifold.eigenvectors[:, list(reflection_modes)])

    def shadow_trajectory(self, trajectory, sign_flips):
        if len(trajectory) < 2:
            return list(trajectory)
        idxs = [self.M.node_index(x) for x in trajectory]
        y = self.phi_refl[idxs]
        d = np.diff(y, axis=0)
        signs = np.array(sign_flips, dtype=float)
        d_flipped = d * signs
        y_hat = np.empty_like(y)
        y_hat[0] = y[0]
        y_hat[1:] = y[0] + np.cumsum(d_flipped, axis=0)
        result = []
        for point in y_hat:
            dists = np.linalg.norm(self.phi_refl - point, axis=1)
            result.append(self.M.nodes_list[int(np.argmin(dists))])
        return result


def _word_str(path):
    return "·".join(path) if path else "e"


def char_to_generator(ch):
    return ["s1", "s2", "s3"][ord(ch) % 3]


# --- SQLite-backed Store. ---


class Store:
    """All persistence goes here. WAL mode, autocommit per turn.

    Migrates legacy state.json + trigrams.json on first run (one-shot, idempotent).
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._ensure_schema()
        self._maybe_migrate_legacy()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                n INTEGER,
                ts TEXT,
                user_input TEXT,
                generator TEXT,
                chamber_from TEXT,
                chamber_to TEXT,
                bruhat INTEGER,
                fiedler REAL,
                turbulence REAL,
                holonomy_closes INTEGER,
                holonomy_target TEXT,
                curvature REAL,
                curvature_band TEXT,
                surprise REAL
            );
            CREATE INDEX IF NOT EXISTS turns_session_idx ON turns(session_id);
            CREATE TABLE IF NOT EXISTS chamber_visits (
                chamber TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS edge_traversals (
                from_chamber TEXT NOT NULL,
                generator TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (from_chamber, generator)
            );
            CREATE TABLE IF NOT EXISTS trigrams (
                c1 TEXT NOT NULL,
                c2 TEXT NOT NULL,
                c3 TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (c1, c2, c3)
            );
        """)
        cur.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)",
            (str(self.SCHEMA_VERSION),),
        )
        self.conn.commit()

    def _maybe_migrate_legacy(self):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key='legacy_migrated'")
        if cur.fetchone():
            return
        legacy_state = self.db_path.parent / "state.json"
        legacy_trigrams = self.db_path.parent / "trigrams.json"
        if legacy_state.exists():
            try:
                with open(legacy_state) as f:
                    s = json.load(f)
                for chamber, count in s.get("chamber_visits", {}).items():
                    cur.execute(
                        "INSERT INTO chamber_visits(chamber, count) VALUES (?, ?) "
                        "ON CONFLICT(chamber) DO UPDATE SET count = count + excluded.count",
                        (chamber, count),
                    )
                for from_c, gens in s.get("edge_traversals", {}).items():
                    for gen, count in gens.items():
                        cur.execute(
                            "INSERT INTO edge_traversals(from_chamber, generator, count) "
                            "VALUES (?, ?, ?) "
                            "ON CONFLICT(from_chamber, generator) DO UPDATE SET count = count + excluded.count",
                            (from_c, gen, count),
                        )
                for k in ("holonomy_closes", "holonomy_drifts", "last_chamber", "last_session_ended"):
                    val = s.get(k)
                    if val is not None:
                        cur.execute(
                            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                            (k, str(val)),
                        )
            except Exception:
                pass
        if legacy_trigrams.exists():
            try:
                with open(legacy_trigrams) as f:
                    t = json.load(f)
                for k, inner in t.items():
                    if len(k) >= 2:
                        for c3, count in inner.items():
                            cur.execute(
                                "INSERT INTO trigrams(c1, c2, c3, count) VALUES (?, ?, ?, ?) "
                                "ON CONFLICT(c1, c2, c3) DO UPDATE SET count = count + excluded.count",
                                (k[0], k[1], c3, count),
                            )
            except Exception:
                pass
        cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('legacy_migrated', '1')")
        self.conn.commit()

    # Session lifecycle.
    def start_session(self, ts):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO sessions(started_at) VALUES (?)", (ts,))
        self.conn.commit()
        return cur.lastrowid

    def end_session(self, session_id, ts):
        self.conn.execute("UPDATE sessions SET ended_at = ? WHERE id = ?", (ts, session_id))
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES ('last_session_ended', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (ts,),
        )
        self.conn.commit()

    def session_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        return cur.fetchone()[0]

    def turn_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM turns")
        return cur.fetchone()[0]

    # Per-turn.
    def record_turn(self, session_id, **fields):
        self.conn.execute("""
            INSERT INTO turns(session_id, n, ts, user_input, generator,
                              chamber_from, chamber_to, bruhat,
                              fiedler, turbulence, holonomy_closes,
                              holonomy_target, curvature, curvature_band, surprise)
            VALUES (:session_id, :n, :ts, :user_input, :generator,
                    :chamber_from, :chamber_to, :bruhat,
                    :fiedler, :turbulence, :holonomy_closes,
                    :holonomy_target, :curvature, :curvature_band, :surprise)
        """, dict(session_id=session_id, **fields))

    def increment_chamber_visit(self, chamber, by=1):
        self.conn.execute(
            "INSERT INTO chamber_visits(chamber, count) VALUES (?, ?) "
            "ON CONFLICT(chamber) DO UPDATE SET count = count + excluded.count",
            (chamber, by),
        )

    def increment_edge(self, from_chamber, generator, by=1):
        self.conn.execute(
            "INSERT INTO edge_traversals(from_chamber, generator, count) VALUES (?, ?, ?) "
            "ON CONFLICT(from_chamber, generator) DO UPDATE SET count = count + excluded.count",
            (from_chamber, generator, by),
        )

    def increment_holonomy(self, closes):
        key = "holonomy_closes" if closes else "holonomy_drifts"
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, '1') "
            "ON CONFLICT(key) DO UPDATE SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)",
            (key,),
        )

    def set_last_chamber(self, chamber):
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES ('last_chamber', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (chamber,),
        )

    def commit(self):
        self.conn.commit()

    # Trigrams.
    def increment_trigram(self, c1, c2, c3, by=1):
        self.conn.execute(
            "INSERT INTO trigrams(c1, c2, c3, count) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(c1, c2, c3) DO UPDATE SET count = count + excluded.count",
            (c1, c2, c3, by),
        )

    def load_trigrams(self):
        cur = self.conn.cursor()
        cur.execute("SELECT c1, c2, c3, count FROM trigrams")
        out = {}
        for c1, c2, c3, count in cur.fetchall():
            inner = out.setdefault((c1, c2), {})
            inner[c3] = count
        return out

    # Aggregate reads.
    def get_visits(self):
        cur = self.conn.cursor()
        cur.execute("SELECT chamber, count FROM chamber_visits")
        return dict(cur.fetchall())

    def get_edges(self):
        cur = self.conn.cursor()
        cur.execute("SELECT from_chamber, generator, count FROM edge_traversals")
        out = {}
        for from_c, gen, count in cur.fetchall():
            inner = out.setdefault(from_c, {})
            inner[gen] = count
        return out

    def get_meta(self, key, default=None):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

    def close(self):
        self.conn.commit()
        self.conn.close()


# --- Recorder backed by Store. ---


class SessionRecorder:
    def __init__(self, store):
        self.store = store
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.session_id = store.start_session(ts)
        self.session_start_ts = ts
        self.aggregate = {
            "session_count": store.session_count(),
            "turn_count": store.turn_count(),
            "chamber_visits": store.get_visits(),
            "edge_traversals": store.get_edges(),
            "holonomy_closes": int(store.get_meta("holonomy_closes") or "0"),
            "holonomy_drifts": int(store.get_meta("holonomy_drifts") or "0"),
            "last_chamber": store.get_meta("last_chamber"),
            "last_session_ended": store.get_meta("last_session_ended"),
        }
        self._turn_counter = 0

    def session_start(self, start_word):
        self.aggregate["chamber_visits"][start_word] = (
            self.aggregate["chamber_visits"].get(start_word, 0) + 1
        )
        self.store.increment_chamber_visit(start_word)
        self.store.commit()

    def record_turn(self, *, user_input, generator, from_word, to_word,
                    bruhat, fiedler, turbulence, h_closes, h_target_word,
                    h_curvature, h_band, surprise=None):
        self._turn_counter += 1
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
        self.store.record_turn(
            self.session_id,
            n=self._turn_counter,
            ts=time.strftime("%Y-%m-%dT%H:%M:%S"),
            user_input=user_input,
            generator=generator,
            chamber_from=from_word,
            chamber_to=to_word,
            bruhat=bruhat,
            fiedler=fiedler,
            turbulence=turbulence,
            holonomy_closes=1 if h_closes else 0,
            holonomy_target=h_target_word,
            curvature=h_curvature,
            curvature_band=h_band,
            surprise=surprise,
        )
        self.store.increment_chamber_visit(to_word)
        self.store.increment_edge(from_word, generator)
        self.store.increment_holonomy(h_closes)
        self.store.set_last_chamber(to_word)
        self.store.commit()

    def session_end(self):
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.aggregate["last_session_ended"] = ts
        self.store.end_session(self.session_id, ts)


# --- TrigramPredictor backed by Store. ---


class TrigramPredictor:
    VOCAB_SIZE = 128
    DEFAULT_SYNTH_TEMP = 1.0
    DEFAULT_SYNTH_LEN = 60

    def __init__(self, manifold, store=None, alpha=0.5):
        self.M = manifold
        self.alpha = alpha
        self.store = store
        self.context = ["", ""]
        self.counts = store.load_trigrams() if store is not None else {}

    def n_contexts(self):
        return len(self.counts)

    def n_observations(self):
        return sum(sum(inner.values()) for inner in self.counts.values())

    def update(self, ch):
        c1, c2 = self.context
        if c1 and c2:
            inner = self.counts.setdefault((c1, c2), {})
            inner[ch] = inner.get(ch, 0) + 1
            if self.store is not None:
                self.store.increment_trigram(c1, c2, ch)
        self.context = [c2, ch]

    def save(self):
        if self.store is not None:
            self.store.commit()

    def smoothed_prob(self, c3, c1=None, c2=None):
        if c1 is None: c1 = self.context[0]
        if c2 is None: c2 = self.context[1]
        inner = self.counts.get((c1, c2), {})
        total = sum(inner.values())
        return (inner.get(c3, 0) + self.alpha) / (total + self.alpha * self.VOCAB_SIZE)

    def surprise_bits(self, actual_ch):
        c1, c2 = self.context
        if not c1 or not c2:
            return None
        p = self.smoothed_prob(actual_ch, c1, c2)
        return float(-np.log2(p)) if p > 0 else float("inf")

    def top_predictions(self, n=5):
        c1, c2 = self.context
        if not c1 or not c2:
            return []
        inner = self.counts.get((c1, c2), {})
        if not inner:
            return []
        total = sum(inner.values())
        ranked = sorted(inner.items(), key=lambda kv: -kv[1])[:n]
        return [(c, v / total) for c, v in ranked]

    def predicted_next_chamber(self, current_chamber):
        top = self.top_predictions(n=1)
        if not top:
            return None
        gen = char_to_generator(top[0][0])
        return self.M.apply_reflection(current_chamber, gen)

    def project_text(self, n_chars=None, temperature=None):
        n_chars = n_chars or self.DEFAULT_SYNTH_LEN
        temperature = temperature if temperature is not None else self.DEFAULT_SYNTH_TEMP
        if temperature <= 0:
            temperature = 0.01
        out = []
        c1, c2 = self.context
        for _ in range(n_chars):
            if not c1 or not c2:
                break
            inner = self.counts.get((c1, c2), {})
            if not inner:
                break
            chars = list(inner.keys())
            counts = np.array(list(inner.values()), dtype=float)
            probs = counts ** (1.0 / temperature)
            probs = probs / probs.sum()
            ch = str(np.random.choice(chars, p=probs))
            out.append(ch)
            c1, c2 = c2, ch
        return "".join(out)


# --- Engine with branched syntheses. ---


TRAJECTORY_WINDOW = 24
SHADOW_SIGN_FLIPS = [
    ("Φ̄",   (-1, +1)),
    ("T̄",   (+1, -1)),
    ("Φ̄T̄", (-1, -1)),
]
GENERATORS = ("s1", "s2", "s3")


class Engine:
    def __init__(self, recorder=None, predictor=None):
        self.manifold = SpectralManifold()
        self.holonomy = HolonomyEngine(self.manifold)
        self.analytics = SpectralAnalytics(self.manifold)
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.recorder = recorder
        self.predictor = predictor
        self.trajectory = deque([self.current_chamber], maxlen=TRAJECTORY_WINDOW)
        if recorder:
            recorder.session_start(_word_str(self.current_physics["shortlex"]))

    def step(self, ch):
        surprise = None
        predicted_chamber = None
        if self.predictor is not None:
            surprise = self.predictor.surprise_bits(ch)
            predicted_chamber = self.predictor.predicted_next_chamber(self.current_chamber)

        gen = char_to_generator(ch)
        from_word = _word_str(self.current_physics["shortlex"])
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, gen)
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        to_word = _word_str(self.current_physics["shortlex"])
        h = self.holonomy.at(self.current_chamber)
        self.trajectory.append(self.current_chamber)

        if self.predictor is not None:
            self.predictor.update(ch)
        if self.recorder:
            self.recorder.record_turn(
                user_input=ch,
                generator=gen,
                from_word=from_word,
                to_word=to_word,
                bruhat=self.current_physics["bruhat_distance"],
                fiedler=self.current_physics["fiedler_polarity"],
                turbulence=self.current_physics["turbulence"],
                h_closes=h["closes"],
                h_target_word=_word_str(h["target_word"]),
                h_curvature=h["curvature"],
                h_band=h["band"],
                surprise=surprise,
            )

        return {
            "char": ch,
            "generator": gen,
            "from_word": from_word,
            "to_word": to_word,
            "physics": self.current_physics,
            "holonomy": h,
            "surprise": surprise,
            "predicted_chamber": predicted_chamber,
        }

    def shadow_trajectories(self):
        traj = list(self.trajectory)
        out = {}
        for label, flips in SHADOW_SIGN_FLIPS:
            shadow = self.analytics.shadow_trajectory(traj, flips)
            out[label] = [_word_str(self.manifold.shortlex_paths[x]) for x in shadow]
        return out

    def synthesize_branches(self, n_chars=60):
        if self.predictor is None:
            return {}
        return {
            label: self._project_branched(flips, n_chars)
            for label, flips in SHADOW_SIGN_FLIPS
        }

    def _spectral_deltas(self, chamber):
        idx = self.manifold.node_index(chamber)
        here = np.array([
            self.manifold.fiedler_vector[idx],
            self.manifold.turbulence_vector[idx],
        ])
        deltas = {}
        for g in GENERATORS:
            nxt = self.manifold.apply_reflection(chamber, g)
            n_idx = self.manifold.node_index(nxt)
            deltas[g] = np.array([
                self.manifold.fiedler_vector[n_idx],
                self.manifold.turbulence_vector[n_idx],
            ]) - here
        return deltas

    def _project_branched(self, sign_flips, n_chars):
        out = []
        c1, c2 = self.predictor.context
        chamber = self.current_chamber
        signs = np.array(sign_flips, dtype=float)
        for _ in range(n_chars):
            if not c1 or not c2:
                break
            inner = self.predictor.counts.get((c1, c2), {})
            if not inner:
                break
            chars = list(inner.keys())
            counts = np.array(list(inner.values()), dtype=float)
            probs = counts / counts.sum()
            actual_ch = str(np.random.choice(chars, p=probs))
            actual_gen = char_to_generator(actual_ch)
            deltas = self._spectral_deltas(chamber)
            desired = deltas[actual_gen] * signs
            shadow_gen = min(deltas.items(), key=lambda gd: np.linalg.norm(gd[1] - desired))[0]
            shadow_idx = GENERATORS.index(shadow_gen)
            valid = [(c, cnt) for c, cnt in inner.items() if ord(c) % 3 == shadow_idx]
            if valid:
                vchars = [c for c, _ in valid]
                vcounts = np.array([cnt for _, cnt in valid], dtype=float)
                vprobs = vcounts / vcounts.sum()
                ch = str(np.random.choice(vchars, p=vprobs))
            else:
                ch = actual_ch
            out.append(ch)
            chamber = self.manifold.apply_reflection(chamber, char_to_generator(ch))
            c1, c2 = c2, ch
        return "".join(out)

    def end(self):
        if self.recorder:
            self.recorder.session_end()
        if self.predictor:
            self.predictor.save()


# --- Textual UI. ---


def _build_app(engine, source=None, rate=20.0):
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import Footer, Header, Sparkline, Static

    HISTORY = 200
    SYNTH_REFRESH_EVERY = 20

    class ChamberPanel(Static):
        word = reactive("e")
        coord = reactive("(1, 2, 3, 4)")
        def render(self):
            return f"[bold]Chamber[/bold]   {self.word}\n[dim]{self.coord}[/dim]"

    class HolonomyPanel(Static):
        closes = reactive(False)
        target = reactive("e")
        band = reactive("low")
        kappa = reactive(0.0)
        def render(self):
            verdict = "[green]closes[/green]" if self.closes else f"[yellow]drifts → {self.target}[/yellow]"
            band_color = {"low": "green", "mid": "yellow", "high": "red"}[self.band]
            return (
                f"[bold]ℋ[/bold]   {verdict}\n"
                f"κ={self.kappa:+.3f}   [{band_color}]{self.band}[/{band_color}]"
            )

    class GradientPanel(Static):
        up = reactive(3)
        down = reactive(0)
        last_gen = reactive("·")
        def render(self):
            return (
                f"[bold]Gradient[/bold]   ↑{self.up}  ↓{self.down}\n"
                f"last gen   [cyan]{self.last_gen}[/cyan]"
            )

    class VisitsPanel(Static):
        visits = reactive({})
        def render(self):
            if not self.visits:
                return "[bold]Top by visits[/bold]\n[dim]none yet[/dim]"
            ranked = sorted(self.visits.items(), key=lambda kv: -kv[1])[:8]
            top_count = ranked[0][1] if ranked else 1
            lines = ["[bold]Top by visits[/bold]"]
            for word, count in ranked:
                bar = "█" * max(1, int(15 * count / top_count))
                lines.append(f"{word:>12}  [cyan]{bar}[/cyan] {count}")
            return "\n".join(lines)

    class PowerPanel(Static):
        visits = reactive({})
        lengths = reactive({})
        L_MAX = 6

        def render(self):
            if not self.lengths:
                return "[bold]Top by power[/bold]\n[dim]initialising[/dim]"
            v_max = max(self.visits.values()) if self.visits else 1
            v_max = max(v_max, 1)
            scores = {}
            for word, length in self.lengths.items():
                v = self.visits.get(word, 0)
                lnorm = length / self.L_MAX
                vnorm = v / v_max
                scores[word] = (lnorm * lnorm + vnorm * vnorm) ** 0.5
            ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:8]
            top = ranked[0][1] if ranked and ranked[0][1] > 0 else 1.0
            lines = ["[bold]Top by power[/bold]   [dim]√((L/6)² + (V/Vmax)²)[/dim]"]
            for word, p in ranked:
                length = self.lengths.get(word, 0)
                v = self.visits.get(word, 0)
                bar = "█" * max(1, int(15 * p / top))
                lines.append(f"{word:>12} [magenta]{bar}[/magenta] {p:.2f} [dim](L{length} V{v})[/dim]")
            return "\n".join(lines)

    class PredictionPanel(Static):
        top_chars = reactive([])
        predicted_chamber = reactive("?")
        actual_char = reactive("·")
        n_contexts = reactive(0)
        n_obs = reactive(0)
        mean_surprise = reactive(0.0)
        def render(self):
            lines = [f"[bold]Prediction[/bold]   ctx={self.n_contexts} obs={self.n_obs}"]
            if not self.top_chars:
                lines.append("[dim]type more[/dim]")
            else:
                lines.append(f"next chamber: [cyan]{self.predicted_chamber}[/cyan]")
                for c, p in self.top_chars[:4]:
                    disp = c if c.isprintable() and c != "\n" else f"\\x{ord(c):02x}"
                    marker = "[yellow]◄[/yellow]" if c == self.actual_char else ""
                    bar = "█" * max(1, int(12 * p))
                    lines.append(f"  {disp!r:>5} [cyan]{bar}[/cyan] {p:.2f} {marker}")
            lines.append(f"[dim]μ surprise: {self.mean_surprise:.2f} bits[/dim]")
            return "\n".join(lines)

    class SynthesisPanel(Static):
        actual = reactive("")
        branches = reactive({})
        n_obs = reactive(0)

        def render(self):
            if not self.actual and not self.branches:
                return f"[bold]Synthesis[/bold]\n[dim]waiting for context (obs={self.n_obs})…[/dim]"
            lines = ["[bold]Synthesis[/bold]   [dim]continuations in your style[/dim]"]
            actual_shown = (self.actual or "").replace("\n", "↵").replace("\t", "→")
            lines.append(f"[green]actual[/green]  {actual_shown}")
            colors = {"Φ̄": "magenta", "T̄": "yellow", "Φ̄T̄": "red"}
            for label, text in self.branches.items():
                shown = (text or "").replace("\n", "↵").replace("\t", "→")
                col = colors.get(label, "cyan")
                lines.append(f"[{col}]{label:>6}[/{col}]  {shown}")
            return "\n".join(lines)

    class BranchesPanel(Static):
        actual_tail = reactive([])
        shadows = reactive({})
        def render(self):
            lines = ["[bold]Branches[/bold]   [dim]shadow trajectories under axis-flip[/dim]"]
            tail = " → ".join(self.actual_tail[-6:]) if self.actual_tail else "[dim]none[/dim]"
            lines.append(f"[white]actual[/white]  {tail}")
            colors = {"Φ̄": "magenta", "T̄": "yellow", "Φ̄T̄": "red"}
            for label, traj in self.shadows.items():
                tail = " → ".join(traj[-6:]) if traj else ""
                col = colors.get(label, "cyan")
                lines.append(f"[{col}]{label:>6}[/{col}]  {tail}")
            return "\n".join(lines)

    class StreamPanel(Static):
        text = reactive("")
        def render(self):
            return f"[bold]Stream[/bold]\n[dim]{self.text}[/dim]"

    class ElizaApp(App):
        CSS = """
        Screen { layout: vertical; }
        #top { height: 4; }
        #top > Static { width: 1fr; border: round $primary; padding: 0 1; }
        #sparks { height: 6; }
        .spark-cell { width: 1fr; border: round $primary; padding: 0 1; }
        .spark-cell > Static { height: 1; }
        .spark-cell > Sparkline { height: 2; }
        #middle { height: 12; }
        #middle > Static { width: 1fr; border: round $primary; padding: 0 1; }
        #synthesis { height: 6; border: round $accent; padding: 0 1; }
        #branches { height: 6; border: round $accent; padding: 0 1; }
        #stream { height: 4; border: round $primary; padding: 0 1; }
        Sparkline > .sparkline--max-color { color: $accent; }
        Sparkline > .sparkline--min-color { color: $primary; }
        """

        BINDINGS = [
            Binding("ctrl+r", "reset", "Reset chamber"),
            Binding("ctrl+s", "resynth", "Re-roll synthesis"),
            Binding("ctrl+p", "toggle_play", "Pause/play file"),
            Binding("ctrl+q", "quit", "Quit"),
        ]

        def __init__(self, engine, source=None, rate=20.0):
            super().__init__()
            self.engine = engine
            self.source = source
            self.rate = rate
            self.playing = source is not None
            self.fiedler_hist = deque([0.0], maxlen=HISTORY)
            self.turbulence_hist = deque([0.0], maxlen=HISTORY)
            self.kappa_hist = deque([0.0], maxlen=HISTORY)
            self.surprise_hist = deque([0.0], maxlen=HISTORY)
            self.stream_buf = deque(maxlen=140)
            self._chars_since_synth = 0
            self._surprise_running = 0.0
            self._surprise_count = 0

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with Horizontal(id="top"):
                yield ChamberPanel(id="chamber")
                yield HolonomyPanel(id="holonomy")
                yield GradientPanel(id="gradient")
            with Horizontal(id="sparks"):
                with Vertical(classes="spark-cell"):
                    yield Static("Fiedler polarity")
                    yield Sparkline(list(self.fiedler_hist), id="spark-fiedler")
                with Vertical(classes="spark-cell"):
                    yield Static("Turbulence")
                    yield Sparkline(list(self.turbulence_hist), id="spark-turbulence")
                with Vertical(classes="spark-cell"):
                    yield Static("Curvature κ")
                    yield Sparkline(list(self.kappa_hist), id="spark-kappa")
                with Vertical(classes="spark-cell"):
                    yield Static("Surprise (bits)")
                    yield Sparkline(list(self.surprise_hist), id="spark-surprise")
            with Horizontal(id="middle"):
                yield VisitsPanel(id="visits")
                yield PowerPanel(id="power")
                yield PredictionPanel(id="prediction")
            yield SynthesisPanel(id="synthesis")
            yield BranchesPanel(id="branches")
            yield StreamPanel(id="stream")
            yield Footer()

        def on_mount(self):
            self._refresh_chamber()
            self._source_timer = None
            lengths = {
                _word_str(self.engine.manifold.shortlex_paths[x]):
                    len(self.engine.manifold.shortlex_paths[x])
                for x in self.engine.manifold.nodes_list
            }
            power_panel = self.query_one("#power", PowerPanel)
            power_panel.lengths = lengths
            if self.engine.recorder is not None:
                visits = dict(self.engine.recorder.aggregate["chamber_visits"])
                self.query_one("#visits", VisitsPanel).visits = visits
                power_panel.visits = visits
            if self.engine.predictor is not None:
                pred_panel = self.query_one("#prediction", PredictionPanel)
                pred_panel.n_contexts = self.engine.predictor.n_contexts()
                pred_panel.n_obs = self.engine.predictor.n_observations()
                self._refresh_synthesis()
            self._refresh_branches()
            if self.source is not None:
                self._source_timer = self.set_interval(
                    1.0 / max(self.rate, 0.1), self._tick_source
                )

        def _tick_source(self):
            if not self.playing or self.source is None:
                return
            ch = self.source.read(1)
            if not ch:
                self.playing = False
                if self._source_timer is not None:
                    self._source_timer.stop()
                return
            try:
                self._consume(ch)
            except Exception:
                self.playing = False
                if self._source_timer is not None:
                    self._source_timer.stop()

        def on_key(self, event):
            if "+" in event.key:
                return
            ch = event.character
            if ch is None:
                ch = {"enter": "\n", "tab": "\t", "space": " "}.get(event.key)
            if ch and len(ch) == 1:
                self._consume(ch)

        def action_reset(self):
            self.engine.current_chamber = self.engine.manifold.origin
            self.engine.current_physics = self.engine.manifold.get_physics(
                self.engine.current_chamber
            )
            self.engine.trajectory.clear()
            self.engine.trajectory.append(self.engine.current_chamber)
            self._refresh_chamber()
            self._refresh_branches()

        def action_toggle_play(self):
            if self.source is not None:
                self.playing = not self.playing

        def action_resynth(self):
            self._refresh_synthesis()

        def _refresh_synthesis(self):
            if self.engine.predictor is None:
                return
            panel = self.query_one("#synthesis", SynthesisPanel)
            panel.actual = self.engine.predictor.project_text()
            panel.branches = self.engine.synthesize_branches()
            panel.n_obs = self.engine.predictor.n_observations()

        def _refresh_branches(self):
            shadows = self.engine.shadow_trajectories()
            actual_tail = [
                _word_str(self.engine.manifold.shortlex_paths[x])
                for x in self.engine.trajectory
            ]
            branches = self.query_one("#branches", BranchesPanel)
            branches.actual_tail = actual_tail
            branches.shadows = shadows

        def _consume(self, ch):
            result = self.engine.step(ch)
            phys = result["physics"]
            holo = result["holonomy"]
            self.fiedler_hist.append(phys["fiedler_polarity"])
            self.turbulence_hist.append(phys["turbulence"])
            self.kappa_hist.append(holo["curvature"])
            surprise = result["surprise"]
            self.surprise_hist.append(surprise if surprise is not None else 0.0)
            if surprise is not None:
                self._surprise_running += surprise
                self._surprise_count += 1
            self.stream_buf.append(ch if ch.isprintable() and ch != "\n" else "·")

            self.query_one("#chamber", ChamberPanel).word = result["to_word"]
            self.query_one("#chamber", ChamberPanel).coord = str(phys["coordinate"])

            holo_panel = self.query_one("#holonomy", HolonomyPanel)
            holo_panel.closes = holo["closes"]
            holo_panel.target = _word_str(holo["target_word"])
            holo_panel.band = holo["band"]
            holo_panel.kappa = holo["curvature"]

            grad_panel = self.query_one("#gradient", GradientPanel)
            grad_panel.up = phys["gradient_up"]
            grad_panel.down = phys["gradient_down"]
            grad_panel.last_gen = result["generator"]

            self.query_one("#spark-fiedler", Sparkline).data = list(self.fiedler_hist)
            self.query_one("#spark-turbulence", Sparkline).data = list(self.turbulence_hist)
            self.query_one("#spark-kappa", Sparkline).data = list(self.kappa_hist)
            self.query_one("#spark-surprise", Sparkline).data = list(self.surprise_hist)

            if self.engine.recorder is not None:
                visits_dict = dict(self.engine.recorder.aggregate["chamber_visits"])
            else:
                visits_dict = {}
            self.query_one("#visits", VisitsPanel).visits = visits_dict
            self.query_one("#power", PowerPanel).visits = visits_dict

            if self.engine.predictor is not None:
                pred_panel = self.query_one("#prediction", PredictionPanel)
                pred_panel.top_chars = self.engine.predictor.top_predictions(n=5)
                pred_panel.actual_char = ch
                pchamber = self.engine.predictor.predicted_next_chamber(
                    self.engine.current_chamber
                )
                pred_panel.predicted_chamber = (
                    _word_str(self.engine.manifold.shortlex_paths.get(pchamber, []))
                    if pchamber else "?"
                )
                pred_panel.n_contexts = self.engine.predictor.n_contexts()
                pred_panel.n_obs = self.engine.predictor.n_observations()
                pred_panel.mean_surprise = (
                    self._surprise_running / self._surprise_count
                    if self._surprise_count else 0.0
                )
                self._chars_since_synth += 1
                if self._chars_since_synth >= SYNTH_REFRESH_EVERY:
                    self._chars_since_synth = 0
                    self._refresh_synthesis()

            self._refresh_branches()
            self.query_one("#stream", StreamPanel).text = "".join(self.stream_buf)

        def _refresh_chamber(self):
            phys = self.engine.current_physics
            chamber = self.query_one("#chamber", ChamberPanel)
            chamber.word = _word_str(phys["shortlex"])
            chamber.coord = str(phys["coordinate"])

        def on_unmount(self):
            self.engine.end()

    return ElizaApp(engine, source=source, rate=rate)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", help="Text file to stream (omit for interactive)")
    parser.add_argument("--rate", type=float, default=20.0, help="Chars/sec when streaming a file")
    parser.add_argument("--no-persist", action="store_true", help="Skip persistence")
    parser.add_argument("--smoke", action="store_true", help="Initialise engine and exit (no UI)")
    args = parser.parse_args(argv)

    store = None
    if not args.no_persist:
        store = Store(STATE_DIR / DB_FILENAME)
    recorder = SessionRecorder(store) if store else None
    engine = Engine(recorder=recorder)
    predictor = TrigramPredictor(engine.manifold, store=store)
    engine.predictor = predictor

    try:
        if args.smoke:
            text = "the quick brown fox jumps over the lazy dog. " * 6
            for ch in text:
                engine.step(ch)
            print(f"SMOKE OK; chamber={_word_str(engine.current_physics['shortlex'])}")
            print(f"trigram contexts={predictor.n_contexts()} obs={predictor.n_observations()}")
            print(f"actual:  {predictor.project_text(n_chars=50)!r}")
            for label, text in engine.synthesize_branches(n_chars=50).items():
                print(f"  {label}: {text!r}")
            engine.end()
            return 0

        source = open(args.path, "r") if args.path else None
        app = _build_app(engine, source=source, rate=args.rate)
        try:
            app.run()
        finally:
            if source is not None:
                source.close()
        return 0
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
