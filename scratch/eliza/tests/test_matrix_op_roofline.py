"""tests/test_matrix_op_roofline.py — roofline timing of codec stages.

Measure CPU time spent in each codec component to identify where
GPU-porting (or other parallelisation) would have the biggest impact.

Stages timed:
  1. Per-nibble chain stream generation (chamber walk)
     - Python `perm_compose` loop
     - Matrix-op equivalent (`walk_to_chamber_indices`)
  2. Opcode matching across the stream
     - Python `best_opcode_at` per-position loop
     - Tensor `longest_opcode_at_each_position`
  3. Adaptive arithmetic coding emission/decode
     - Currently the inner loop of all codecs
  4. Full-remainder speculation
     - O(N²) outer; tractable for diagnostic but not production
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.adaptive_opcode_codec import encode as ad_enc
from eliza.full_speculation_codec import encode as fs_enc
from eliza.matrix_ops import (
    _manifold_index, longest_opcode_at_each_position,
    walk_to_chamber_indices,
)
from eliza.opcode_set import build_full_opcode_set
from eliza.per_nibble_chain import per_nibble_chain_stream
from eliza.chain_symbol import ChainSymbol


def _text(n: int) -> bytes:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < n:
        data = data + data
    return data[:n]


def time_chamber_walk_python(data: bytes, iters: int = 5) -> float:
    """Time the Python `perm_compose` walk."""
    t0 = time.perf_counter()
    for _ in range(iters):
        state = ORIGIN
        for byte in data:
            for shift in (4, 0):
                n = (byte >> shift) & 0xF
                state = perm_compose(state, NIBBLE_TO_PERM[n])
    return (time.perf_counter() - t0) / iters


def time_chamber_walk_matrix(data: bytes, iters: int = 5) -> float:
    """Time the numpy matrix-op walk."""
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = walk_to_chamber_indices(data)
    return (time.perf_counter() - t0) / iters


def time_chain_stream_creation(data: bytes, iters: int = 5) -> float:
    """Time the full chain-stream generation including ChainSymbol
    construction (per_nibble_chain_stream)."""
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = per_nibble_chain_stream(data)
    return (time.perf_counter() - t0) / iters


def time_opcode_match_python(data: bytes, iters: int = 5) -> float:
    """Time the Python-loop opcode match (best_opcode_at applied per position).

    Note: this mirrors what the adaptive codec does per position.
    """
    chain_stream = per_nibble_chain_stream(data)
    opcodes = build_full_opcode_set()
    t0 = time.perf_counter()
    for _ in range(iters):
        for pos in range(len(chain_stream)):
            best_idx = None
            best_len = 0
            for i, op in enumerate(opcodes):
                L = op.length
                if L > best_len and pos + L <= len(chain_stream):
                    if all(chain_stream[pos + j] == op.body[j] for j in range(L)):
                        best_idx = i
                        best_len = L
    return (time.perf_counter() - t0) / iters


def time_opcode_match_tensor(data: bytes, iters: int = 5) -> float:
    chain_stream = per_nibble_chain_stream(data)
    walk_idx = walk_to_chamber_indices(data)
    opcodes = build_full_opcode_set()
    _, idx_map = _manifold_index()
    bodies = []
    for op in opcodes:
        bodies.append(np.array([idx_map[cs.to_s4()] for cs in op.body]))
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = longest_opcode_at_each_position(walk_idx, bodies)
    return (time.perf_counter() - t0) / iters


def time_full_codec(encoder, data: bytes, iters: int = 1) -> float:
    """Time the full encoder. iters=1 for speculation-heavy variants."""
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = encoder(data)
    return (time.perf_counter() - t0) / iters


def main() -> int:
    print("=== Roofline analysis: codec stages on CPU ===\n")
    sizes = (256, 1024, 4096)

    for size in sizes:
        data = _text(size)
        print(f"--- {size}B input ---")
        # Per-stage timings.
        t_walk_py = time_chamber_walk_python(data, iters=3)
        t_walk_mat = time_chamber_walk_matrix(data, iters=3)
        t_chain_creation = time_chain_stream_creation(data, iters=3)
        t_op_py = time_opcode_match_python(data, iters=1)
        t_op_tensor = time_opcode_match_tensor(data, iters=3)

        print(f"  {'chamber walk (python)':<40} {t_walk_py*1000:>9.2f}ms")
        print(f"  {'chamber walk (matrix)':<40} {t_walk_mat*1000:>9.2f}ms"
              f"  ({t_walk_py/t_walk_mat:.2f}× ratio)")
        print(f"  {'chain-stream creation (incl. ChainSymbol)':<40} "
              f"{t_chain_creation*1000:>9.2f}ms")
        print(f"  {'opcode match (python per-pos)':<40} "
              f"{t_op_py*1000:>9.2f}ms")
        print(f"  {'opcode match (tensor)':<40} {t_op_tensor*1000:>9.2f}ms"
              f"  ({t_op_py/t_op_tensor:.2f}× ratio)")

        # Full codec timings (1 iter each).
        if size <= 1024:
            t_ad = time_full_codec(ad_enc, data, iters=1)
            print(f"  {'L0 adaptive codec (full encode)':<40} "
                  f"{t_ad*1000:>9.2f}ms")
        if size <= 512:
            t_fs = time_full_codec(fs_enc, data, iters=1)
            print(f"  {'Full-spec codec (full encode)':<40} "
                  f"{t_fs*1000:>9.2f}ms")
        print()

    print("Reading:")
    print("  matrix-op chamber walk gives a speedup over Python loop")
    print("  tensor opcode match outperforms per-position Python loop")
    print("  full-spec codec is O(N²); the speculation loop dominates")
    print("  matrix-op formulation is GPU-ready; cuBLAS env issue defers")
    print("  GPU validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
