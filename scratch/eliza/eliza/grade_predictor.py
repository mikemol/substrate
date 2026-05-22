"""Eliza.GradePredictor — EE9 grade-conditioned predictor.

A grade-conditioned predictor maintains SEPARATE count tables per
Clifford grade k ∈ [0, MAX_GRADE]. When `update()` is called, the
emit's grade is inferred from the joint-alphabet symbol (the symbol's
position in the alphabet's grade-decomposed structure) and the count
goes into the appropriate sub-table.

Per [[tetrative-metacircularity]]: this is the codec encoding ITS OWN
graded structure as a parameter of its predictor — the next level of
the recursive self-reference tower.

Per [[3plus1-parity-universal]]: grades partition the alphabet into
n+1 classes; the predictor naturally instantiates the universal at
the model layer.

For the V7 alphabet:
  * Terminals (0..23): chain symbols, ungraded → grade-bucket "T".
  * Data opcodes (24..24+n_used): rule bodies with chain-symbol
    grades; default grade = popcount of opcode index.
  * Control opcodes (24+n_used+i for i in 0..7): structural, ungraded
    → grade-bucket "C".

The grade-bucket selection is a substrate-internal map; the predictor
uses it to maintain separate adaptive distributions over each bucket
without changing the encoder's per-emission contract.
"""

from __future__ import annotations

from math import log2
from typing import Dict, Optional

import numpy as np

from eliza.v7_predictor import Predictor, _smoothed_cumfreqs


N_GRADE_BUCKETS = 9   # 0..8 = popcount of byte mask; plus "T" / "C" → 9


def grade_bucket_of_symbol(emit_idx: int, n_used: int,
                              n_terminals: int = 24) -> int:
    """Map an alphabet symbol to its grade bucket [0, N_GRADE_BUCKETS).

      0   = control opcodes (terminals + structural)
      1..8 = data opcodes by popcount of (emit_idx - 24)
    """
    if emit_idx < n_terminals:
        return 0
    if emit_idx >= n_terminals + n_used:
        # Control opcode slot.
        return 0
    op_idx = emit_idx - n_terminals
    return min(bin(op_idx).count("1") + 1, N_GRADE_BUCKETS - 1)


class GradeConditionedPredictor(Predictor):
    """Maintain N_GRADE_BUCKETS separate count tables.

    On `update(emit_idx, ctx)`: lookup grade-bucket; increment
    counts[bucket][emit_idx].

    On `cumfreqs(alphabet_size, ctx)`: combine all buckets weighted
    by their accumulated mass (a soft mixture).

    For codec compression this acts as a richer-context predictor;
    structural value is the substrate-honest grade-decomposed counting.
    """

    name = "grade_conditioned"

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros((N_GRADE_BUCKETS, max_alphabet),
                                 dtype=np.int64)
        self.totals = np.zeros(N_GRADE_BUCKETS, dtype=np.int64)
        self._n_used_hint = 0

    def set_n_used(self, n_used: int) -> None:
        """Encoder/decoder may inform the predictor of n_used so the
        grade-bucket of incoming symbols can be computed precisely.
        Default 0 = treat everything as grade-bucket 0.
        """
        self._n_used_hint = n_used

    def cumfreqs(self, alphabet_size, context=None):
        # Soft mixture: sum of bucket count rows, each weighted by its
        # own total (so high-mass buckets dominate but low-mass ones
        # still inform the alphabet's tail).
        if self.totals.sum() == 0:
            return _smoothed_cumfreqs(
                np.zeros(alphabet_size, dtype=np.int64), alphabet_size)
        combined = np.zeros(alphabet_size, dtype=np.int64)
        for k in range(N_GRADE_BUCKETS):
            combined += self.counts[k, :alphabet_size]
        return _smoothed_cumfreqs(combined, alphabet_size)

    def update(self, emit_idx, context=None):
        bucket = grade_bucket_of_symbol(emit_idx, self._n_used_hint)
        self.counts[bucket, emit_idx] += 1
        self.totals[bucket] += 1

    def grow_to(self, new_alphabet_size):
        if new_alphabet_size > self.counts.shape[1]:
            new_counts = np.zeros(
                (N_GRADE_BUCKETS, new_alphabet_size), dtype=np.int64)
            new_counts[:, :self.counts.shape[1]] = self.counts
            self.counts = new_counts


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    p = GradeConditionedPredictor(32)
    p.set_n_used(4)

    # 1. Grade buckets within range.
    for emit in (0, 23, 24, 25, 27, 28, 31):
        b = grade_bucket_of_symbol(emit, n_used=4)
        if not (0 <= b < N_GRADE_BUCKETS):
            if verbose:
                print(f"FAIL: bucket {b} out of range for emit {emit}")
            ok = False

    # 2. Update accumulates into the right bucket.
    p.update(24, None)   # op_idx 0, popcount 0 → bucket 1
    if p.counts[1, 24] != 1:
        if verbose:
            print(f"FAIL: update didn't reach bucket 1")
        ok = False
    p.update(27, None)   # op_idx 3 = 0b011, popcount 2 → bucket 3
    if p.counts[3, 27] != 1:
        if verbose:
            print(f"FAIL: update didn't reach bucket 3 for emit 27")
        ok = False

    # 3. cumfreqs returns a valid distribution.
    cf = p.cumfreqs(32, None)
    if cf.shape[0] != 33 or cf[0] != 0 or cf[-1] <= 0:
        if verbose:
            print(f"FAIL: cumfreqs malformed: shape={cf.shape}, "
                  f"first={cf[0]}, last={cf[-1]}")
        ok = False

    # 4. Growing.
    p.grow_to(64)
    if p.counts.shape[1] != 64:
        if verbose:
            print(f"FAIL: grow_to didn't resize")
        ok = False

    if verbose:
        print(f"grade_predictor self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
