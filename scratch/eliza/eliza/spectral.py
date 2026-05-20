"""Eliza.Spectral — the Galois pair between the V₄ ⋊ S₃ algebraic basis
and the Laplacian-eigenvector spectral basis.

Per the DATAFLOW_REMODEL correction: spectral and V₄⋊S₃ are dual
coordinate systems for the same algebra (S₄). The Laplacian of the
Cayley graph diagonalises in the irreducible-representation basis of
S₄; each spectral mode IS a coordinate function on one specific irrep.

This module gives the explicit Galois adapter:

  forward  : Chamber → SpectralCoords     (project to L's eigenbasis)
  backward : SpectralCoords → Chamber     (nearest-chamber under inverse)

Both verified to round-trip on all 24 chambers. The pair is an
`Adapter` brick (per Brick.agda's Adapter combinator); the backward
direction is the right inverse on the chambers' image, faithful in
the substrate-honest sense.

For the chooser-correction discipline: a SpectralChooser scores
rotation candidates by their projection onto specific S₃-irreps
rather than by gt cost. Both should agree asymptotically; divergences
are diagnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from eliza.alphabets import Chamber
from eliza.brick import BrickType, Unit, UNIT, Witnessing
from eliza.manifold import Manifold


# A SpectralCoords value is a 24-dim numpy array of eigenvector
# coefficients (one per spectral mode).
SpectralCoords = np.ndarray


@dataclass
class SpectralBasis:
    """Pre-computed Laplacian eigendecomposition of the S₄ Cayley graph.

    The 24×24 eigenvector matrix E has columns = eigenvectors. The
    forward map takes a chamber (one-hot indicator) and projects onto
    E's columns: `coords = E^T @ one_hot(chamber)`. Backward: take the
    chamber whose one-hot vector is closest to `E @ coords`.

    By Peter-Weyl on S₄, E's columns partition into 5 blocks
    corresponding to the 5 irreps of S₄ (dimensions 1, 1, 3, 3, 2):
      * column 0: trivial irrep (constant vector)
      * column 1: sign irrep
      * columns 2-10: standard irrep (9 = 3²)
      * columns 11-19: standard ⊗ sign irrep (9 = 3²)
      * columns 20-23: 2-dim irrep (4 = 2²)
    The block boundaries depend on eigenvalue multiplicities; this
    module sorts by eigenvalue and notes the boundaries.
    """
    eigenvalues: np.ndarray  # shape (24,)
    eigenvectors: np.ndarray  # shape (24, 24), columns = vectors

    @classmethod
    def from_manifold(cls, manifold: Manifold) -> "SpectralBasis":
        L = cls._build_laplacian(manifold)
        evals, evecs = np.linalg.eigh(L)
        return cls(eigenvalues=evals, eigenvectors=evecs)

    @staticmethod
    def _build_laplacian(manifold: Manifold) -> np.ndarray:
        """Combinatorial Laplacian L = D − A of the Cayley graph."""
        from eliza.manifold import apply
        from eliza.alphabets import GENERATORS
        n = manifold.num_chambers
        A = np.zeros((n, n), dtype=np.float64)
        for x in manifold.nodes:
            i = manifold.node_index(x)
            for g in GENERATORS:
                y = apply(g, x)
                j = manifold.node_index(y)
                A[i, j] = 1.0
        D = np.diag(A.sum(axis=1))
        return D - A

    def one_hot(self, chamber_idx: int) -> np.ndarray:
        v = np.zeros(self.eigenvectors.shape[0])
        v[chamber_idx] = 1.0
        return v

    def forward(self, chamber_idx: int) -> SpectralCoords:
        """Project a chamber's one-hot indicator onto the eigenbasis."""
        return self.eigenvectors.T @ self.one_hot(chamber_idx)

    def backward(self, coords: SpectralCoords) -> int:
        """Nearest-chamber under the inverse projection.

        Reconstruction: `reconstructed = E @ coords`. The nearest
        chamber is the argmax over the reconstructed coefficients (the
        chambers' one-hot vectors are the canonical basis).
        """
        reconstructed = self.eigenvectors @ coords
        return int(np.argmax(reconstructed))

    def verify_round_trip(self) -> bool:
        """For all 24 chambers, forward then backward returns the same
        chamber index. Always true because E is orthogonal."""
        n = self.eigenvectors.shape[0]
        for i in range(n):
            coords = self.forward(i)
            j = self.backward(coords)
            if i != j:
                return False
        return True


# --- Adapter brick ---------------------------------------------------------


@dataclass
class SpectralBasisAdapter:
    """Galois pair between chamber-index and spectral-coords spaces.

    Forward witnesses D⇒D (pure transform); pair is an Adapter brick
    per Brick.agda's Adapter combinator.
    """
    basis: SpectralBasis
    manifold: Manifold
    name: str = "spectral_adapter"
    homomorphism_tag: str = "Galois insertion (E orthogonal)"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=Chamber, D_out=SpectralCoords, S_in=Unit, S_out=Unit
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.D_TO_S  # trivial: S = Unit; pure transform

    def step(self, chamber: Chamber, _: Any = None) -> Tuple[SpectralCoords, Unit]:
        idx = self.manifold.node_index(chamber)
        return self.basis.forward(idx), UNIT

    def inverse_step(self, coords: SpectralCoords) -> Chamber:
        idx = self.basis.backward(coords)
        return self.manifold.nodes[idx]

    def stats(self) -> Dict[str, Any]:
        return {
            "spectral_eigenvalues": self.basis.eigenvalues.tolist(),
        }


