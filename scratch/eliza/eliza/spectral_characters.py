"""Eliza.SpectralCharacters — S₄ isotypic decomposition of the 24-dim
regular rep, restricted to the Laplacian eigenspaces.

The Cayley graph of S₄ with right-multiplication generators carries a
LEFT-multiplication S₄-action on its 24 chambers that commutes with
the Laplacian. Hence L's eigenspaces are S₄-invariant subspaces, and
by Peter-Weyl each one decomposes into S₄-irreps (5 irreps of dims
1, 1, 3, 3, 2 with multiplicities 1, 1, 3, 3, 2 in the regular rep).

This module computes the 5 isotypic projectors P_λ and tags each of
the 24 Laplacian eigenvectors with the S₄ irrep it belongs to.

Diagnostic / educational output (no longer wired as a chooser):
  * isotypic_blocks: Dict[irrep_label, List[col_idx]]
  * sylow2_block_cols: columns where V₄ acts non-trivially (Standard
    + Standard⊗sign isotypics; total 18 columns)
  * sylow3_block_cols: columns where the 2-dim S₃ irrep lives (the
    2d isotypic; total 4 columns)
  * trivial_cols: 1d isotypics (trivial + sign; total 2 columns)

NOTE on the prior atlas-as-Bezout-of-scalars framing: that framing
was retracted (see `[[codec-as-pfg-witness]]`). The chain-of-charts
template (per `Substrate.Category.PrimeFactoredGauge.MultiRoute
Equivariance`) lives in `sylow_chain.py` and `chain_chooser.py`; the
spectral partition here remains as background diagnostic, NOT as an
oracle. Eigenspace structure documents the algebra; chain
decomposition extracts the substrate-honest gauge content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import Chamber, perm_compose, perm_inverse
from eliza.manifold import Manifold
from eliza.spectral import SpectralBasis


IrrepLabel = str  # "trivial" | "sign" | "standard" | "standard_sign" | "two_dim"


# --- S₄ character table ---------------------------------------------------
# Rows = irreps; columns = conjugacy classes in the order:
#   e, (12), (12)(34), (123), (1234)
# Class sizes: 1, 6, 3, 8, 6 (sum = 24).

_CONJ_CLASS_ORDER: Tuple[str, ...] = (
    "e", "transposition", "double_transposition", "three_cycle", "four_cycle"
)

_IRREP_DIMS: Dict[IrrepLabel, int] = {
    "trivial":       1,
    "sign":          1,
    "two_dim":       2,
    "standard":      3,
    "standard_sign": 3,
}

_CHARACTERS: Dict[IrrepLabel, Dict[str, int]] = {
    "trivial":       {"e": 1, "transposition":  1, "double_transposition":  1,
                      "three_cycle":  1, "four_cycle":  1},
    "sign":          {"e": 1, "transposition": -1, "double_transposition":  1,
                      "three_cycle":  1, "four_cycle": -1},
    "two_dim":       {"e": 2, "transposition":  0, "double_transposition":  2,
                      "three_cycle": -1, "four_cycle":  0},
    "standard":      {"e": 3, "transposition":  1, "double_transposition": -1,
                      "three_cycle":  0, "four_cycle": -1},
    "standard_sign": {"e": 3, "transposition": -1, "double_transposition": -1,
                      "three_cycle":  0, "four_cycle":  1},
}


def conjugacy_class(g: Chamber) -> str:
    """Return the conjugacy class label of g ∈ S₄ by cycle type."""
    n = len(g)
    seen = [False] * n
    cycle_lengths = []
    for i in range(n):
        if seen[i]:
            continue
        j = i
        length = 0
        while not seen[j]:
            seen[j] = True
            j = g[j] - 1
            length += 1
        if length > 1:
            cycle_lengths.append(length)
    cycle_lengths.sort(reverse=True)
    if not cycle_lengths:
        return "e"
    if cycle_lengths == [2]:
        return "transposition"
    if cycle_lengths == [2, 2]:
        return "double_transposition"
    if cycle_lengths == [3]:
        return "three_cycle"
    if cycle_lengths == [4]:
        return "four_cycle"
    raise ValueError(f"unexpected cycle type {cycle_lengths} for {g}")


def left_mul_perm_matrix(h: Chamber, chambers: List[Chamber]) -> np.ndarray:
    """The 24×24 permutation matrix for σ ↦ h ∘ σ."""
    n = len(chambers)
    idx = {c: i for i, c in enumerate(chambers)}
    M = np.zeros((n, n), dtype=np.float64)
    for j, sigma in enumerate(chambers):
        h_sigma = perm_compose(h, sigma)
        i = idx[h_sigma]
        M[i, j] = 1.0
    return M


def isotypic_projector(
    irrep: IrrepLabel, chambers: List[Chamber]
) -> np.ndarray:
    """P_λ = (d_λ / |G|) · Σ_g χ_λ(g) · π(g)  (left-mult action)."""
    d_lambda = _IRREP_DIMS[irrep]
    chars = _CHARACTERS[irrep]
    n = len(chambers)
    P = np.zeros((n, n), dtype=np.float64)
    for h in chambers:
        cls = conjugacy_class(h)
        chi = chars[cls]
        if chi == 0:
            continue
        P = P + chi * left_mul_perm_matrix(h, chambers)
    return (d_lambda / n) * P


def all_isotypic_projectors(
    manifold: Manifold,
) -> Dict[IrrepLabel, np.ndarray]:
    """Compute all 5 S₄ isotypic projectors on the 24-dim chamber space."""
    chambers = manifold.nodes
    return {label: isotypic_projector(label, chambers) for label in _IRREP_DIMS}


@dataclass
class IrrepBlockReport:
    """The partition of the 24 eigenvectors by S₄ isotypic."""
    isotypic_blocks: Dict[IrrepLabel, List[int]]
    sylow2_block_cols: List[int]      # V₄ non-trivial = standard + standard_sign
    sylow3_block_cols: List[int]      # 2-dim isotypic (Z/3 non-trivial part lives here)
    trivial_cols: List[int]            # 1-dim irreps (trivial + sign)
    irrep_dims_sum: Dict[IrrepLabel, int] = field(default_factory=dict)

    def check(self) -> bool:
        """Each block has the expected dimension; total = 24."""
        expected = {"trivial": 1, "sign": 1, "two_dim": 4,
                    "standard": 9, "standard_sign": 9}
        for label, exp in expected.items():
            if len(self.isotypic_blocks.get(label, [])) != exp:
                return False
        all_cols = sorted(c for b in self.isotypic_blocks.values() for c in b)
        return all_cols == list(range(24))


def tag_eigenvectors(
    basis: SpectralBasis, manifold: Manifold, tol: float = 1e-6
) -> IrrepBlockReport:
    """Project each Laplacian eigenvector onto each isotypic; assign
    each column to the isotypic carrying ≥ tol of its norm.

    Since [L, π(g)] = 0 for all g ∈ S₄, each eigenvector lies in
    exactly one isotypic (up to numerical noise), so the assignment
    is unambiguous.
    """
    projectors = all_isotypic_projectors(manifold)
    blocks: Dict[IrrepLabel, List[int]] = {label: [] for label in _IRREP_DIMS}
    E = basis.eigenvectors                              # (24, 24), cols = vecs
    for col in range(E.shape[1]):
        v = E[:, col]
        scores = {label: float(np.linalg.norm(P @ v))
                  for label, P in projectors.items()}
        best = max(scores, key=lambda k: scores[k])
        if scores[best] < tol:
            raise ValueError(f"column {col} has no isotypic with norm ≥ {tol}")
        blocks[best].append(col)
    sylow2 = sorted(blocks["standard"] + blocks["standard_sign"])
    sylow3 = sorted(blocks["two_dim"])
    trivial = sorted(blocks["trivial"] + blocks["sign"])
    return IrrepBlockReport(
        isotypic_blocks=blocks,
        sylow2_block_cols=sylow2,
        sylow3_block_cols=sylow3,
        trivial_cols=trivial,
        irrep_dims_sum={k: len(v) for k, v in blocks.items()},
    )


# --- Self-check ----------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    m = Manifold()
    basis = SpectralBasis.from_manifold(m)
    report = tag_eigenvectors(basis, m)
    ok = report.check()
    if verbose:
        print("=== S₄ isotypic partition of the 24-dim regular rep ===")
        for label, cols in report.isotypic_blocks.items():
            d = _IRREP_DIMS[label]
            mult = len(cols) // d if d else 0
            print(f"  {label:>14}: dim {d}, mult {mult}, "
                  f"{len(cols):>2} columns  {cols}")
        print(f"\n  sylow2_block_cols (V₄-non-trivial): {len(report.sylow2_block_cols)} cols")
        print(f"  sylow3_block_cols (2-dim isotypic): {len(report.sylow3_block_cols)} cols")
        print(f"  trivial_cols (1-dim isotypics):     {len(report.trivial_cols)} cols")
        print(f"\nResult: {'OK' if ok else 'FAILURE'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
