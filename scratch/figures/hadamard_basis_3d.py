#!/usr/bin/env python3
"""The Walsh–Hadamard basis as a self-similar terraced landscape.

The flat ±1 matrix is boring in z, but the recursion *grade* gives the height.
Take the partial Walsh sum weighted by bit significance:

    h(k, x) = Σ_{i=0}^{n-1} 2^(−i) · (−1)^(kᵢ xᵢ)

The high-order bit (i=0) carves the tallest terraces; each finer bit adds a
half-height step — so the Sylvester recursion literally becomes stepped
"steppe shifting", a self-similar ziggurat over F₂ⁿ × F₂ⁿ. (gauge: the 2^(−i)
weighting is a chosen significance; the bit structure is not.) Character math
from scratch/hadamard_basis.py.
"""

from _gallery import finish, make_parser, set_style
from _lift3d import shade_surface, style_3d, floor_plane

parser = make_parser("hadamard_basis_3d")
parser.add_argument("--n", type=int, default=5, help="WHT level (grid is 2ⁿ×2ⁿ).")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np


def terraced_walsh(n):
    N = 2 ** n
    H = np.zeros((N, N))
    for k in range(N):
        for x in range(N):
            h = 0.0
            for i in range(n):
                ki = (k >> (n - 1 - i)) & 1
                xi = (x >> (n - 1 - i)) & 1
                h += (2.0 ** (-i)) * (-1 if (ki & xi) else 1)
            H[k, x] = h
    return H


H = terraced_walsh(args.n)
N = 2 ** args.n

fig = plt.figure(figsize=(11, 9))
ax = fig.add_subplot(111, projection="3d")
shade_surface(ax, H, cmap="twilight_shifted", azdeg=315, altdeg=55, vert_exag=2.0)

ax.set_xlabel("x  (point of F₂ⁿ)")
ax.set_ylabel("k  (character index)")
ax.set_zlabel("partial Walsh sum")
ax.set_box_aspect((1, 1, 0.5))
ax.view_init(elev=46, azim=-55)
ax.invert_yaxis()  # bring the low-z terrace toward the foreground
floor_plane(ax, z=0.0, alpha=0.18)
style_3d(ax)
ax.set_title(f"Walsh–Hadamard terraces at level n = {args.n}  ({N}×{N})\n"
             "height = Σᵢ 2⁻ⁱ·(−1)^(kᵢxᵢ)  — recursion grade → steppe shifting",
             pad=4)

finish(fig, "hadamard_basis_3d", args)
