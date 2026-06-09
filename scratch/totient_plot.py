"""Remainder plot tied to Euler's totient.

Pick a modulus m. The plot scatters (k, k mod m) for k = 1..N.
All remainders sit strictly below the horizontal line y = m.
Points coloured by gcd(k, m): coprime points (gcd = 1) are the ones
counted by φ(m). The legend reports φ(m) and the prime factorisation
of m.

By default this renders a static figure and saves it into the gallery
(scratch/figures/out/). Pass --interactive for the live slider UI:

    N max         slider — how many k's to plot
    Modulus m     slider — horizontal modulus line
    Only coprime  checkbox — hide non-coprime remainders
"""

from __future__ import annotations

import sys
from pathlib import Path

# The gallery plumbing lives alongside the other figures.
sys.path.insert(0, str(Path(__file__).resolve().parent / "figures"))
from _gallery import make_parser, set_style, finish  # noqa: E402

parser = make_parser("totient")
parser.add_argument("--m", type=int, default=12, help="Modulus m (static mode).")
parser.add_argument("--N", type=int, default=200, help="Max k (static mode).")
args = parser.parse_args()
set_style()

import numpy as np
import matplotlib

if args.interactive:
    for _backend in ("QtAgg", "TkAgg", "GTK3Agg"):
        try:
            matplotlib.use(_backend)
            break
        except (ImportError, ValueError):
            continue

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons


def totient_sieve(limit: int) -> np.ndarray:
    phi = np.arange(limit + 1, dtype=np.int64)
    for p in range(2, limit + 1):
        if phi[p] == p:
            phi[p::p] -= phi[p::p] // p
    return phi


def prime_factorisation(n: int) -> list[tuple[int, int]]:
    factors: list[tuple[int, int]] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            k = 0
            while n % d == 0:
                n //= d
                k += 1
            factors.append((d, k))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors


def factor_string(n: int) -> str:
    if n < 2:
        return str(n)
    parts = [f"{p}" if k == 1 else f"{p}^{k}" for p, k in prime_factorisation(n)]
    return " · ".join(parts)


INITIAL_LIMIT = args.N
INITIAL_M = args.m
HARD_LIMIT = 5000

phi = totient_sieve(HARD_LIMIT)

fig, ax = plt.subplots(figsize=(11, 6.5))
plt.subplots_adjust(left=0.08, right=0.78, bottom=0.22, top=0.92)
ax.set_xlabel("k")
ax.set_ylabel("k mod m")
ax.grid(alpha=0.3)

state = {
    "limit": INITIAL_LIMIT,
    "m": INITIAL_M,
    "only_coprime": False,
    "log_x": False,
}


def redraw():
    ax.clear()
    ax.grid(alpha=0.3)
    ax.set_xlabel("k")
    ax.set_ylabel("k mod m")

    lim = state["limit"]
    m = state["m"]

    ks = np.arange(1, lim + 1)
    rems = ks % m
    gcds = np.gcd(ks, m)
    coprime = gcds == 1

    if not state["only_coprime"]:
        ax.scatter(
            ks[~coprime],
            rems[~coprime],
            s=8,
            color="#888888",
            alpha=0.55,
            label="gcd(k, m) > 1",
        )
    ax.scatter(
        ks[coprime],
        rems[coprime],
        s=14,
        color="#1f77b4",
        label="gcd(k, m) = 1 (counted by φ)",
    )

    ax.axhline(
        m,
        color="#d62728",
        lw=1.2,
        ls="--",
        label=f"modulus m = {m}",
    )
    ax.set_ylim(-1, max(m * 1.08, m + 1))
    if state["log_x"]:
        ax.set_xscale("log")
        ax.set_xlim(max(0.9, 1), lim * 1.05)
    else:
        ax.set_xscale("linear")

    title = (
        f"k mod m for k = 1..{lim}, m = {m} = {factor_string(m)}    "
        f"φ({m}) = {phi[m]}"
    )
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    fig.canvas.draw_idle()


redraw()

if not args.interactive:
    # Static gallery render.
    finish(fig, "totient", args)
else:
    ax_limit = plt.axes([0.08, 0.10, 0.62, 0.03])
    ax_m = plt.axes([0.08, 0.05, 0.62, 0.03])
    s_limit = Slider(ax_limit, "N max", 10, HARD_LIMIT, valinit=INITIAL_LIMIT, valstep=1)
    s_m = Slider(ax_m, "Modulus m", 2, 200, valinit=INITIAL_M, valstep=1)

    def on_limit(val):
        state["limit"] = int(val)
        redraw()

    def on_m(val):
        state["m"] = int(val)
        redraw()

    s_limit.on_changed(on_limit)
    s_m.on_changed(on_m)

    ax_check = plt.axes([0.81, 0.50, 0.16, 0.13])
    c_opts = CheckButtons(ax_check, ["only coprime", "log x"], [False, False])

    def on_check(label):
        if label == "only coprime":
            state["only_coprime"] = not state["only_coprime"]
        elif label == "log x":
            state["log_x"] = not state["log_x"]
        redraw()

    c_opts.on_clicked(on_check)
    plt.show()
