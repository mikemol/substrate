"""Shared plumbing for the substrate figure gallery.

Every figure script imports this module, calls `set_style()`, builds a
matplotlib Figure, and hands it to `finish(fig, name, args)`.

By default figures render headless (Agg backend) and save both a PNG and an
SVG under `scratch/figures/out/`. Pass `--interactive` to instead pop a live
window. The backend decision has to happen before `pyplot` is imported, so
`make_parser` parses argv eagerly and selects the backend as a side effect;
import this module *before* importing `matplotlib.pyplot` in a figure script.

Typical figure skeleton:

    from _gallery import make_parser, set_style, finish
    args = make_parser("fano_plane").parse_args()
    set_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 8))
    ...
    finish(fig, "fano_plane", args)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

# Directory layout: this file lives in scratch/figures/; outputs go to
# scratch/figures/out/ unless --out overrides.
FIGURES_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = FIGURES_DIR / "out"
REPO_ROOT = FIGURES_DIR.parent.parent  # scratch/figures -> scratch -> repo

# A shared qualitative palette for generators / clusters / packages. Picked for
# legibility on a light background and colour-blind friendliness (Okabe-Ito).
PALETTE = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#D55E00",  # vermilion
    "#CC79A7",  # purple
    "#56B4E9",  # sky
    "#F0E442",  # yellow
    "#999999",  # grey
]

# Diverging colours for invariant vs gauge, +1 vs -1, etc.
INVARIANT_COLOR = "#0072B2"
GAUGE_COLOR = "#D55E00"


def make_parser(name: str) -> argparse.ArgumentParser:
    """Build the standard figure parser and select the matplotlib backend.

    Selecting the backend is a side effect of parsing: when `--interactive` is
    absent we force Agg so the script runs headless. We peek at argv here
    (before pyplot import) rather than after parse_args so the import order in
    figure scripts stays simple.
    """
    interactive = "--interactive" in sys.argv
    if not interactive:
        matplotlib.use("Agg")
    # else: leave the default interactive backend in place.

    p = argparse.ArgumentParser(prog=f"{name}.py", description=f"Render the {name} figure.")
    p.add_argument("--interactive", action="store_true",
                   help="Pop a live window instead of saving files.")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help=f"Output directory (default {DEFAULT_OUT}).")
    p.add_argument("--dpi", type=int, default=200, help="PNG resolution (default 200).")
    p.add_argument("--no-svg", action="store_true", help="Skip the SVG export.")
    return p


def set_style() -> None:
    """Apply one consistent theme across the gallery."""
    matplotlib.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.8,
        "figure.autolayout": False,
    })


def finish(fig, name: str, args) -> list[Path]:
    """Either show the figure interactively or save PNG (+ SVG)."""
    import matplotlib.pyplot as plt

    if args.interactive:
        plt.show()
        plt.close(fig)
        return []

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    png = out_dir / f"{name}.png"
    fig.savefig(png, dpi=args.dpi, bbox_inches="tight")
    written.append(png)

    if not args.no_svg:
        svg = out_dir / f"{name}.svg"
        fig.savefig(svg, bbox_inches="tight")
        written.append(svg)

    plt.close(fig)
    for path in written:
        size = path.stat().st_size
        print(f"  wrote {path}  ({size:,} bytes)")
    return written
