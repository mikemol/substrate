"""Textual dashboard over the spectral manifold.

Char-level streaming: every keystroke (or every char from a file) emits a
generator and walks the chamber one step. Sparklines of Fiedler, turbulence,
and curvature update live so the manifold's behaviour is legible at a glance.

Usage:
    python 13.py                        # interactive: type chars
    python 13.py path/to/file.txt       # stream the file
    python 13.py path/to/file.txt --rate 30   # stream at 30 chars/sec
    python 13.py --smoke                # no-UI smoke check
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


# --- Manifold + holonomy: identical to 12.py, inlined for self-containment. ---


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


# --- Char-level router: ord(ch) % 3, deterministic and uniform. ---


def char_to_generator(ch):
    return ["s1", "s2", "s3"][ord(ch) % 3]


# --- Recorder: same Layer-1 persistence as 12.py, but optional. ---


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
        self._flush_every = 50  # batch aggregate writes — char-level fires hot

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
                    h_curvature, h_band):
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


# --- Engine: stateless physics + walker that the UI drives one char at a time. ---


class Engine:
    """Single-step walker, decoupled from any UI."""

    def __init__(self, recorder=None):
        self.manifold = SpectralManifold()
        self.holonomy = HolonomyEngine(self.manifold)
        self.current_chamber = self.manifold.origin
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        self.recorder = recorder
        if recorder:
            recorder.session_start(_word_str(self.current_physics["shortlex"]))

    def step(self, ch):
        gen = char_to_generator(ch)
        from_word = _word_str(self.current_physics["shortlex"])
        self.current_chamber = self.manifold.apply_reflection(self.current_chamber, gen)
        self.current_physics = self.manifold.get_physics(self.current_chamber)
        to_word = _word_str(self.current_physics["shortlex"])
        h = self.holonomy.at(self.current_chamber)
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
            )
        return {
            "char": ch,
            "generator": gen,
            "from_word": from_word,
            "to_word": to_word,
            "physics": self.current_physics,
            "holonomy": h,
        }

    def end(self):
        if self.recorder:
            self.recorder.session_end()


# --- Textual UI. ---


def _build_app(engine, source=None, rate=20.0):
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import Footer, Header, Sparkline, Static

    HISTORY = 200

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

    class StreamPanel(Static):
        text = reactive("")

        def render(self):
            return f"[bold]Stream[/bold]\n[dim]{self.text}[/dim]"

    class ElizaApp(App):
        CSS = """
        Screen { layout: vertical; }
        #top { height: 5; }
        #top > Static { width: 1fr; border: round $primary; padding: 0 1; }
        #sparks { height: 7; }
        .spark-cell { width: 1fr; border: round $primary; padding: 0 1; }
        .spark-cell > Static { height: 1; }
        .spark-cell > Sparkline { height: 3; }
        #middle { height: 12; }
        #middle > Static { width: 1fr; border: round $primary; padding: 0 1; }
        #stream { height: 5; border: round $primary; padding: 0 1; }
        Sparkline > .sparkline--max-color { color: $accent; }
        Sparkline > .sparkline--min-color { color: $primary; }
        """

        BINDINGS = [
            Binding("ctrl+r", "reset", "Reset chamber"),
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
            self.stream_buf = deque(maxlen=140)

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
            with Horizontal(id="middle"):
                yield VisitsPanel(id="visits")
            yield StreamPanel(id="stream")
            yield Footer()

        def on_mount(self):
            self._refresh_chamber()
            self._source_timer = None
            if self.engine.recorder is not None:
                self.query_one("#visits", VisitsPanel).visits = dict(
                    self.engine.recorder.aggregate["chamber_visits"]
                )
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
                # Screen may be tearing down (e.g. pilot test exit); stop streaming.
                self.playing = False
                if self._source_timer is not None:
                    self._source_timer.stop()

        def on_key(self, event):
            # Bound combos are routed via BINDINGS; skip modifiers here.
            if "+" in event.key:
                return
            ch = event.character
            # Some terminals deliver Enter/Tab/Space as named keys with no
            # character; map them explicitly so they enter the chamber walk.
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

        def _consume(self, ch):
            result = self.engine.step(ch)
            phys = result["physics"]
            holo = result["holonomy"]
            self.fiedler_hist.append(phys["fiedler_polarity"])
            self.turbulence_hist.append(phys["turbulence"])
            self.kappa_hist.append(holo["curvature"])
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

            if self.engine.recorder is not None:
                visits_dict = dict(self.engine.recorder.aggregate["chamber_visits"])
            else:
                visits_dict = {}
            self.query_one("#visits", VisitsPanel).visits = visits_dict
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
    parser.add_argument("--no-persist", action="store_true", help="Skip the session recorder")
    parser.add_argument("--smoke", action="store_true", help="Initialise engine and exit (no UI)")
    args = parser.parse_args(argv)

    recorder = None if args.no_persist else SessionRecorder()
    engine = Engine(recorder=recorder)

    if args.smoke:
        for ch in "Hello, world.":
            engine.step(ch)
        engine.end()
        print("SMOKE OK; final chamber:", _word_str(engine.current_physics["shortlex"]))
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
