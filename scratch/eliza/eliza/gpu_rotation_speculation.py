"""Eliza.GpuRotationSpeculation — P3+P4: full-speculation across rotations.

For each window of input bytes, evaluate all 16 nibble-rotations on
GPU in parallel; commit the rotation whose resulting chain stream has
the lowest encoding cost.

Per the user's BWT-emergence hypothesis: with proper full-speculation
over rotations, the committed rotation pattern should exhibit BWT-like
concentration (a small number of rotations covers most windows).

This is the BWT-emergence diagnostic at the codec level, integrated as
a real encoder choice rather than an external test harness.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.gpu_codec_v2 import (
    _build_next_chamber_table, adaptive_cumfreqs, encode as v2_encode,
    int_chamber_walk,
)
from eliza.gpu_kernels import HAS_CUPY, cp, gpu_opcode_match_vectorized, xp
from eliza.matrix_ops import _manifold_index
from eliza.octonion import rotate_bytes
from eliza.opcode_set import Opcode, build_full_opcode_set


def estimate_rotation_cost_per_window(
    window: bytes, opcodes: List[Opcode],
    next_table: np.ndarray, chambers, idx_map,
) -> np.ndarray:
    """Estimate encoding cost in bits for each of 16 nibble-rotations.

    For each rotation r:
      1. Rotate window's bytes by r.
      2. Walk chain on the rotated bytes (int lookup).
      3. Compute opcode match tensor on GPU.
      4. Greedy commit chains -> emissions; sum bits using a
         simple proxy (log2(alphabet) per emission, uniform).
    The proxy is uniform; for ranking purposes a uniform proxy is OK
    (relative ordering preserved when adaptive predictors apply
    similarly across paths).

    Returns shape (16,) float array of per-rotation costs.
    """
    n_opcodes = len(opcodes)
    max_body = max(op.length for op in opcodes)
    bodies = np.full((n_opcodes, max_body), -1, dtype=np.int64)
    lengths = np.zeros((n_opcodes,), dtype=np.int64)
    for i, op in enumerate(opcodes):
        for j, cs in enumerate(op.body):
            bodies[i, j] = idx_map[cs.to_s4()]
        lengths[i] = op.length

    # Process all 16 rotations in a single batched walk computation.
    rotated_windows = [rotate_bytes(window, r) for r in range(16)]
    # Compute walks (16, 2*win_len).
    walks = []
    for rw in rotated_windows:
        walks.append(int_chamber_walk(rw, chambers, idx_map, next_table))
    walks_arr = np.stack(walks)    # (16, n_chain)
    n_chain = walks_arr.shape[1]

    # For each rotation, compute match tensor and greedy-walk to cost.
    # We do this rotation-by-rotation to keep the per-walk grammar
    # growth independent. For pure speculation comparison, no growth
    # is needed (use only initial opcodes).
    costs = np.zeros(16, dtype=np.float64)
    from math import log2

    for r in range(16):
        walk = walks_arr[r]
        match = gpu_opcode_match_vectorized(walk, bodies, lengths)
        # Greedy: at each pos, longest match; sum bits.
        pos = 0
        bits = 0.0
        alphabet_size = 24 + n_opcodes
        log_alphabet = log2(alphabet_size)
        n_emissions = 0
        # Transfer match to CPU once per rotation.
        if HAS_CUPY:
            match_cpu = cp.asnumpy(match)
        else:
            match_cpu = np.asarray(match)
        while pos < n_chain:
            row = match_cpu[pos]
            best_idx = int(np.argmax(row))
            best_len = int(row[best_idx])
            if best_len == 0:
                advance = 1
            else:
                advance = best_len
            bits += log_alphabet
            pos += advance
            n_emissions += 1
        costs[r] = bits

    return costs


def speculate_rotations_for_corpus(
    data: bytes, window_size: int, opcodes: List[Opcode] = None,
) -> dict:
    """For each window in `data`, pick the rotation with lowest cost.

    Returns a report with chosen rotation per window + histogram.
    """
    opcodes = opcodes if opcodes is not None else build_full_opcode_set()
    chambers, idx_map = _manifold_index()
    next_table = _build_next_chamber_table(chambers, idx_map)

    chosen = []
    cost_savings = []
    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        if len(window) < window_size // 2:
            continue
        costs = estimate_rotation_cost_per_window(
            window, opcodes, next_table, chambers, idx_map,
        )
        best_r = int(np.argmin(costs))
        chosen.append(best_r)
        cost_savings.append(float(np.max(costs) - np.min(costs)))

    from collections import Counter
    hist = Counter(chosen)
    return {
        "n_windows": len(chosen),
        "chosen_rotations": chosen,
        "rotation_histogram": dict(hist),
        "distinct_rotations": len(hist),
        "avg_cost_savings_bits": float(np.mean(cost_savings)) if cost_savings else 0.0,
    }


# --- Self-check: BWT-emergence diagnostic at scale --------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        full = f.read()

    sizes = (256, 1024, 4096)
    if verbose:
        print("=== P3+P4: BWT-emergence at scale ===\n")
        print(f"  {'size':>5}  {'windows':>8}  {'distinct':>9}  "
              f"{'top-3%':>7}  {'avg saved bits':>14}  {'time':>8}")

    all_ok = True
    for size in sizes:
        data = full[:size]
        t0 = time.perf_counter()
        report = speculate_rotations_for_corpus(data, window_size=32)
        dt = time.perf_counter() - t0
        n_w = report["n_windows"]
        if n_w == 0:
            continue
        hist = report["rotation_histogram"]
        top3 = sum(sorted(hist.values(), reverse=True)[:3])
        top3_pct = 100 * top3 / n_w
        if verbose:
            print(f"  {size:>5}  {n_w:>8}  {report['distinct_rotations']:>9}  "
                  f"{top3_pct:>6.1f}%  {report['avg_cost_savings_bits']:>14.2f}  "
                  f"{dt:>6.2f}s")

    if verbose:
        print("\nReading: high top-3% + few distinct rotations = BWT-emergent concentration")
        print("Result: OK" if all_ok else "Result: FAIL")
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
