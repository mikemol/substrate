#!/usr/bin/env python3
"""The octonion Cayley table as a signed 3D relief.

The 2D table colours each cell by the sign of the product (red +, blue −). Here
that sign becomes height: the LiftMap is a signed bar field (_lift3d.signed_bars)
over the 8×8 grid. Two gauge choices for what the bar height encodes —

    --z-mode sign   : height = ±1  (exactly the red/blue you saw, lifted)
    --z-mode index  : height = the product index e_k, signed

— picked-and-labelled per the discipline. Table from _fano.octonion_table.
"""

from _gallery import finish, make_parser, set_style
from _fano import octonion_table
from _lift3d import signed_bars, style_3d, floor_plane

parser = make_parser("octonion_fano_3d")
parser.add_argument("--z-mode", choices=["index", "sign"], default="index",
                    help="Bar height = product index e_k (default) or a flat ±1 field.")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

sign, idx = octonion_table()
# Height carries magnitude, colour carries sign — so the floor is flush at 0.
if args.z_mode == "index":
    heights = idx.astype(float)          # which unit e_k the product lands on
    zlabel = "height = product index e_k"
else:
    heights = np.ones_like(idx, dtype=float)
    zlabel = "height = 1 (flat field)"

fig = plt.figure(figsize=(11, 9))
ax = fig.add_subplot(111, projection="3d")
signed_bars(ax, heights, sign)

labels = ["1"] + [f"e{chr(0x2080 + i)}" for i in range(1, 8)]
ax.set_xticks(np.arange(8) + 0.4); ax.set_xticklabels(labels, fontsize=8)
ax.set_yticks(np.arange(8) + 0.4); ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("right factor"); ax.set_ylabel("left factor")
ax.set_zlabel(zlabel)
ax.set_zlim(0, heights.max() + 0.3)
floor_plane(ax, z=0.0, alpha=0.18)
ax.view_init(elev=30, azim=-50)
style_3d(ax)
ax.set_title("Octonion Cayley table as a relief — floor flush at 0\n"
             f"gauge: {zlabel}; colour = sign (red +, blue −)", pad=4)

finish(fig, "octonion_fano_3d", args)
