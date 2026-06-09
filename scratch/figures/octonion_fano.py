#!/usr/bin/env python3
"""Octonion multiplication — the Fano-plane mnemonic and the Cayley table.

The seven imaginary units e₁…e₇ sit on the Fano plane; each of the 7 lines is
an oriented triple (a,b,c) with eₐe_b = e_c cyclically (and the reverse gives
the negative). This is the 3+1 = octonion level of the Cayley–Dickson ladder
formalised in
    agda/Substrate/Category/MultiscaleOctonionLoop.agda
(Rotation = F₂ⁿ × F₂; XOR-composition on the n axes and the chirality bit).

Left  : the oriented Fano mnemonic (each triple a coloured directed 3-cycle).
Right : the 8×8 multiplication table, cells coloured by sign of the product.
"""

import math

from _gallery import PALETTE, finish, make_parser, set_style
from _fano import OCTONION_TRIPLES as TRIPLES, octonion_table

args = make_parser("octonion_fano").parse_args()
set_style()

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

# Geometric placement so each octonion triple is a Fano line. Worked out so the
# three e₁-triples are the medians (e₁ at the centre), the all-midpoint triple
# (3,6,5) is the circle, and (2,4,6)/(2,5,7)/(3,4,7) are the triangle sides.
R = 1.0
C1 = (0.0, R)
C2 = (-R * math.sin(math.radians(60)), -R / 2)
C3 = (R * math.sin(math.radians(60)), -R / 2)
M12 = ((C1[0] + C2[0]) / 2, (C1[1] + C2[1]) / 2)
M13 = ((C1[0] + C3[0]) / 2, (C1[1] + C3[1]) / 2)
M23 = ((C2[0] + C3[0]) / 2, (C2[1] + C3[1]) / 2)
O = (0.0, 0.0)
POS = {1: O, 2: C1, 4: C2, 7: C3, 6: M12, 5: M13, 3: M23}


def panel_mnemonic(ax):
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-0.95, 1.25)
    # The seven lines: six straight (faint), plus the inscribed circle.
    straight = [t for t in TRIPLES if t != (3, 6, 5)]
    for (a, b, c) in straight:
        pts = sorted([POS[a], POS[b], POS[c]])
        ax.plot([pts[0][0], pts[-1][0]], [pts[0][1], pts[-1][1]],
                color="#dddddd", lw=1.2, zorder=1)
    ax.add_patch(Circle(O, math.dist(M12, O), fill=False, lw=1.2,
                        edgecolor="#dddddd", zorder=1))
    # Each triple as a coloured directed 3-cycle a→b→c→a.
    for i, (a, b, c) in enumerate(TRIPLES):
        col = PALETTE[i % len(PALETTE)]
        for u, v in ((a, b), (b, c), (c, a)):
            ax.add_patch(FancyArrowPatch(
                POS[u], POS[v], connectionstyle="arc3,rad=0.18",
                arrowstyle="-|>", mutation_scale=13, lw=1.7, color=col,
                zorder=3, shrinkA=13, shrinkB=13, alpha=0.85))
    for u, (x, y) in POS.items():
        ax.scatter([x], [y], s=520, color="white", edgecolors="#222222",
                   linewidths=1.6, zorder=5)
        ax.text(x, y, f"e{chr(0x2080 + u)}", ha="center", va="center",
                fontsize=12, fontweight="bold", zorder=6)
    ax.set_title("Fano mnemonic\neₐe_b = e_c along each oriented line")


def panel_table(ax):
    sign, idx = octonion_table()
    ax.imshow(sign, cmap="coolwarm", vmin=-1, vmax=1, alpha=0.85)
    labels = ["1"] + [f"e{chr(0x2080 + i)}" for i in range(1, 8)]
    for r in range(8):
        for c in range(8):
            s = "−" if sign[r][c] < 0 else ""
            ax.text(c, r, f"{s}{labels[idx[r][c]]}", ha="center", va="center",
                    fontsize=10, fontweight="bold",
                    color=("white" if abs(sign[r][c]) and idx[r][c] != 0 else "#222222"))
    ax.set_xticks(range(8)); ax.set_yticks(range(8))
    ax.set_xticklabels(labels); ax.set_yticklabels(labels)
    ax.set_xlabel("right factor"); ax.set_ylabel("left factor")
    for k in range(9):
        ax.axhline(k - 0.5, color="white", lw=1.2)
        ax.axvline(k - 0.5, color="white", lw=1.2)
    ax.set_title("Cayley table  (red = +,  blue = −)")


fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 7.4),
                               gridspec_kw={"width_ratios": [1, 1.1]})
panel_mnemonic(axL)
panel_table(axR)
fig.suptitle("Octonions — Cayley–Dickson 3+1 level "
             "(agda/Substrate/Category/MultiscaleOctonionLoop.agda)",
             fontsize=12, y=1.0)

finish(fig, "octonion_fano", args)
