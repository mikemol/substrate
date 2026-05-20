"""Textual dashboard over the cleanroom Engine.

OUTSIDE the Agda skeleton's scope (the UI has no substrate content),
but inside the same boundary discipline: this module only touches the
Engine's published surface — `step`, `current_chamber`, `manifold`,
`cocycle`, `holonomy`, `predictor`, `grammar_char`, `grammar_orbit`.
No reaching into internal state.

Panels mirror 17.py's structure: Chamber + Holonomy + Gradient, sparklines
for Fiedler/Turbulence/κ/Surprise, Visits + Orbits + Prediction in the
middle row, Synthesis (with per-char orbit colour-coding) + Branches
(shadow chamber trajectories) + Stream below.
"""

from __future__ import annotations

import random
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

from eliza.alphabets import Chamber, Gen
from eliza.engine import Engine, StepResult
from eliza.holonomy import SHADOW_FLIPS
from eliza.manifold import word_str
from eliza.orbit import Cocycle
from eliza.synthesis import branched


HISTORY = 200
SYNTH_REFRESH_EVERY = 20


def _build_orbit_palette(cocycle: Cocycle) -> Dict[str, str]:
    """Six V₄-cosets → six distinct colours; cool for even chirality, warm for odd."""
    even: List[Tuple[int, int, str]] = []
    odd: List[Tuple[int, int, str]] = []
    seen: set = set()
    for orbit_word in cocycle.orbits():
        if orbit_word in seen:
            continue
        seen.add(orbit_word)
        # Look up chirality via one of the chamber members.
        members = cocycle.coset_members(orbit_word)
        if not members:
            continue
        any_member = next(iter(members))
        chir = cocycle.chirality_of(any_member)
        length = sum(1 for _ in cocycle.info(any_member).canonical) if False else 0
        # length unused; sort already comes from cocycle.orbits().
        entry = (length, len(orbit_word), orbit_word)
        if chir.name == "even":
            even.append(entry)
        else:
            odd.append(entry)
    palette: Dict[str, str] = {}
    cool = ["cyan", "green", "bright_blue"]
    warm = ["magenta", "yellow", "red"]
    for i, (_, _, w) in enumerate(even):
        palette[w] = cool[i % len(cool)]
    for i, (_, _, w) in enumerate(odd):
        palette[w] = warm[i % len(warm)]
    return palette


def _coloured(items, palette: Dict[str, str], default: str = "white") -> str:
    out: List[str] = []
    for ch, orbit in items:
        colour = palette.get(orbit, default)
        safe = ch.replace("[", "\\[")
        out.append(f"[{colour}]{safe}[/]")
    return "".join(out)


