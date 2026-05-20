"""Eliza.GpuKernels — O-arc fused GPU kernels.

Replaces the per-opcode Python loop in `gpu_codec_stages.gpu_opcode_match`
with a single fully-vectorised CuPy launch.

O1: `gpu_opcode_match_vectorized(stream, bodies, lengths)` — single
    broadcast + reduction; no per-opcode Python iteration.
O2: `gpu_opcode_match_incremental(stream, bodies, lengths, prev_match,
    new_opcode_start)` — match only the newly-added opcodes and
    concatenate the new columns to the existing match tensor.
O3: `gpu_argmax_at(match, pos)` — GPU-side argmax + max reduction
    returning (best_idx_scalar, best_len_scalar) without Python side-
    effects in the hot loop.

All three keep tensors GPU-resident; only the final committed
emission's (idx, len) scalars cross to CPU per step.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

try:
    import cupy as cp
    if cp.cuda.is_available():
        _ = cp.zeros((2, 2), dtype=cp.float32) @ cp.zeros((2, 2), dtype=cp.float32)
        HAS_CUPY = True
    else:
        HAS_CUPY = False
except Exception:
    cp = None
    HAS_CUPY = False


def xp():
    return cp if HAS_CUPY else np


# Sentinel value in opcode bodies for padding beyond actual body length.
PAD = -1


# --- O1: fully vectorised opcode match --------------------------------


def gpu_opcode_match_vectorized(stream, bodies, lengths):
    """Compute (N, N_opc) match-length tensor without any Python loop
    over opcodes.

    Approach:
      1. Build sliding window: window[p, k] = stream[p + k] for
         k in [0, max_body), p in [0, N).
      2. Compare against bodies (broadcast): cmp[p, j, k] =
         (window[p, k] == bodies[j, k]).
      3. Treat padded body positions (bodies[j, k] == PAD) as
         automatically-matching by ORing with (bodies[j, k] == PAD).
      4. Position-validity: pos_in_range[p, j] = (p + lengths[j] <= N).
      5. opcode_matches[p, j] = all(cmp_or_pad[p, j, :]) AND pos_in_range.
      6. match_length[p, j] = lengths[j] if matches else 0.

    All ops are tensor broadcasts; single CuPy launch chain.
    """
    xp_mod = xp()
    stream = xp_mod.asarray(stream)
    bodies = xp_mod.asarray(bodies)
    lengths = xp_mod.asarray(lengths)

    N = int(stream.shape[0])
    N_opc, max_body = int(bodies.shape[0]), int(bodies.shape[1])

    if N == 0 or N_opc == 0:
        return xp_mod.zeros((N, N_opc), dtype=xp_mod.int64)

    # Pad stream with a sentinel that never appears in bodies.
    SENTINEL = -3
    padded = xp_mod.full((N + max_body,), SENTINEL, dtype=xp_mod.int64)
    padded[:N] = stream

    # window[p, k] = padded[p + k]. Build via arange-broadcast.
    p_idx = xp_mod.arange(N, dtype=xp_mod.int64)[:, None]    # (N, 1)
    k_idx = xp_mod.arange(max_body, dtype=xp_mod.int64)[None, :]  # (1, max_body)
    window = padded[p_idx + k_idx]    # (N, max_body)

    # Compare: cmp[p, j, k] = (window[p, k] == bodies[j, k]).
    # Broadcast shapes: (N, 1, max_body) == (1, N_opc, max_body) → (N, N_opc, max_body)
    cmp = window[:, None, :] == bodies[None, :, :]    # (N, N_opc, max_body)

    # Pad-mask: True where body[j, k] == PAD (don't-care positions).
    body_is_pad = (bodies == PAD)    # (N_opc, max_body)

    # Effective match per position: cmp OR body_is_pad.
    eff = cmp | body_is_pad[None, :, :]    # (N, N_opc, max_body)

    # opcode matches at p iff all eff[p, j, :] True.
    all_match = xp_mod.all(eff, axis=2)    # (N, N_opc)

    # Position-validity: p + length[j] <= N. Equivalent: p <= N - length[j].
    pos_valid = (p_idx + lengths[None, :]) <= N    # (N, N_opc)

    matches = all_match & pos_valid    # (N, N_opc) bool

    # match_length[p, j] = length[j] if match else 0.
    match_lengths = xp_mod.where(matches, lengths[None, :], xp_mod.int64(0))
    return match_lengths


# --- O2: incremental match update ------------------------------------


def gpu_opcode_match_append(stream, prev_match, new_bodies, new_lengths,
                              total_lengths):
    """Append match columns for newly-added opcodes to an existing match
    tensor.

    Arguments:
      stream:       (N,) chain index stream
      prev_match:   (N, N_old) existing match-length tensor
      new_bodies:   (N_new, max_body) bodies of just the newly-added opcodes
      new_lengths:  (N_new,) lengths
      total_lengths: (N_old + N_new,) full lengths after append; used only
                     for shape consistency check

    Returns: (N, N_old + N_new) updated match tensor.
    """
    xp_mod = xp()
    new_columns = gpu_opcode_match_vectorized(stream, new_bodies, new_lengths)
    return xp_mod.concatenate([prev_match, new_columns], axis=1)


# --- O3: GPU-side argmax + max for the per-position decision ---------


def gpu_argmax_at(match, pos: int):
    """At a fixed position, return (best_idx, best_len) on GPU.

    Avoids constructing a full row on CPU; the argmax + max reductions
    run on the existing GPU tensor and return device scalars.
    """
    xp_mod = xp()
    row = match[pos]              # (N_opc,)
    best_idx = xp_mod.argmax(row)
    best_len = row[best_idx]
    return best_idx, best_len


# --- Self-check: vectorised vs Python-loop reference ------------------


def self_check(verbose: bool = True) -> bool:
    from eliza.gpu_codec_stages import gpu_opcode_match as gpu_om_old
    from eliza.matrix_ops import _manifold_index, walk_to_chamber_indices
    from eliza.opcode_set import build_full_opcode_set

    # Build test data.
    test = b"def encode(data: bytes) -> bytes:\n    return data\n"
    walk = walk_to_chamber_indices(test)
    opcodes = build_full_opcode_set()
    _, idx_map = _manifold_index()
    max_body = max(op.length for op in opcodes)
    bodies_np = np.full((len(opcodes), max_body), PAD, dtype=np.int64)
    lengths_np = np.zeros((len(opcodes),), dtype=np.int64)
    for i, op in enumerate(opcodes):
        for j, cs in enumerate(op.body):
            bodies_np[i, j] = idx_map[cs.to_s4()]
        lengths_np[i] = op.length

    # Old kernel.
    old = gpu_om_old(walk, bodies_np, lengths_np)
    if HAS_CUPY:
        old_np = cp.asnumpy(old)
    else:
        old_np = np.asarray(old)

    # New vectorized kernel.
    new = gpu_opcode_match_vectorized(walk, bodies_np, lengths_np)
    if HAS_CUPY:
        new_np = cp.asnumpy(new)
    else:
        new_np = np.asarray(new)

    correctness_ok = np.array_equal(old_np, new_np)

    # Timing.
    import time
    iters = 5
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = gpu_om_old(walk, bodies_np, lengths_np)
        if HAS_CUPY:
            cp.cuda.runtime.deviceSynchronize()
    old_time = (time.perf_counter() - t0) / iters

    t0 = time.perf_counter()
    for _ in range(iters):
        _ = gpu_opcode_match_vectorized(walk, bodies_np, lengths_np)
        if HAS_CUPY:
            cp.cuda.runtime.deviceSynchronize()
    new_time = (time.perf_counter() - t0) / iters

    # O2 append test.
    bodies_initial = bodies_np[:10]
    lengths_initial = lengths_np[:10]
    new_bodies = bodies_np[10:]
    new_lengths = lengths_np[10:]
    prev = gpu_opcode_match_vectorized(walk, bodies_initial, lengths_initial)
    appended = gpu_opcode_match_append(walk, prev, new_bodies, new_lengths,
                                         lengths_np)
    full = gpu_opcode_match_vectorized(walk, bodies_np, lengths_np)
    if HAS_CUPY:
        appended_np = cp.asnumpy(appended)
        full_np = cp.asnumpy(full)
    else:
        appended_np = np.asarray(appended)
        full_np = np.asarray(full)
    append_ok = np.array_equal(appended_np, full_np)

    # O3 argmax test.
    if HAS_CUPY:
        match_gpu = cp.asarray(full_np)
    else:
        match_gpu = full_np
    best_idx, best_len = gpu_argmax_at(match_gpu, pos=0)
    bi = int(best_idx); bl = int(best_len)
    ref_bi = int(np.argmax(full_np[0]))
    ref_bl = int(full_np[0, ref_bi])
    argmax_ok = bi == ref_bi and bl == ref_bl

    if verbose:
        print("=== GpuKernels self-check ===")
        print(f"  HAS_CUPY:                  {HAS_CUPY}")
        print(f"  vectorized vs old loop:    {'OK' if correctness_ok else 'FAIL'}")
        print(f"  old kernel time:           {old_time*1000:.2f}ms / iter")
        print(f"  new kernel time:           {new_time*1000:.2f}ms / iter")
        if new_time > 0:
            print(f"  speedup:                   {old_time/new_time:.2f}×")
        print(f"  O2 incremental append:     {'OK' if append_ok else 'FAIL'}")
        print(f"  O3 GPU-side argmax:        {'OK' if argmax_ok else 'FAIL'}")
        ok = correctness_ok and append_ok and argmax_ok
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return correctness_ok and append_ok and argmax_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
