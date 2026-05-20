"""Textual dashboard over the spectral manifold, with a learned predictor.

14.py adds the C-layer the readmes promise: a char-trigram model accumulated
from every char you've ever fed (across all sessions). It does three things:

  * Scores SURPRISE per char — -log2 P(actual | last two chars). Sparkline.
  * PREDICTS the next char / generator / chamber from learned context.
  * SYNTHESIZES a sampled continuation in your style. Refreshed every ~20 chars.

Trigrams persist to state/trigrams.json (separate from state.json to keep
that file readable). Loaded at startup so the model keeps learning across
sessions.

Usage:
    python 14.py                        # interactive
    python 14.py path/to/file.txt       # stream the file
    python 14.py file.txt --rate 30     # stream at 30 chars/sec
    python 14.py --smoke                # no-UI smoke check
"""

import argparse
import json
import os
import sys
import time
from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np


STATE_DIR = Path(os.environ.get("ELIZA_STATE_DIR", Path(__file__).parent / "state"))


# --- Manifold + holonomy: identical to 12/13.py, inlined for self-containment. ---


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
    def __init__(self, manifold, modes=(1, 2)):
        self.M = manifold
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


def _word_str(path):
    return "·".join(path) if path else "e"


def char_to_generator(ch):
    return ["s1", "s2", "s3"][ord(ch) % 3]


# --- Learned predictor: char-trigram with Laplace smoothing. ---


class TrigramPredictor:
    """P(c3 | c1, c2) accumulated over all chars ever seen.

    Counts persist as state/trigrams.json across sessions; the longer the user
    feeds text, the more the predictor's distribution approaches their style.

    Surprise of an actual char is -log2 P(c | last two chars) under Laplace
    smoothing (α small, vocab size = 128 ASCII). Maximum surprise ≈ 7 bits
    (uniform over ASCII); typical English text settles below 5 once the model
    has a few thousand chars to learn from.
    """

    VOCAB_SIZE = 128
    DEFAULT_SYNTH_TEMP = 1.0
    DEFAULT_SYNTH_LEN = 60

    def __init__(self, manifold, alpha=0.5, persist_path=None):
        self.M = manifold
        self.alpha = alpha
        self.counts = {}
        self.context = ["", ""]
        self.persist_path = persist_path
        self._dirty = 0
        self._flush_every = 200
        if persist_path is not None and persist_path.exists():
            self._load()

    def _load(self):
        with open(self.persist_path) as f:
            state = json.load(f)
        for k, inner in state.items():
            if len(k) >= 2:
                self.counts[(k[0], k[1])] = dict(inner)

    def save(self):
        if self.persist_path is None:
            return
        state = {f"{c1}{c2}": inner for (c1, c2), inner in self.counts.items()}
        tmp = self.persist_path.with_suffix(".json.tmp")
        with open(tmp, "w") as f:
            json.dump(state, f)
        tmp.replace(self.persist_path)

    def n_contexts(self):
        return len(self.counts)

    def n_observations(self):
        return sum(sum(inner.values()) for inner in self.counts.values())

    def update(self, ch):
        c1, c2 = self.context
        if c1 and c2:
            inner = self.counts.setdefault((c1, c2), {})
            inner[ch] = inner.get(ch, 0) + 1
        self.context = [c2, ch]
        self._dirty += 1
        if self._dirty >= self._flush_every:
            self.save()
            self._dirty = 0

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


# --- Recorder: Layer-1 persistence as 12.py. ---


