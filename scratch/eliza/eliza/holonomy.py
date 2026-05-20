"""Eliza.Holonomy — BC-cell + shadow trajectories.

Implements the G→C→S→G round-trip from readme-4.md as a Beck-Chevalley
square. For each chamber x:

  * φ(x)        = (fiedler, turbulence) coordinate.
  * centroid(x) = mean over neighbours of φ.
  * κ(x)        = |φ(x) - centroid(x)|.
  * ℋ(x)        = nearest chamber y to centroid(x).
  * closes(x)   = (ℋ(x) == x).

The shadow trajectory under sign-flip s ∈ {-1,+1}² for an existing
chamber trajectory is computed by lifting to spectral space, taking
derivatives, sign-flipping per axis, integrating, and reprojecting each
point to its nearest chamber.

Per the Agda contract this is the SOLE access point to spectral
non-commutativity content; Holonomy doesn't compute itself anywhere
else.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from eliza.alphabets import Chamber, Gen, GENERATORS
from eliza.manifold import Manifold, apply


@dataclass(frozen=True)
class HolonomyReading:
    closes: bool
    target: Chamber
    curvature: float
    band: str  # "low" | "mid" | "high"


class Holonomy:
    """Per-chamber BC-cell readings on the 2D macro embedding."""

    def __init__(self, manifold: Manifold) -> None:
        self._manifold = manifold
        n = manifold.num_chambers
        # Build the per-chamber spectral coordinate matrix.
        self._phi = np.empty((n, 2), dtype=float)
        for i, x in enumerate(manifold.nodes):
            self._phi[i] = manifold.macro_coord(x)
        # Centroids.
        self._centroid = np.empty_like(self._phi)
        for i, x in enumerate(manifold.nodes):
            nbrs = manifold.neighbours(x)
            self._centroid[i] = np.mean(
                [manifold.macro_coord(y) for y in nbrs], axis=0
            )
        # Shadow chamber: arg min over y of ||phi[y] - centroid[x]||.
        diffs = self._phi[:, None, :] - self._centroid[None, :, :]
        sq = (diffs ** 2).sum(axis=2)
        self._shadow_idx = sq.argmin(axis=0)
        # Curvature per chamber.
        self._kappa = np.linalg.norm(self._phi - self._centroid, axis=1)
        # Bands by terciles of the observed κ distribution.
        sorted_k = np.sort(self._kappa)
        self._low_thresh = float(sorted_k[n // 3])
        self._high_thresh = float(sorted_k[2 * n // 3])

    def _band(self, kappa: float) -> str:
        if kappa < self._low_thresh:
            return "low"
        if kappa < self._high_thresh:
            return "mid"
        return "high"

    def at(self, x: Chamber) -> HolonomyReading:
        i = self._manifold.node_index(x)
        target_idx = int(self._shadow_idx[i])
        target = self._manifold.nodes[target_idx]
        kappa = float(self._kappa[i])
        return HolonomyReading(
            closes=target == x,
            target=target,
            curvature=kappa,
            band=self._band(kappa),
        )

    # --- Shadow trajectories under axis-flip ------------------------------

    def shadow_trajectory(
        self,
        trajectory: Sequence[Chamber],
        sign_flips: Tuple[int, int],
    ) -> List[Chamber]:
        """Lift to 2D spectral coords, differentiate, sign-flip per axis,
        reintegrate from y[0], reproject each point to nearest chamber."""
        if len(trajectory) < 2:
            return list(trajectory)
        idxs = [self._manifold.node_index(x) for x in trajectory]
        y = self._phi[idxs]
        d = np.diff(y, axis=0)
        signs = np.array(sign_flips, dtype=float)
        d_flipped = d * signs
        y_hat = np.empty_like(y)
        y_hat[0] = y[0]
        y_hat[1:] = y[0] + np.cumsum(d_flipped, axis=0)
        result: List[Chamber] = []
        for point in y_hat:
            dists = np.linalg.norm(self._phi - point, axis=1)
            result.append(self._manifold.nodes[int(np.argmin(dists))])
        return result


# Standard three non-identity sign-flip pairs.
SHADOW_FLIPS: Tuple[Tuple[str, Tuple[int, int]], ...] = (
    ("Φ̄",   (-1, +1)),
    ("T̄",   (+1, -1)),
    ("Φ̄T̄", (-1, -1)),
)


def spectral_deltas(
    manifold: Manifold, chamber: Chamber
) -> Dict[Gen, np.ndarray]:
    """Per-generator spectral delta at `chamber`. Used by Synthesis to
    pick the generator whose delta best matches a sign-flipped target."""
    here = np.array(manifold.macro_coord(chamber), dtype=float)
    out: Dict[Gen, np.ndarray] = {}
    for g in GENERATORS:
        out[g] = np.array(manifold.macro_coord(apply(g, chamber)), dtype=float) - here
    return out