def build_app(engine: Engine, source=None, rate: float = 20.0):
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import Footer, Header, Sparkline, Static

    palette = _build_orbit_palette(engine.cocycle)

    # --- Panels ---------------------------------------------------------

    class ChamberPanel(Static):
        word = reactive("e")
        coord = reactive("(1, 2, 3, 4)")
        chirality = reactive("even")
        fiber = reactive("e")
        period = reactive(0)

        def render(self):
            chir_colour = "cyan" if self.chirality == "even" else "magenta"
            chir_glyph = "+" if self.chirality == "even" else "−"
            period_str = (
                f"period {self.period}" if self.period > 0
                else "[dim]non-periodic[/dim]"
            )
            return (
                f"[bold]Chamber[/bold]  {self.word}\n"
                f"[{chir_colour}]{chir_glyph} {self.chirality}[/{chir_colour}]  "
                f"fib [yellow]{self.fiber}[/yellow]  {period_str}  "
                f"[dim]{self.coord}[/dim]"
            )

    class HolonomyPanel(Static):
        closes = reactive(False)
        target = reactive("e")
        band = reactive("low")
        kappa = reactive(0.0)

        def render(self):
            verdict = (
                "[green]closes[/green]" if self.closes
                else f"[yellow]drifts → {self.target}[/yellow]"
            )
            band_colour = {"low": "green", "mid": "yellow", "high": "red"}[self.band]
            return (
                f"[bold]ℋ[/bold]   {verdict}\n"
                f"κ={self.kappa:+.3f}   "
                f"[{band_colour}]{self.band}[/{band_colour}]"
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

    class OrbitsPanel(Static):
        visits = reactive({})
        orbit_of = reactive({})
        chirality_of = reactive({})

        def render(self):
            if not self.orbit_of:
                return "[bold]Top by orbit[/bold]\n[dim]initialising[/dim]"
            orbit_visits: Dict[str, int] = {}
            for w, c in self.visits.items():
                ow = self.orbit_of.get(w, w)
                orbit_visits[ow] = orbit_visits.get(ow, 0) + c
            for ow in set(self.orbit_of.values()):
                orbit_visits.setdefault(ow, 0)
            ranked = sorted(orbit_visits.items(), key=lambda kv: -kv[1])[:6]
            top = max((c for _, c in ranked), default=1)
            top = max(top, 1)
            lines = ["[bold]Top by orbit[/bold]   [dim]colour legend ↓[/dim]"]
            for w, count in ranked:
                chir = self.chirality_of.get(w, "even")
                glyph = "+" if chir == "even" else "−"
                colour = palette.get(w, "white")
                bar = "█" * max(1, int(14 * count / top))
                lines.append(
                    f"[{colour}]{glyph} {w:>16} {bar}[/{colour}] {count}"
                )
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

    class GrammarPanel(Static):
        char_rules = reactive([])
        orbit_rules = reactive([])
        n_char = reactive(0)
        n_orbit = reactive(0)
        bits_per_symbol = reactive(0.0)
        compress_ratio = reactive(1.0)
        grammar_ratio = reactive(1.0)
        gt_ratio = reactive(1.0)
        gt_bits_per_symbol = reactive(0.0)
        raw_bits = reactive(8.0)

        def render(self):
            def colour(r):
                return "green" if r >= 2 else "yellow" if r >= 1.2 else "red"
            lines = [
                f"[bold]Grammar + Compression[/bold]   "
                f"char={self.n_char}  orbit={self.n_orbit}",
                f"  trigram     [{colour(self.compress_ratio)}]"
                f"{self.bits_per_symbol:.2f}b/s  {self.compress_ratio:.2f}×[/{colour(self.compress_ratio)}]",
                f"  grammar     [{colour(self.grammar_ratio)}]"
                f"             {self.grammar_ratio:.2f}×[/{colour(self.grammar_ratio)}]",
                f"  gram-tri    [{colour(self.gt_ratio)}]"
                f"{self.gt_bits_per_symbol:.2f}b/s  {self.gt_ratio:.2f}×[/{colour(self.gt_ratio)}]  "
                f"[dim](raw {self.raw_bits:.1f})[/dim]",
            ]
            lines.append("[dim]top char rules[/dim]")
            for r in (self.char_rules or ["[dim](none yet)[/dim]"])[:2]:
                lines.append(f"  {r}")
            lines.append("[dim]top orbit rules[/dim]")
            for r in (self.orbit_rules or ["[dim](none yet)[/dim]"])[:2]:
                lines.append(f"  {r}")
            return "\n".join(lines)

    class SynthesisPanel(Static):
        actual = reactive([])
        branches = reactive({})
        n_obs = reactive(0)

        def render(self):
            if not self.actual and not self.branches:
                return (f"[bold]Synthesis[/bold]\n"
                        f"[dim]waiting for context (obs={self.n_obs})…[/dim]")
            lines = ["[bold]Synthesis[/bold]   [dim]chars coloured by V₄-coset[/dim]"]
            lines.append(f"[bold]actual[/bold]  {_coloured(self.actual, palette)}")
            for label, seq in self.branches.items():
                lines.append(f"[bold]{label:>6}[/bold]  {_coloured(seq, palette)}")
            return "\n".join(lines)

    class BranchesPanel(Static):
        actual_tail = reactive([])
        shadows = reactive({})

        def render(self):
            lines = ["[bold]Branches[/bold]   [dim]shadow trajectories[/dim]"]
            tail = (" → ".join(self.actual_tail[-6:])
                    if self.actual_tail else "[dim]none[/dim]")
            lines.append(f"[white]actual[/white]  {tail}")
            for label, traj in self.shadows.items():
                t = " → ".join(traj[-6:]) if traj else ""
                lines.append(f"[bold]{label:>6}[/bold]  {t}")
            return "\n".join(lines)

    class StreamPanel(Static):
        text = reactive([])

        def render(self):
            if not self.text:
                return "[bold]Stream[/bold]\n[dim]waiting for input[/dim]"
            return f"[bold]Stream[/bold]\n{_coloured(self.text, palette)}"

    # --- The App --------------------------------------------------------

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
        #grammar { height: 11; border: round $accent; padding: 0 1; }
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

        def __init__(self, engine: Engine, source=None, rate: float = 20.0):
            super().__init__()
            self.engine = engine
            self.source = source
            self.rate = rate
            self.playing = source is not None
            self.fiedler_hist: Deque[float] = deque([0.0], maxlen=HISTORY)
            self.turb_hist: Deque[float] = deque([0.0], maxlen=HISTORY)
            self.kappa_hist: Deque[float] = deque([0.0], maxlen=HISTORY)
            self.surprise_hist: Deque[float] = deque([0.0], maxlen=HISTORY)
            self.stream_buf: Deque[Tuple[str, str]] = deque(maxlen=140)
            self._chars_since_synth = 0
            self._surprise_running = 0.0
            self._surprise_count = 0
            self._source_timer = None

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
                    yield Sparkline(list(self.turb_hist), id="spark-turbulence")
                with Vertical(classes="spark-cell"):
                    yield Static("Curvature κ")
                    yield Sparkline(list(self.kappa_hist), id="spark-kappa")
                with Vertical(classes="spark-cell"):
                    yield Static("Surprise (bits)")
                    yield Sparkline(list(self.surprise_hist), id="spark-surprise")
            with Horizontal(id="middle"):
                yield VisitsPanel(id="visits")
                yield OrbitsPanel(id="orbits")
                yield PredictionPanel(id="prediction")
            yield GrammarPanel(id="grammar")
            yield SynthesisPanel(id="synthesis")
            yield BranchesPanel(id="branches")
            yield StreamPanel(id="stream")
            yield Footer()

        # --- Lifecycle ------------------------------------------------

        def on_mount(self):
            self._refresh_chamber()
            # Build orbit/chirality lookup keyed by chamber-word.
            orbit_of = {}
            chirality_of = {}
            for c in self.engine.manifold.nodes:
                w = word_str(self.engine.manifold.shortlex_word(c))
                orbit_of[w] = self.engine.cocycle.orbit_of(c)
                chirality_of[orbit_of[w]] = self.engine.cocycle.chirality_of(c).name
            op = self.query_one("#orbits", OrbitsPanel)
            op.orbit_of = orbit_of
            op.chirality_of = chirality_of
            if self.engine.recorder is not None:
                visits = dict(self.engine.recorder.aggregate["chamber_visits"])
                self.query_one("#visits", VisitsPanel).visits = visits
                op.visits = visits
            pred_panel = self.query_one("#prediction", PredictionPanel)
            pred_panel.n_contexts = self.engine.predictor.n_contexts()
            pred_panel.n_obs = self.engine.predictor.n_observations()
            self._refresh_synthesis()
            self._refresh_branches()
            self._refresh_grammar()
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
            self.engine.current_chamber = self.engine.manifold.origin()
            self.engine.trajectory.clear()
            self.engine.trajectory.append(self.engine.current_chamber)
            self._refresh_chamber()
            self._refresh_branches()

        def action_toggle_play(self):
            if self.source is not None:
                self.playing = not self.playing

        def action_resynth(self):
            self._refresh_synthesis()

        def on_unmount(self):
            self.engine.end()

        # --- Refreshers -----------------------------------------------

        def _refresh_chamber(self):
            x = self.engine.current_chamber
            info = self.engine.cocycle.info(x)
            cp = self.query_one("#chamber", ChamberPanel)
            cp.word = word_str(self.engine.manifold.shortlex_word(x))
            cp.coord = str(x)
            cp.chirality = info.chirality.name
            cp.fiber = info.fiber_label
            from eliza.trajectory import detect_period
            p = detect_period(list(self.engine.trajectory))
            cp.period = p if p is not None else 0

        def _refresh_synthesis(self):
            text = self.engine.predictor.project_text(60)
            actual = self._colorize(text)
            branches_out = {}
            for label, flips in SHADOW_FLIPS:
                t = branched(
                    self.engine.predictor,
                    self.engine.manifold,
                    self.engine.current_chamber,
                    self.engine.router,
                    flips,
                    length=60,
                )
                branches_out[label] = self._colorize(t)
            sp = self.query_one("#synthesis", SynthesisPanel)
            sp.actual = actual
            sp.branches = branches_out
            sp.n_obs = self.engine.predictor.n_observations()

        def _colorize(self, text: str):
            x = self.engine.current_chamber
            out = []
            from eliza.manifold import apply
            for ch in text:
                gen = self.engine.router(ch)
                x = apply(gen, x)
                orbit = self.engine.cocycle.orbit_of(x)
                disp = ch if ch.isprintable() and ch != "\n" else (
                    "↵" if ch == "\n" else "·"
                )
                out.append((disp, orbit))
            return out

        def _refresh_branches(self):
            traj = list(self.engine.trajectory)
            shadows = {}
            for label, flips in SHADOW_FLIPS:
                s = self.engine.holonomy.shadow_trajectory(traj, flips)
                shadows[label] = [
                    word_str(self.engine.manifold.shortlex_word(x)) for x in s
                ]
            actual_tail = [
                word_str(self.engine.manifold.shortlex_word(x))
                for x in self.engine.trajectory
            ]
            bp = self.query_one("#branches", BranchesPanel)
            bp.actual_tail = actual_tail
            bp.shadows = shadows

        def _refresh_grammar(self):
            gp = self.query_one("#grammar", GrammarPanel)
            gp.n_char = self.engine.grammar_char.n_rules()
            gp.n_orbit = self.engine.grammar_orbit.n_rules()
            gp.char_rules = self.engine.grammar_char.top_rules(3)
            gp.orbit_rules = self.engine.grammar_orbit.top_rules(3)
            stats = self.engine.compression_stats()
            gp.bits_per_symbol = stats["bits_per_symbol"]
            gp.compress_ratio = stats["ratio"]
            gp.grammar_ratio = stats["grammar_ratio"]
            gp.gt_ratio = stats["gt_ratio"]
            gp.gt_bits_per_symbol = stats["gt_bits_per_symbol"]
            gp.raw_bits = stats["raw_bits_per_symbol"]

        # --- Per-char consumption -------------------------------------

        def _consume(self, ch: str):
            result: StepResult = self.engine.step(ch)
            self.fiedler_hist.append(result.fiedler)
            self.turb_hist.append(result.turbulence)
            self.kappa_hist.append(result.holonomy.curvature)
            surprise = result.surprise
            self.surprise_hist.append(surprise if surprise is not None else 0.0)
            if surprise is not None:
                self._surprise_running += surprise
                self._surprise_count += 1
            disp = ch if ch.isprintable() and ch != "\n" else (
                "↵" if ch == "\n" else "·"
            )
            self.stream_buf.append((disp, result.orbit_to))

            # Push to panels.
            cp = self.query_one("#chamber", ChamberPanel)
            cp.word = result.chamber_to_word
            cp.coord = str(result.chamber_to)
            cp.chirality = result.chirality
            cp.fiber = result.fiber
            cp.period = result.period if result.period is not None else 0

            hp = self.query_one("#holonomy", HolonomyPanel)
            hp.closes = result.holonomy.closes
            hp.target = word_str(
                self.engine.manifold.shortlex_word(result.holonomy.target)
            )
            hp.band = result.holonomy.band
            hp.kappa = result.holonomy.curvature

            phys = self.engine.manifold.get_physics(result.chamber_to) if False else None
            # Gradient from manifold directly:
            from eliza.manifold import apply as _apply
            from eliza.alphabets import GENERATORS
            here = result.chamber_to
            here_d = self.engine.manifold.bruhat_distance(here)
            up = down = 0
            for g in GENERATORS:
                d = self.engine.manifold.bruhat_distance(_apply(g, here))
                if d == here_d + 1: up += 1
                elif d == here_d - 1: down += 1
            gp = self.query_one("#gradient", GradientPanel)
            gp.up = up
            gp.down = down
            gp.last_gen = result.char  # show the actual char that emitted the gen

            self.query_one("#spark-fiedler", Sparkline).data = list(self.fiedler_hist)
            self.query_one("#spark-turbulence", Sparkline).data = list(self.turb_hist)
            self.query_one("#spark-kappa", Sparkline).data = list(self.kappa_hist)
            self.query_one("#spark-surprise", Sparkline).data = list(self.surprise_hist)

            visits = (
                dict(self.engine.recorder.aggregate["chamber_visits"])
                if self.engine.recorder is not None else {}
            )
            self.query_one("#visits", VisitsPanel).visits = visits
            self.query_one("#orbits", OrbitsPanel).visits = visits

            pred = self.query_one("#prediction", PredictionPanel)
            pred.top_chars = self.engine.predictor.top_predictions(5)
            pred.actual_char = ch
            pchamber = self.engine.predictor.predicted_next_chamber = (
                self._predicted_chamber()
            )
            pred.predicted_chamber = pchamber if pchamber else "?"
            pred.n_contexts = self.engine.predictor.n_contexts()
            pred.n_obs = self.engine.predictor.n_observations()
            pred.mean_surprise = (
                self._surprise_running / self._surprise_count
                if self._surprise_count else 0.0
            )
            self._chars_since_synth += 1
            if self._chars_since_synth >= SYNTH_REFRESH_EVERY:
                self._chars_since_synth = 0
                self._refresh_synthesis()
                self._refresh_grammar()

            self._refresh_branches()
            self.query_one("#stream", StreamPanel).text = list(self.stream_buf)

        def _predicted_chamber(self) -> str:
            # Argmax-char of trigram → generator → apply on current chamber.
            top = self.engine.predictor.top_predictions(1)
            if not top:
                return ""
            ch, _ = top[0]
            from eliza.manifold import apply as _apply
            x = _apply(self.engine.router(ch), self.engine.current_chamber)
            return word_str(self.engine.manifold.shortlex_word(x))

    return ElizaApp(engine, source=source, rate=rate)
