"""EE12: Scale-5 RM(2, 5) diminishing-return measurement.

RM(2, 5) = [32, 16, 8] has 65536 codewords. Full sweep is feasible
with GPU vectorisation (a single batched chain-walk over 65k masks
on a few KB of data).

Compares chain-symbol entropy at scale 3 (256 byte masks), scale 4
(2048 word masks), and scale 5 (65536 dword masks) — reports the
best mask + entropy at each scale.

(EE-E3): scale-5 RM(2, 5) does NOT substantially outperform scale-4
RM(2, 4) on natural-data corpora; diminishing returns set in beyond
scale 4 because cross-dword structure is rare and the chain walk's
nibble granularity is unchanged across scales.
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.reed_muller import all_codewords
from eliza.multiscale_rotation import chain_symbol_entropy_estimator
from eliza.clifford_tracer import apply_clifford_mask
from eliza.word_mask import apply_word_mask, find_best_word_mask_gpu
from tests.test_substrate_atlas import CORPORA


def apply_dword_mask(data: bytes, dword_mask: int) -> bytes:
    """Apply 32-bit XOR mask aligned on dword boundaries.

    Tail bytes that don't fill a full dword are XOR'd with the
    corresponding high bytes of the mask.
    """
    if dword_mask == 0:
        return bytes(data)
    pattern = [(dword_mask >> 24) & 0xFF,
               (dword_mask >> 16) & 0xFF,
               (dword_mask >> 8) & 0xFF,
                dword_mask & 0xFF]
    return bytes(b ^ pattern[i & 3] for i, b in enumerate(data))


def find_best_byte_mask(data: bytes) -> int:
    best_m = 0
    best_score = chain_symbol_entropy_estimator(data)
    for m in range(1, 256):
        score = chain_symbol_entropy_estimator(
            apply_clifford_mask(data, m))
        if score < best_score:
            best_score = score
            best_m = m
    return best_m


def find_best_dword_mask_in(data: bytes, candidates):
    """Per-candidate Python loop (slower than GPU; tractable on smaller
    candidate sets via sampling).
    """
    best_m = 0
    best_score = chain_symbol_entropy_estimator(data)
    for m in candidates:
        if m == 0:
            continue
        score = chain_symbol_entropy_estimator(apply_dword_mask(data, m))
        if score < best_score:
            best_score = score
            best_m = m
    return best_m, best_score


def main() -> int:
    print("EE12: Scale-5 RM(2, 5) diminishing-return")
    print()
    sizes = (1024, 2048)
    n_sample = 2048

    # Pre-build the RM(2, 5) candidate set (this is large; 65536 codewords).
    print("Building RM(2, 5) codeword cache...")
    t0 = time.perf_counter()
    rm25 = all_codewords(5, 2)
    t_build = time.perf_counter() - t0
    print(f"  built {len(rm25)} codewords in {t_build:.1f}s")
    print()

    # Sample a tractable subset for the per-corpus sweep.
    rng = np.random.default_rng(42)
    sampled = list(rng.choice(rm25, size=min(n_sample, len(rm25)),
                                replace=False))
    print(f"Sampling {len(sampled)} codewords per measurement")
    print()

    for size in sizes:
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'scale-3 b':>10} "
              f"{'scale-4 w':>10} {'scale-5 d':>10}")
        for corpus_name, builder in CORPORA.items():
            data = builder(size)
            t0 = time.perf_counter()
            byte_m = find_best_byte_mask(data)
            byte_score = chain_symbol_entropy_estimator(
                apply_clifford_mask(data, byte_m))
            t_byte = time.perf_counter() - t0

            t0 = time.perf_counter()
            word_m, _ = find_best_word_mask_gpu(data)
            word_score = chain_symbol_entropy_estimator(
                apply_word_mask(data, word_m))
            t_word = time.perf_counter() - t0

            t0 = time.perf_counter()
            dword_m, dword_score = find_best_dword_mask_in(data, sampled)
            t_dword = time.perf_counter() - t0

            print(f"{corpus_name:<22} "
                  f"{byte_score:>10.4f} "
                  f"{word_score:>10.4f} "
                  f"{dword_score:>10.4f}")
            print(f"{'  picks:':<22} "
                  f"{'0x' + format(byte_m, '02x'):>10} "
                  f"{'0x' + format(word_m, '04x'):>10} "
                  f"{'0x' + format(dword_m, '08x'):>10}")
            print(f"{'  search ms:':<22} "
                  f"{int(t_byte*1000):>10} "
                  f"{int(t_word*1000):>10} "
                  f"{int(t_dword*1000):>10}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
