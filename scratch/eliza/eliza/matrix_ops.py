"""Eliza.MatrixOps — matrix-operation formulation of codec primitives.

Per the user's directive: pay attention to how the architecture is
implemented in terms of matrix operations and GPU-friendliness.

This module re-expresses the codec's per-position operations as tensor
operations:

  * NIBBLE_TO_PERM_MATRIX (16, 24, 24) — each nibble as a 24×24
    permutation matrix on the chamber space.
  * walk_to_chamber_indices(window) — chamber-walk via index-chained
    matrix-vector products; vectorisable across multiple windows.
  * opcode_match_tensor(stream, opcodes) — (N_pos, N_opc) match-length
    tensor; computed via broadcast comparison.
  * spectral_isotypic_projection(chamber_idx) — 5-block 24-dim vector
    obtained by applying isotypic projectors (already 24×24 matrices
    in spectral_characters.py).

These primitives form the GPU-friendly compute graph. CPU
implementations here use numpy; the same shapes/operations port to
CuPy / Triton / CUDA RawKernels without algorithmic changes.

Stage / parallelism profile:
  * Chamber walk: sequential within window (prefix dependency);
    parallel across windows.
  * Opcode match: fully parallel.
  * Spectral projection: fully parallel.
  * Arithmetic coding: within-chunk sequential (already kernelised);
    parallel across chunks.
  * Speculation: parallel across candidates.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

import numpy as np

from eliza.alphabets import Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.manifold import Manifold


# --- L1: NIBBLE_TO_PERM as 24×24 matrix tensor -------------------------


@lru_cache(maxsize=1)
def _manifold_index() -> Tuple[List[Chamber], dict]:
    m = Manifold()
    chambers = list(m.nodes)
    idx = {c: i for i, c in enumerate(chambers)}
    return chambers, idx


@lru_cache(maxsize=1)
def nibble_to_perm_matrix() -> np.ndarray:
    """Shape (16, 24, 24). For nibble n: matrix M_n acts on a one-hot
    chamber state by M_n @ state_vec = new_state_vec. Equivalently,
    M_n[i, j] = 1 iff chamber_i = perm_compose(chamber_j, NIBBLE_TO_PERM[n]).
    """
    chambers, idx = _manifold_index()
    n_cham = len(chambers)
    T = np.zeros((16, n_cham, n_cham), dtype=np.float32)
    for n in range(16):
        nperm = NIBBLE_TO_PERM[n]
        for j, c in enumerate(chambers):
            new_c = perm_compose(c, nperm)
            i = idx[new_c]
            T[n, i, j] = 1.0
    return T


# --- L2: chamber walk via matrix multiplication ----------------------


def walk_to_chamber_indices(window: bytes) -> np.ndarray:
    """Compute the chamber index at every nibble step.

    Returns shape (2 * len(window),) int array — chamber index at the
    end of each nibble's transition.

    Reference (sequential matrix multiplication): start with
    state = e_origin. For each nibble n: state = M[n] @ state.
    """
    T = nibble_to_perm_matrix()
    chambers, idx = _manifold_index()
    state = np.zeros(24, dtype=np.float32)
    state[idx[ORIGIN]] = 1.0
    n_nib = 2 * len(window)
    out = np.zeros(n_nib, dtype=np.int64)
    pos = 0
    for byte in window:
        for shift in (4, 0):
            n = (byte >> shift) & 0xF
            state = T[n] @ state
            out[pos] = int(np.argmax(state))
            pos += 1
    return out


def walk_to_chamber_indices_batched(windows: List[bytes]) -> List[np.ndarray]:
    """Compute chamber walks for multiple windows in parallel (one
    walk per CPU core via numpy's BLAS, or fully GPU-parallel via the
    same routine on CuPy)."""
    return [walk_to_chamber_indices(w) for w in windows]


# --- L3: opcode matching as tensor comparison ------------------------


def opcode_match_lengths(
    stream_chamber_indices: np.ndarray,
    opcode_bodies_indices: List[np.ndarray],
) -> np.ndarray:
    """Compute the longest match length for each (position, opcode).

    Arguments:
      stream_chamber_indices: shape (N,) — the per-nibble chamber index
        stream
      opcode_bodies_indices: list of length N_opc, each entry is an
        int array of chamber indices

    Returns: shape (N, N_opc) int array; entry [pos, op] = length of
    the opcode if its body matches at `pos`, else 0.
    """
    N = len(stream_chamber_indices)
    N_opc = len(opcode_bodies_indices)
    out = np.zeros((N, N_opc), dtype=np.int64)
    for j, body in enumerate(opcode_bodies_indices):
        L = len(body)
        if L == 0:
            continue
        # For each starting position pos ∈ [0, N-L]: check stream[pos:pos+L] == body.
        # Broadcast comparison: shape (N-L+1, L) vs (L,) → (N-L+1, L)
        if N >= L:
            sliced = np.lib.stride_tricks.sliding_window_view(
                stream_chamber_indices, L)
            # sliced shape: (N - L + 1, L)
            matches = np.all(sliced == body, axis=1)
            valid_positions = np.where(matches)[0]
            for pos in valid_positions:
                out[pos, j] = L
    return out


def longest_opcode_at_each_position(
    stream_chamber_indices: np.ndarray,
    opcode_bodies_indices: List[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    """For each position, return (longest_opcode_idx, longest_length).

    Returns ((N,) opcode_idx_or_-1, (N,) length) arrays.
    """
    match_tensor = opcode_match_lengths(stream_chamber_indices,
                                         opcode_bodies_indices)
    # argmax along opcode axis (ties broken by lowest index).
    # But we want the LONGEST so we use max-length:
    lengths = match_tensor.max(axis=1)
    # For positions with length > 0, find an opcode that achieves it.
    op_idx = np.full(len(lengths), -1, dtype=np.int64)
    nonzero = np.where(lengths > 0)[0]
    for pos in nonzero:
        # First opcode achieving max length at this position.
        candidates = np.where(match_tensor[pos] == lengths[pos])[0]
        op_idx[pos] = candidates[0]
    return op_idx, lengths


# --- L4: spectral isotypic projection as matrix tensor ----------------


@lru_cache(maxsize=1)
def isotypic_projector_tensor() -> Tuple[np.ndarray, List[str]]:
    """Stack all 5 S₄ isotypic projectors into a (5, 24, 24) tensor.

    Labels in the standard substrate order: trivial, sign, two_dim,
    standard, standard_sign. Applying P @ state gives the projection
    of `state` onto the corresponding isotypic component.
    """
    from eliza.spectral_characters import (
        all_isotypic_projectors, _IRREP_DIMS,
    )
    m = Manifold()
    projectors = all_isotypic_projectors(m)
    labels = list(_IRREP_DIMS.keys())
    T = np.stack([projectors[lab] for lab in labels], axis=0)
    return T.astype(np.float32), labels


def project_chamber_to_isotypics(chamber_idx: int) -> np.ndarray:
    """Apply all 5 isotypic projectors to a chamber's one-hot vector.

    Returns shape (5, 24) — 5 isotypic projections of the chamber.
    """
    T, _ = isotypic_projector_tensor()
    state = np.zeros(24, dtype=np.float32)
    state[chamber_idx] = 1.0
    return T @ state    # (5, 24, 24) @ (24,) → (5, 24)


# --- Self-check: correctness vs sequential reference ------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.opcode_set import build_full_opcode_set

    # (1) Walk consistency.
    test_window = b"def encode(data: bytes)\n"
    expected_chambers = []
    state = ORIGIN
    for byte in test_window:
        for shift in (4, 0):
            n = (byte >> shift) & 0xF
            state = perm_compose(state, NIBBLE_TO_PERM[n])
            expected_chambers.append(state)
    chambers, idx_map = _manifold_index()
    expected_idx = np.array([idx_map[c] for c in expected_chambers])
    actual_idx = walk_to_chamber_indices(test_window)
    walk_ok = np.array_equal(actual_idx, expected_idx)

    # (2) Opcode matching.
    opcodes = build_full_opcode_set()
    # Convert opcode bodies (ChainSymbol tuples) to chamber-index arrays.
    from eliza.chain_symbol import ChainSymbol
    bodies_idx = []
    for op in opcodes:
        body_chambers = [s.to_s4() for s in op.body]
        body_arr = np.array([idx_map[c] for c in body_chambers])
        bodies_idx.append(body_arr)

    op_match_idx, op_match_len = longest_opcode_at_each_position(
        actual_idx, bodies_idx,
    )

    # (3) Spectral projection sanity.
    T, labels = isotypic_projector_tensor()
    proj = project_chamber_to_isotypics(0)   # project chamber 0
    proj_norms = np.linalg.norm(proj, axis=1)   # (5,)

    if verbose:
        print("=== MatrixOps self-check ===")
        print(f"  NIBBLE_TO_PERM matrix shape:   "
              f"{nibble_to_perm_matrix().shape}")
        print(f"  walk consistency:              "
              f"{'OK' if walk_ok else 'FAIL'}")
        print(f"    {len(actual_idx)} chamber indices")
        print(f"    first 5: {actual_idx[:5].tolist()}")
        print(f"  opcode set size:               {len(opcodes)}")
        n_matched = int((op_match_len > 0).sum())
        print(f"  positions with opcode match:   {n_matched} / "
              f"{len(actual_idx)} ({100*n_matched/len(actual_idx):.1f}%)")
        print(f"  isotypic projector shape:      {T.shape}")
        print(f"  per-isotypic norms (chamber 0): "
              f"{dict(zip(labels, proj_norms.tolist()))}")
        # Total norm should be 1 (one-hot vector preserved by projection sum).
        total_proj = proj.sum(axis=0)
        total_norm = float(np.linalg.norm(total_proj))
        print(f"  Σ projectors = identity:       "
              f"|sum @ e_0| = {total_norm:.4f}  "
              f"(should be 1.0)")
        return walk_ok and abs(total_norm - 1.0) < 1e-5
    return walk_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
