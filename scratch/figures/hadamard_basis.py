#!/usr/bin/env python3
"""The Walsh–Hadamard character basis as a self-similar ±1 fractal.

The witness axis of the unified codeword indexes a WHT character of F₂ⁿ
(scratch/hadamard_basis.py, M39):  χ_k(x) = (−1)^{k·x},  k·x = ⊕ᵢ kᵢxᵢ. The
2ⁿ × 2ⁿ matrix H[k][x] = χ_k(x) is the Sylvester–Hadamard matrix, with the
recursive block structure Hₙ = [[Hₙ₋₁, Hₙ₋₁], [Hₙ₋₁, −Hₙ₋₁]] — a self-similar
checkerboard.

Left  : the full Hₙ heatmap (default n = 5 → 32×32).
Right : the H₁ ⊂ H₂ ⊂ H₃ nesting that generates it.
"""

from _gallery import finish, make_parser, set_style

parser = make_parser("hadamard_basis")
parser.add_argument("--n", type=int, default=5, help="WHT level (matrix is 2ⁿ×2ⁿ).")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
import numpy as np


def wht_matrix(n):
    """Hₙ[k][x] = χ_k(x) = (−1)^{popcount(k & x)} — the M39 construction."""
    N = 2 ** n
    H = np.empty((N, N), dtype=int)
    for k in range(N):
        for x in range(N):
            H[k, x] = -1 if bin(k & x).count("1") & 1 else 1
    return H


fig = plt.figure(figsize=(15, 7.6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1])
ax_big = fig.add_subplot(gs[0])
ax_nest = fig.add_subplot(gs[1])

# --- Left: the full matrix. ---
H = wht_matrix(args.n)
N = 2 ** args.n
ax_big.imshow(H, cmap="binary", vmin=-1, vmax=1, interpolation="nearest")
ax_big.set_title(f"H{chr(0x2080 + args.n)}  =  χ_k(x) = (−1)^(k·x)   "
                 f"({N}×{N},  F₂{['','¹','²','³','⁴','⁵','⁶'][args.n]})")
ax_big.set_xlabel("x  (point of F₂ⁿ)")
ax_big.set_ylabel("k  (character index)")
# Light grid at the top recursive split.
for d in range(1, args.n):
    step = N // (2 ** d)
    for t in range(step, N, step):
        ax_big.axhline(t - 0.5, color="#cc0000", lw=0.4, alpha=0.25)
        ax_big.axvline(t - 0.5, color="#cc0000", lw=0.4, alpha=0.25)

# --- Right: the H₁⊂H₂⊂H₃ Sylvester nesting. ---
ax_nest.set_xlim(0, 8); ax_nest.set_ylim(0, 8); ax_nest.set_aspect("equal")
ax_nest.invert_yaxis(); ax_nest.axis("off")
for lvl, (col, lw) in zip((3, 2, 1), (("#999999", 1.0), ("#0072B2", 1.6), ("#D55E00", 2.4))):
    H3 = wht_matrix(3)
    # show H3 once as the backdrop
    if lvl == 3:
        ax_nest.imshow(H3, cmap="binary", vmin=-1, vmax=1, extent=(0, 8, 8, 0),
                       interpolation="nearest")
    size = 2 ** lvl
    import matplotlib.patches as mp
    ax_nest.add_patch(mp.Rectangle((0, 0), size, size, fill=False,
                                   edgecolor=col, lw=lw))
    ax_nest.text(size - 0.1, 0.1, f"H{chr(0x2080 + lvl)}", color=col,
                 ha="right", va="top", fontsize=13, fontweight="bold")
ax_nest.set_title("Sylvester recursion\nHₙ = [[Hₙ₋₁, Hₙ₋₁], [Hₙ₋₁, −Hₙ₋₁]]")

fig.suptitle("Walsh–Hadamard character basis  (scratch/hadamard_basis.py, M39)",
             fontsize=13, y=1.0)

finish(fig, "hadamard_basis", args)
