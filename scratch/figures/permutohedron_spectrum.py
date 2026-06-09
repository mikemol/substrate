#!/usr/bin/env python3
"""Laplacian spectrum of the S₄ permutohedron Cayley graph.

Companion to permutohedron_s4.py, sharing the same `Permutohedron` core
(_perm.py). Left: the eigenvalue spectrum λ₀ ≤ … ≤ λ₂₃ as a bar chart, with the
spectral gap (Fiedler value λ₁) marked. Right: a heatmap of the low harmonics
φ₀…φ₇ over the 24 chambers, ordered by Coxeter (Bruhat) length from the
identity — the standing waves of the manifold.
"""

from _perm import Permutohedron
from _gallery import finish, make_parser, set_style

args = make_parser("permutohedron_spectrum").parse_args()
set_style()

import matplotlib.pyplot as plt
import numpy as np

P = Permutohedron()

fig, (ax_spec, ax_heat) = plt.subplots(
    1, 2, figsize=(15, 7), gridspec_kw={"width_ratios": [1, 1.25]})

# --- Left: eigenvalue spectrum. ---
ev = P.eigenvalues
idx = np.arange(len(ev))
bars = ax_spec.bar(idx, ev, color="#56B4E9", edgecolor="#222222", linewidth=0.6)
bars[1].set_color("#D55E00")  # Fiedler value λ₁
ax_spec.axhline(ev[1], color="#D55E00", ls="--", lw=1.0, alpha=0.7)
ax_spec.text(len(ev) - 0.5, ev[1], f"  λ₁ = {ev[1]:.3f}\n  (spectral gap)",
             va="bottom", ha="right", color="#D55E00", fontsize=10)
ax_spec.set_xlabel("eigenvalue index  k")
ax_spec.set_ylabel("λ_k")
ax_spec.set_title("Graph Laplacian spectrum")
ax_spec.set_xticks(idx[::2])

# --- Right: low harmonics over chambers, ordered by Bruhat length. ---
order = sorted(P.nodes_list, key=lambda p: (P.dist[p], p))
row_idx = [P.index(p) for p in order]
n_modes = 8
M = P.eigenvectors[np.ix_(row_idx, np.arange(n_modes))].T  # modes × chambers

im = ax_heat.imshow(M, aspect="auto", cmap="coolwarm",
                    vmin=-np.abs(M).max(), vmax=np.abs(M).max())
ax_heat.set_yticks(range(n_modes))
ax_heat.set_yticklabels([f"φ{chr(0x2080 + k)}  (λ={ev[k]:.2f})" for k in range(n_modes)])
ax_heat.set_xticks(range(len(order)))
ax_heat.set_xticklabels(["".join(map(str, p)) for p in order],
                        rotation=90, fontsize=6.5)
ax_heat.set_xlabel("chamber (permutation), ordered by Coxeter length")
ax_heat.set_title("Low harmonics  φ₀…φ₇  over the 24 chambers")
# Mark Bruhat-length block boundaries.
lengths = [P.dist[p] for p in order]
for k in range(1, len(order)):
    if lengths[k] != lengths[k - 1]:
        ax_heat.axvline(k - 0.5, color="#222222", lw=0.6, alpha=0.4)
fig.colorbar(im, ax=ax_heat, shrink=0.7, pad=0.02, label="amplitude")

fig.suptitle("S₄ permutohedron — Laplacian spectrum & harmonics", fontsize=15,
             fontweight="bold", y=1.0)

finish(fig, "permutohedron_spectrum", args)