class SessionRecorder:
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
        self._turn_counter = 0
        self._dirty = 0
        self._flush_every = 50

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
        self._emit({
            "event": "turn",
            "n": self._turn_counter,
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
            "surprise": surprise,
        })
        self._dirty += 1
        if self._dirty >= self._flush_every:
            self._save_aggregate()
            self._dirty = 0

    def session_end(self):
        if self.session_log.closed:
            return
        self.aggregate["last_session_ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._emit({"event": "session_end", "ts": self.aggregate["last_session_ended"]})
        self._save_aggregate()
        self.session_log.close()


# --- Engine: walker + predictor coupled together. ---


class Engine:
    def __init__(self, recorder=None, predictor=None):
        self.manifold = SpectralManifold()
        self.holonomy = HolonomyEngine(self.manifold)
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.recorder = recorder
        self.predictor = predictor
        if recorder:
            recorder.session_start(_word_str(self.current_physics["shortlex"]))

    def step(self, ch):
        # Surprise + prediction are computed under the PRE-update context.
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
                f"κ={self.kappa:+.3f}   "
                f"[{band_color}]{self.band}[/{band_color}]"
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
                return "[dim]no visits yet[/dim]"
            ranked = sorted(self.visits.items(), key=lambda kv: -kv[1])[:8]
            top_count = ranked[0][1] if ranked else 1
            lines = ["[bold]Top chambers[/bold]"]
            for word, count in ranked:
                bar_width = int(20 * count / top_count)
                bar = "█" * bar_width
                lines.append(f"{word:>16}  [cyan]{bar}[/cyan] {count}")
            return "\n".join(lines)

    class PredictionPanel(Static):
        top_chars = reactive([])     # [(char, prob)]
        predicted_chamber = reactive("?")
        actual_char = reactive("·")
        n_contexts = reactive(0)
        n_obs = reactive(0)
        mean_surprise = reactive(0.0)

        def render(self):
            lines = [f"[bold]Prediction[/bold]   contexts={self.n_contexts}  obs={self.n_obs}"]
            if not self.top_chars:
                lines.append("[dim]insufficient context — type more[/dim]")
            else:
                lines.append(f"next-chamber guess: [cyan]{self.predicted_chamber}[/cyan]")
                lines.append("[dim]most likely next chars:[/dim]")
                for c, p in self.top_chars[:5]:
                    disp = c if c.isprintable() and c != "\n" else f"\\x{ord(c):02x}"
                    marker = "[yellow]◄ actual[/yellow]" if c == self.actual_char else ""
                    bar = "█" * max(1, int(20 * p))
                    lines.append(f"  {disp!r:>6}  [cyan]{bar}[/cyan] {p:.2f} {marker}")
            lines.append(f"[dim]mean surprise: {self.mean_surprise:.2f} bits[/dim]")
            return "\n".join(lines)

    class SynthesisPanel(Static):
        text = reactive("")
        n_obs = reactive(0)

        def render(self):
            if not self.text:
                return f"[bold]Synthesis[/bold]\n[dim]waiting for enough context (obs={self.n_obs})…[/dim]"
            shown = self.text.replace("\n", "↵").replace("\t", "→")
            return f"[bold]Synthesis[/bold]   [dim](sampled continuation in your style)[/dim]\n[green]{shown}[/green]"

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
        #synthesis { height: 5; border: round $accent; padding: 0 1; }
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
                yield PredictionPanel(id="prediction")
            yield SynthesisPanel(id="synthesis")
            yield StreamPanel(id="stream")
            yield Footer()

        def on_mount(self):
            self._refresh_chamber()
            self._source_timer = None
            if self.engine.recorder is not None:
                self.query_one("#visits", VisitsPanel).visits = dict(
                    self.engine.recorder.aggregate["chamber_visits"]
                )
            if self.engine.predictor is not None:
                pred_panel = self.query_one("#prediction", PredictionPanel)
                pred_panel.n_contexts = self.engine.predictor.n_contexts()
                pred_panel.n_obs = self.engine.predictor.n_observations()
                self._refresh_synthesis()
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
            self.engine.current_physics = self.engine.manifold.get_physics(self.engine.current_chamber)
            self._refresh_chamber()

        def action_toggle_play(self):
            if self.source is not None:
                self.playing = not self.playing

        def action_resynth(self):
            self._refresh_synthesis()

        def _refresh_synthesis(self):
            if self.engine.predictor is None:
                return
            text = self.engine.predictor.project_text()
            panel = self.query_one("#synthesis", SynthesisPanel)
            panel.text = text
            panel.n_obs = self.engine.predictor.n_observations()

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

            if self.engine.predictor is not None:
                pred_panel = self.query_one("#prediction", PredictionPanel)
                # IMPORTANT: top_predictions reflects the context AFTER update,
                # which is the right context for "what comes next from here."
                pred_panel.top_chars = self.engine.predictor.top_predictions(n=5)
                pred_panel.actual_char = ch
                pchamber = self.engine.predictor.predicted_next_chamber(self.engine.current_chamber)
                pred_panel.predicted_chamber = _word_str(self.engine.manifold.shortlex_paths.get(pchamber, [])) if pchamber else "?"
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
    parser.add_argument("--no-persist", action="store_true", help="Skip recorder + predictor persistence")
    parser.add_argument("--smoke", action="store_true", help="Initialise engine and exit (no UI)")
    args = parser.parse_args(argv)

    recorder = None if args.no_persist else SessionRecorder()
    # Predictor shares the state dir but uses its own file.
    pred_path = None if args.no_persist else STATE_DIR / "trigrams.json"
    # Manifold is built inside Engine, but the predictor needs it too. So
    # build engine first, then thread the predictor through after construction.
    engine = Engine(recorder=recorder)
    predictor = TrigramPredictor(engine.manifold, persist_path=pred_path)
    engine.predictor = predictor

    if args.smoke:
        text = "the quick brown fox jumps over the lazy dog. " * 6
        for ch in text:
            engine.step(ch)
        synth = predictor.project_text(n_chars=60)
        print(f"SMOKE OK; chamber={_word_str(engine.current_physics['shortlex'])}")
        print(f"trigram contexts={predictor.n_contexts()} obs={predictor.n_observations()}")
        print(f"synthesis: {synth!r}")
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
