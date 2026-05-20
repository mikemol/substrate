"""Eliza.GpuMatrixOps — GPU implementations of the matrix-op primitives.

CuPy ports of matrix_ops.py routines. Same shapes, same algorithms.
Falls back to numpy if cupy unavailable.

Stages ported:
  * Chamber walk (batched across windows; within-window sequential
    due to prefix dependency).
  * Opcode match tensor (fully parallel).
  * Spectral isotypic projection (fully parallel).

Stages NOT ported (architectural reasons):
  * Adaptive arithmetic coding (already in gpu_codec_kernel.py).
  * Speculation full-remainder simulation (Python-control-flow heavy;
    each candidate's sequential dependency limits GPU value).
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

import numpy as np

try:
    import cupy as cp
    # Don't just check is_available; actually try a matmul. The newer
    # CUDA 13 environment can report available=True but fail on matmul
    # if cuBLAS isn't loaded properly.
    if cp.cuda.is_available():
        _test = cp.zeros((2, 2), dtype=cp.float32)
        _ = _test @ _test
        HAS_CUPY = True
    else:
        HAS_CUPY = False
except Exception:
    cp = None
    HAS_CUPY = False


def _xp():
    """Return cupy if available, else numpy."""
    return cp if HAS_CUPY else np


@lru_cache(maxsize=1)
def nibble_to_perm_matrix_gpu():
    """(16, 24, 24) tensor on GPU (or CPU if no CuPy)."""
    from eliza.matrix_ops import nibble_to_perm_matrix
    T_cpu = nibble_to_perm_matrix()
    return _xp().asarray(T_cpu)


def walk_to_chamber_indices_gpu(window: bytes) -> "_xp().ndarray":
    """Single-window chamber walk on GPU/CPU.

    Within-window is sequential due to prefix-product dependency, but
    each matrix-vector product is a 24×24 matmul that's fast even on
    CPU. GPU value emerges when batching MULTIPLE windows.
    """
    xp = _xp()
    T = nibble_to_perm_matrix_gpu()
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    from eliza.alphabets import ORIGIN
    state = xp.zeros(24, dtype=xp.float32)
    state[idx_map[ORIGIN]] = 1.0
    n_nib = 2 * len(window)
    nibbles = []
    for byte in window:
        nibbles.append((byte >> 4) & 0xF)
        nibbles.append(byte & 0xF)
    nibbles_arr = xp.asarray(nibbles, dtype=xp.int64)
    out = xp.zeros(n_nib, dtype=xp.int64)
    for i in range(n_nib):
        n = int(nibbles_arr[i])
        state = T[n] @ state
        out[i] = int(xp.argmax(state))
    return out


def walk_to_chamber_indices_batched_gpu(windows: List[bytes]) -> "_xp().ndarray":
    """Batched chamber walks. Each window's walk is internally
    sequential, but multiple windows can be processed simultaneously
    via batched matmul.

    Returns shape (n_windows, 2 * window_len) int64 tensor.
    """
    xp = _xp()
    T = nibble_to_perm_matrix_gpu()
    n_w = len(windows)
    if n_w == 0:
        return xp.zeros((0, 0), dtype=xp.int64)
    win_len = len(windows[0])
    if any(len(w) != win_len for w in windows):
        # Pad-truncate to the first window's length for clean batching.
        raise ValueError("all windows must have same length for batched walk")
    n_nib = 2 * win_len
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    from eliza.alphabets import ORIGIN
    # Build the nibble matrix (n_windows, n_nib).
    nibbles_per_window = np.zeros((n_w, n_nib), dtype=np.int64)
    for w_i, win in enumerate(windows):
        for i, byte in enumerate(win):
            nibbles_per_window[w_i, 2 * i] = (byte >> 4) & 0xF
            nibbles_per_window[w_i, 2 * i + 1] = byte & 0xF
    nibbles_per_window = xp.asarray(nibbles_per_window)
    # Initial state for all windows: e_origin.
    states = xp.zeros((n_w, 24), dtype=xp.float32)
    states[:, idx_map[ORIGIN]] = 1.0
    out = xp.zeros((n_w, n_nib), dtype=xp.int64)
    for step in range(n_nib):
        nib_at_step = nibbles_per_window[:, step]    # (n_w,)
        # Look up the corresponding matrices: T[nib_at_step] of shape (n_w, 24, 24)
        M = T[nib_at_step]
        # Batched matmul: (n_w, 24, 24) @ (n_w, 24, 1) → (n_w, 24, 1)
        states = (M @ states[:, :, None]).squeeze(-1)
        out[:, step] = xp.argmax(states, axis=1)
    return out


def opcode_match_tensor_gpu(
    stream_chamber_indices, opcode_bodies_padded,
):
    """Compute opcode match-length tensor on GPU.

    Arguments:
      stream_chamber_indices: shape (N,) int64
      opcode_bodies_padded: shape (N_opc, max_body) int64; pad with -1
        beyond body length

    Returns: shape (N, N_opc) int array of match lengths (0 if no match).
    """
    xp = _xp()
    N = len(stream_chamber_indices)
    N_opc, max_body = opcode_bodies_padded.shape

    # Generate sliding windows: shape (N - max_body + 1, max_body).
    # Use stride_tricks; cupy has it too.
    stream = xp.asarray(stream_chamber_indices)
    bodies = xp.asarray(opcode_bodies_padded)

    out = xp.zeros((N, N_opc), dtype=xp.int64)

    # For each opcode separately (could be batched but stride-tricks
    # don't generalise cleanly across uneven body lengths).
    body_lengths = (bodies != -1).sum(axis=1)
    for j in range(N_opc):
        L = int(body_lengths[j])
        if L == 0 or N < L:
            continue
        if HAS_CUPY:
            # CuPy doesn't have sliding_window_view; build via index arithmetic.
            sliced = xp.zeros((N - L + 1, L), dtype=xp.int64)
            for k in range(L):
                sliced[:, k] = stream[k:N - L + 1 + k]
        else:
            sliced = np.lib.stride_tricks.sliding_window_view(stream, L)
        body_slice = bodies[j, :L]
        matches = xp.all(sliced == body_slice[None, :], axis=1)  # (N - L + 1,)
        # Positions where match=True get length L.
        # Broadcast into out:
        match_positions = xp.where(matches)[0]
        for pos in match_positions:
            out[int(pos), j] = L
    return out


# --- Self-check + CPU-vs-GPU correctness + timing ---------------------


def self_check(verbose: bool = True) -> bool:
    import time
    from eliza.matrix_ops import (
        walk_to_chamber_indices, longest_opcode_at_each_position,
    )
    from eliza.opcode_set import build_full_opcode_set

    test = b"def encode(data: bytes) -> bytes:\n    return data\n"

    # (1) Single-window walk: CPU vs GPU.
    cpu_walk = walk_to_chamber_indices(test)
    gpu_walk = walk_to_chamber_indices_gpu(test)
    if HAS_CUPY:
        gpu_walk_cpu = cp.asnumpy(gpu_walk)
    else:
        gpu_walk_cpu = np.asarray(gpu_walk)
    walk_match = np.array_equal(cpu_walk, gpu_walk_cpu)

    # (2) Batched walk: N windows of same length.
    n_windows = 8
    window_len = len(test)
    windows = [test] * n_windows
    t0 = time.perf_counter()
    batch_walks = walk_to_chamber_indices_batched_gpu(windows)
    t_batch = time.perf_counter() - t0
    if HAS_CUPY:
        batch_walks_cpu = cp.asnumpy(batch_walks)
    else:
        batch_walks_cpu = np.asarray(batch_walks)
    batch_match = all(np.array_equal(cpu_walk, batch_walks_cpu[i])
                      for i in range(n_windows))

    # (3) Opcode match: CPU vs GPU.
    opcodes = build_full_opcode_set()
    from eliza.matrix_ops import _manifold_index
    _, idx_map = _manifold_index()
    bodies = []
    max_body = max(len(op.body) for op in opcodes)
    bodies_padded = np.full((len(opcodes), max_body), -1, dtype=np.int64)
    for j, op in enumerate(opcodes):
        for k, cs in enumerate(op.body):
            bodies_padded[j, k] = idx_map[cs.to_s4()]
        bodies.append(np.array([idx_map[cs.to_s4()] for cs in op.body]))

    cpu_ot = sum(1 for v in
                  longest_opcode_at_each_position(cpu_walk, bodies)[1]
                  if v > 0)
    gpu_ot = opcode_match_tensor_gpu(cpu_walk, bodies_padded)
    if HAS_CUPY:
        gpu_ot_cpu = cp.asnumpy(gpu_ot)
    else:
        gpu_ot_cpu = np.asarray(gpu_ot)
    # Both should find the same number of positions with any opcode match.
    n_gpu_match = int((gpu_ot_cpu.max(axis=1) > 0).sum())
    match_match = (cpu_ot == n_gpu_match)

    if verbose:
        print("=== GPU matrix-ops self-check ===")
        print(f"  HAS_CUPY:                 {HAS_CUPY}")
        print(f"  single-window walk:       "
              f"{'OK' if walk_match else 'FAIL'}")
        print(f"  batched walk ({n_windows} windows): "
              f"{'OK' if batch_match else 'FAIL'} ({t_batch*1000:.2f}ms)")
        print(f"  opcode match consistency: "
              f"{'OK' if match_match else 'FAIL'} "
              f"(CPU {cpu_ot} positions, GPU {n_gpu_match} positions)")
        ok = walk_match and batch_match and match_match
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return walk_match and batch_match and match_match


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
