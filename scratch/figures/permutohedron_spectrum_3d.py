#!/usr/bin/env python3
"""The S₄ permutohedron harmonics as a 3D amplitude surface.

The 2D spectrum figure shows the low eigenvectors φ₀…φ₇ as a heatmap over the
24 chambers. Here amplitude becomes height (LiftMap: cartesian over the
eigenvector field): a surface of standing waves, chambers ordered by Coxeter
length on one axis and harmonic index on the other. Shares the Permutohedron
core (_perm).
"""

from _perm import Permutohedron
from _gallery import finish, make_parser, set_style
from _lift3d import shade_surface, style_3d, floor_plane

parser = make_parser("permutohedron_spectrum_3d")
parser.add_argument("--modes", type=int, default=8, help="How many harmonics.")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

P = Permutohedron()
order = sorted(P.nodes_list, key=lambda p: (P.dist[p], p))
rows = [P.index(p) for p in order]
M = P.eigenvectors[np.ix_(rows, np.arange(args.modes))].T  # modes × chambers

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")
# Height = |amplitude| (so the floor is flush at 0); colour = signed phase, so
# crests and troughs are still distinguished (red vs blue) — a rectified
# standing wave with the node structure as valleys touching 0.
absM = np.abs(M)
shade_surface(ax, absM, cmap="coolwarm", color_by=M, diverging=True,
              azdeg=315, altdeg=50, vert_exag=4.0)

ax.set_xlabel("chamber (by Coxeter length)")
ax.set_ylabel("harmonic  φ_k")
ax.set_zlabel("|amplitude|")
ax.set_yticks(range(args.modes))
ax.set_yticklabels([f"φ{chr(0x2080 + k)}" for k in range(args.modes)], fontsize=8)
ax.set_box_aspect((1.6, 1, 0.5))
ax.view_init(elev=34, azim=-60)
ax.set_zlim(0, absM.max() + 0.02)
floor_plane(ax, z=0.0, alpha=0.22)
style_3d(ax)
ax.set_title("S₄ permutohedron harmonics as standing waves\n"
             "height = |amplitude| (floor at 0) · colour = sign over the 24 chambers",
             pad=4)

finish(fig, "permutohedron_spectrum_3d", args)