# --- S₃-irrep coordinate access -------------------------------------------


def s3_irrep_blocks(basis: SpectralBasis, tol: float = 1e-9) -> List[List[int]]:
    """Group eigenvector columns by eigenvalue clusters (irrep blocks).

    Returns a list of column-index lists; each list is one eigenspace.
    For the Coxeter-generator Cayley graph these are 10 clusters; the
    canonical S₄ Peter-Weyl decomposition (1, 1, 9, 9, 4) is a coarser
    grouping when characters are used instead of eigenvalues.
    """
    evals = basis.eigenvalues
    blocks: List[List[int]] = []
    cur_block: List[int] = []
    cur_val: Optional[float] = None
    for i, v in enumerate(evals):
        if cur_val is None or abs(v - cur_val) > tol:
            if cur_block:
                blocks.append(cur_block)
            cur_block = [i]
            cur_val = v
        else:
            cur_block.append(i)
    if cur_block:
        blocks.append(cur_block)
    return blocks


# --- gtS3Irrep brick: counts keyed by spectral-block coordinate -----------


@dataclass
class GtS3IrrepBrick:
    """The S₃-side analog of `gt6`: counts keyed by which spectral block
    the chamber's coordinates put it in.

    For each emission, the block-id is computed as `argmax(|coords_in_each_block|)`
    — i.e., which irrep block has the largest projection magnitude at
    the current chamber. Counts then look like:
        `counts[(c1, c2, block_id)][emit] += 1`

    Same shape as Engine's `_gt6_counts` but keyed by spectral block
    instead of orbit canonical word. Witnesses C⇒S.
    """
    basis: SpectralBasis
    blocks: List[List[int]]
    counts: Dict[Tuple[Any, Any, int], Dict[Any, int]] = None
    n_blocks: int = 0
    name: str = "gt_s3_irrep"
    homomorphism_tag: str = "Counts keyed by Cayley-graph spectral block"

    def __post_init__(self):
        if self.counts is None:
            self.counts = {}
        self.n_blocks = len(self.blocks)

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=tuple, D_out=type(None), S_in=dict, S_out=dict)

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def block_for_chamber(self, chamber_idx: int) -> int:
        """Return the spectral-block index whose summed |coords|² is
        largest at this chamber. This is the "spectral orbit" at the
        char level — the analog of the orbit canonical word."""
        coords = self.basis.forward(chamber_idx)
        best, best_norm = 0, -1.0
        for bi, block in enumerate(self.blocks):
            norm_sq = float(sum(coords[c] ** 2 for c in block))
            if norm_sq > best_norm:
                best_norm = norm_sq
                best = bi
        return best

    def observe(self, c1: Any, c2: Any, chamber_idx: int, emit: Any) -> None:
        """Update counts keyed by (c1, c2, spectral_block)."""
        block = self.block_for_chamber(chamber_idx)
        key = (c1, c2, block)
        self.counts.setdefault(key, {})
        self.counts[key][emit] = self.counts[key].get(emit, 0) + 1

    def step(self, d_in: Any, _: Any = None) -> Tuple[None, Dict]:
        # d_in expected as (c1, c2, chamber_idx, emit)
        if d_in is not None:
            c1, c2, chamber_idx, emit = d_in
            self.observe(c1, c2, chamber_idx, emit)
        return None, self.counts

    def stats(self) -> Dict[str, Any]:
        return {
            "gtS3_n_contexts": len(self.counts),
            "gtS3_n_blocks": self.n_blocks,
        }


# --- SpectralChooser: pick rotation by spectral-mode projection ----------


@dataclass
class SpectralChooser:
    """Rotation chooser scoring by spectral projection rather than by
    gt cost.

    For each candidate rotation, compute the resulting chamber walk's
    cumulative spectral signature (sum of |coords|² over the window).
    Pick the rotation with the smallest signature magnitude (= the
    chamber walk that stays closest to the lowest-frequency modes).

    Per the V₄ ⋊ S₃ correction: this and the gt-cost chooser should
    agree asymptotically because they're reading the same algebra from
    dual coordinate bases. Divergences are diagnostic.
    """
    basis: SpectralBasis
    manifold: Manifold
    name: str = "spectral_chooser"
    homomorphism_tag: str = "spectral-distance scoring"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=list, D_out=int, S_in=Unit, S_out=Unit)

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.D_TO_C  # data selects compute (which rotation)

    def score(self, chamber_indices: List[int]) -> float:
        """Eigenvalue-weighted score: penalize high-frequency excitation.

        Sum over chambers of Σ_k λ_k · |coords_k|². Low-eigenvalue modes
        contribute less; high-eigenvalue (high-frequency) modes are
        penalized. The rotation with the smallest score concentrates
        energy in low-frequency modes — the substrate-honest analog of
        "most compressible."

        The trivial mode (λ=0, constant) is automatically excluded
        because its coefficient is multiplied by 0.
        """
        evals = self.basis.eigenvalues
        total = 0.0
        for idx in chamber_indices:
            coords = self.basis.forward(idx)
            # Eigenvalue-weighted L² norm.
            total += float(np.sum(evals * (coords ** 2)))
        return total

    def step(self, chamber_sequences: List[List[int]], _: Any = None) -> Tuple[int, Unit]:
        """Given chamber sequences (one per rotation), pick min-score."""
        best_r = 0
        best_score = float("inf")
        for r, seq in enumerate(chamber_sequences):
            s = self.score(seq)
            if s < best_score:
                best_score = s
                best_r = r
        return best_r, UNIT

    def stats(self) -> Dict[str, Any]:
        return {}
