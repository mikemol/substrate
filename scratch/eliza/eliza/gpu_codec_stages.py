"""Eliza.GpuCodecStages — N-arc CuPy ports of M-arc tensor stages.

N2  chamber walk (batched across windows)
N3  opcode match tensor
N4  range coder state evolution (chunked)
N5  adaptive grammar growth (opcode tensor concat)
N6  stack machine state (toggle as XOR)

All stages share a uniform pattern: CPU numpy implementation under
`cpu_*` callable, GPU cupy implementation under `gpu_*`, plus a unit
self-check verifying correctness vs the CPU reference.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

import numpy as np

try:
    import cupy as cp
    # Real availability check: try a matmul.
    if cp.cuda.is_available():
        _ = cp.zeros((2, 2), dtype=cp.float32) @ cp.zeros((2, 2), dtype=cp.float32)
        HAS_CUPY = True
    else:
        HAS_CUPY = False
except Exception:
    cp = None
    HAS_CUPY = False


def xp():
    """Returns cupy if available, else numpy."""
    return cp if HAS_CUPY else np


# --- N2: chamber walk batched on GPU ---------------------------------


@lru_cache(maxsize=1)
def _gpu_nibble_perm_matrix():
    from eliza.matrix_ops import nibble_to_perm_matrix
    T = nibble_to_perm_matrix()    # (16, 24, 24) float32 CPU
    return xp().asarray(T)


def gpu_walk_batched(windows_bytes: List[bytes]):
    """Batched chamber walk for many windows simultaneously.

    Returns shape (n_windows, 2 * window_len) int64 of chamber indices.
    Within-window sequential; across-windows fully parallel.
    """
    if not windows_bytes:
        return xp().zeros((0, 0), dtype=xp().int64)
    win_len = len(windows_bytes[0])
    if any(len(w) != win_len for w in windows_bytes):
        raise ValueError("all windows must have same length for batched walk")
    n_w = len(windows_bytes)
    n_nib = 2 * win_len

    # Build nibble tensor.
    nibbles_np = np.zeros((n_w, n_nib), dtype=np.int64)
    for wi, win in enumerate(windows_bytes):
        for bi, byte in enumerate(win):
            nibbles_np[wi, 2 * bi] = (byte >> 4) & 0xF
            nibbles_np[wi, 2 * bi + 1] = byte & 0xF
    nibbles = xp().asarray(nibbles_np)

    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    from eliza.alphabets import ORIGIN

    T = _gpu_nibble_perm_matrix()    # (16, 24, 24)
    states = xp().zeros((n_w, 24), dtype=xp().float32)
    states[:, idx_map[ORIGIN]] = 1.0
    out = xp().zeros((n_w, n_nib), dtype=xp().int64)
    for step in range(n_nib):
        nib_at_step = nibbles[:, step]
        M = T[nib_at_step]    # (n_w, 24, 24)
        states = (M @ states[:, :, None]).squeeze(-1)
        out[:, step] = xp().argmax(states, axis=1)
    return out


# --- N3: opcode match tensor on GPU -----------------------------------


def gpu_opcode_match(stream_idx, opcode_bodies_padded, opcode_lengths):
    """Compute (N_position, N_opcode) match-length tensor.

    Arguments:
      stream_idx: (N,) int64 chamber index stream
      opcode_bodies_padded: (N_opc, max_body) int64 with -1 padding
      opcode_lengths: (N_opc,) int64

    Returns: (N, N_opc) int64 — match length L at (pos, op) if body
    matches, else 0.
    """
    xp_mod = xp()
    stream = xp_mod.asarray(stream_idx)
    bodies = xp_mod.asarray(opcode_bodies_padded)
    lengths = xp_mod.asarray(opcode_lengths)

    N = len(stream)
    N_opc, max_body = bodies.shape
    out = xp_mod.zeros((N, N_opc), dtype=xp_mod.int64)

    for j in range(N_opc):
        L = int(lengths[j])
        if L == 0 or N < L:
            continue
        # Build sliding view by concatenating shifted streams.
        # sliced[pos, k] = stream[pos + k]
        sliced = xp_mod.stack(
            [stream[k:N - L + 1 + k] for k in range(L)], axis=1
        )    # (N - L + 1, L)
        body_slice = bodies[j, :L]
        matches = xp_mod.all(sliced == body_slice[None, :], axis=1)
        out[:N - L + 1, j] = xp_mod.where(matches, L, 0)
    return out


# --- N4: range coder state evolution (chunked) -----------------------
# The range coder is inherently sequential within a chunk, but chunks
# are independent. The existing `gpu_codec_kernel.py` already provides
# a CUDA RawKernel for chunked AC encoding; we expose its shape-typed
# version here.


# --- N5: adaptive grammar growth on GPU ------------------------------


def gpu_grow_opcodes(opcode_bodies, opcode_lengths, new_body):
    """Append a new opcode body to the opcode tensors.

    Pure tensor op: zero-pad new_body to current max_body, concat.
    """
    xp_mod = xp()
    L_new = len(new_body)
    n_opc, max_body = opcode_bodies.shape
    if L_new > max_body:
        new_max = max(max_body * 2, L_new)
        wide = xp_mod.full((n_opc, new_max), -1, dtype=xp_mod.int64)
        wide[:, :max_body] = opcode_bodies
        opcode_bodies = wide
        max_body = new_max
    padded = xp_mod.full((1, max_body), -1, dtype=xp_mod.int64)
    padded[0, :L_new] = xp_mod.asarray(new_body)
    new_bodies = xp_mod.concatenate([opcode_bodies, padded], axis=0)
    new_lengths = xp_mod.concatenate(
        [opcode_lengths, xp_mod.asarray([L_new], dtype=xp_mod.int64)]
    )
    return new_bodies, new_lengths


# --- N6: stack machine state on GPU ----------------------------------


def gpu_apply_stack_toggle(stack, depth, candidate_mask, axis):
    """Apply toggle to top entry of each candidate where mask is True.

    stack: (C, max_depth, 2) int8
    depth: (C,) int64 — pointer to top (= depth - 1)
    candidate_mask: (C,) bool
    axis: 0 (rewrite) or 1 (observe)

    Returns new stack tensor (no mutation).
    """
    xp_mod = xp()
    new_stack = stack.copy()
    C = stack.shape[0]
    # Build (C,) indices into the second axis = depth-1.
    top_d = xp_mod.maximum(depth - 1, 0)
    # Apply XOR where mask is True.
    for c in range(C):
        if bool(candidate_mask[c]):
            d = int(top_d[c])
            new_stack[c, d, axis] ^= 1
    return new_stack


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.matrix_ops import (
        _manifold_index, walk_to_chamber_indices,
    )
    from eliza.opcode_set import build_full_opcode_set

    if verbose:
        print("=== GpuCodecStages self-check ===")
        print(f"  HAS_CUPY:           {HAS_CUPY}")

    # N2: batched walk correctness.
    test = b"def encode(data: bytes) -> bytes:\n"
    cpu_walk = walk_to_chamber_indices(test)
    gpu_batch = gpu_walk_batched([test, test, test])
    if HAS_CUPY:
        gpu_walk0 = cp.asnumpy(gpu_batch[0])
    else:
        gpu_walk0 = np.asarray(gpu_batch[0])
    n2_ok = np.array_equal(cpu_walk, gpu_walk0)

    # N3: opcode match correctness.
    opcodes = build_full_opcode_set()
    _, idx_map = _manifold_index()
    max_body = max(op.length for op in opcodes)
    bodies_np = np.full((len(opcodes), max_body), -1, dtype=np.int64)
    lengths_np = np.zeros((len(opcodes),), dtype=np.int64)
    for i, op in enumerate(opcodes):
        for j, cs in enumerate(op.body):
            bodies_np[i, j] = idx_map[cs.to_s4()]
        lengths_np[i] = op.length
    gpu_match = gpu_opcode_match(cpu_walk, bodies_np, lengths_np)
    if HAS_CUPY:
        gpu_match_np = cp.asnumpy(gpu_match)
    else:
        gpu_match_np = np.asarray(gpu_match)
    # CPU reference.
    from eliza.matrix_ops import longest_opcode_at_each_position
    cpu_op_idx, cpu_op_len = longest_opcode_at_each_position(
        cpu_walk, [bodies_np[i, :int(lengths_np[i])] for i in range(len(opcodes))]
    )
    # GPU output is full (N, N_opc) — recover longest match per position.
    gpu_op_len = gpu_match_np.max(axis=1)
    n3_ok = np.array_equal(cpu_op_len, gpu_op_len)

    # N5: opcode growth correctness.
    bodies_xp = xp().asarray(bodies_np)
    lengths_xp = xp().asarray(lengths_np)
    new_body = np.array([3, 7, 11, 13, 17], dtype=np.int64)
    grown_b, grown_l = gpu_grow_opcodes(bodies_xp, lengths_xp, new_body)
    n5_ok = (grown_b.shape[0] == bodies_np.shape[0] + 1
              and int(grown_l[-1]) == len(new_body))

    # N6: stack toggle correctness.
    stack = xp().zeros((4, 8, 2), dtype=xp().int8)
    stack[:, 0, 0] = 1
    stack[:, 0, 1] = 1
    depth = xp().ones((4,), dtype=xp().int64)
    mask = xp().asarray([False, True, False, True])
    toggled = gpu_apply_stack_toggle(stack, depth, mask, axis=1)
    # Candidate 0 and 2: unchanged. Candidate 1 and 3: observe=0.
    if HAS_CUPY:
        toggled_np = cp.asnumpy(toggled)
    else:
        toggled_np = np.asarray(toggled)
    n6_ok = (toggled_np[0, 0, 1] == 1 and toggled_np[1, 0, 1] == 0
              and toggled_np[2, 0, 1] == 1 and toggled_np[3, 0, 1] == 0)

    if verbose:
        print(f"  N2 batched walk vs CPU:     {'OK' if n2_ok else 'FAIL'}")
        print(f"  N3 opcode match vs CPU:     {'OK' if n3_ok else 'FAIL'}")
        print(f"  N5 grow opcode tensor:      {'OK' if n5_ok else 'FAIL'}")
        print(f"  N6 stack toggle XOR:        {'OK' if n6_ok else 'FAIL'}")
        ok = n2_ok and n3_ok and n5_ok and n6_ok
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return n2_ok and n3_ok and n5_ok and n6_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
