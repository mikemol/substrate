"""Eliza.V7Predictor — predictor typeclass for V-arc generator ring.

Per the DBE pass: each BasisLabel in V7 is bound to a Predictor
instance. Predictors implement a uniform interface (cumfreqs / update
/ cost) so the encoder can speculate over them per emission.

Initial instances:
  * UnigramPredictor — context-free; reproduces V6 behaviour.
  * BigramPredictor — context = previous emit_idx; one row of bigram
    counts per previous symbol.

The interface deliberately exposes cumfreqs as a numpy array so the
range coder can use it directly. Predictors are stateful (counts
accumulate); update() advances the state. cost() is the bit-cost
estimate under the current state.

Per [[expose-generator-not-orbit]]: this names the GENERATOR of the
codec's emission models, which was previously hidden as "the
adaptive predictor" (a single fixed model). Now multiple models are
peers in the V-arc generator ring.
"""

from __future__ import annotations

from math import log2
from typing import Optional

import numpy as np


_ALPHA = 0.5    # Laplace smoothing parameter (matches V6/adaptive_cumfreqs).
_SCALE = 1024   # integer freq scale for range coder.


def _smoothed_cumfreqs(counts: np.ndarray, alphabet_size: int) -> np.ndarray:
    """Helper: turn a count row into the integer cumfreqs the range
    coder expects. Matches `adaptive_cumfreqs` semantics."""
    freqs = ((counts[:alphabet_size].astype(np.float64) + _ALPHA)
             * _SCALE).astype(np.int64)
    freqs = np.maximum(freqs, 1)
    cumfreqs = np.zeros(alphabet_size + 1, dtype=np.int64)
    cumfreqs[1:] = np.cumsum(freqs)
    return cumfreqs


class Predictor:
    """Abstract predictor interface used by V7 encoder/decoder."""

    name: str = "abstract"

    def cumfreqs(self, alphabet_size: int, context: Optional[int]) -> np.ndarray:
        raise NotImplementedError

    def update(self, emit_idx: int, context: Optional[int]) -> None:
        raise NotImplementedError

    def cost(self, emit_idx: int, alphabet_size: int,
               context: Optional[int]) -> float:
        cumfreqs = self.cumfreqs(alphabet_size, context)
        total = int(cumfreqs[-1])
        freq = int(cumfreqs[emit_idx + 1] - cumfreqs[emit_idx])
        if freq <= 0 or total <= 0:
            return 1e9
        return -log2(freq / total)

    def grow_to(self, new_alphabet_size: int) -> None:
        """Grow internal tables to support alphabet_size up to N."""
        raise NotImplementedError


class UnigramPredictor(Predictor):
    """Context-free adaptive counts; matches V6 default behaviour."""

    name = "unigram"

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros(max_alphabet, dtype=np.int64)

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self.counts, alphabet_size)

    def update(self, emit_idx, context=None):
        self.counts[emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        if new_alphabet_size > self.counts.shape[0]:
            new_counts = np.zeros(new_alphabet_size, dtype=np.int64)
            new_counts[:self.counts.shape[0]] = self.counts
            self.counts = new_counts


def _context_pair(context):
    """Normalize context into (prev, prev2) pair. Accepts None, int, or
    a tuple. Returns (prev_or_None, prev2_or_None).
    """
    if context is None:
        return (None, None)
    if isinstance(context, int):
        return (context, None)
    p = context[0] if len(context) > 0 else None
    p2 = context[1] if len(context) > 1 else None
    return (p, p2)


def _context_full(context):
    """Normalize context to (prev, prev2, chamber, quat) quadruple.
    Missing/invalid fields → None. Accepts None / int / tuple-of-any-length.
    """
    if context is None:
        return (None, None, None, None)
    if isinstance(context, int):
        return (context, None, None, None)
    fields = []
    for i in range(4):
        v = context[i] if len(context) > i else None
        fields.append(v if (v is None or v >= 0) else None)
    return tuple(fields)


class BigramPredictor(Predictor):
    """Context = previous emit_idx; one row of counts per prev symbol.

    Accepts context as int OR tuple (uses element 0).
    """

    name = "bigram"

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros((max_alphabet, max_alphabet), dtype=np.int64)

    def _row(self, context):
        prev, _ = _context_pair(context)
        if prev is None or prev < 0 or prev >= self.counts.shape[0]:
            return np.zeros(self.counts.shape[1], dtype=np.int64)
        return self.counts[prev]

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self._row(context), alphabet_size)

    def update(self, emit_idx, context=None):
        prev, _ = _context_pair(context)
        if prev is None or prev < 0 or prev >= self.counts.shape[0]:
            return
        self.counts[prev, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        old = self.counts.shape[0]
        if new_alphabet_size > old:
            new_counts = np.zeros(
                (new_alphabet_size, new_alphabet_size), dtype=np.int64)
            new_counts[:old, :old] = self.counts
            self.counts = new_counts


class TrigramPredictor(Predictor):
    """Context = (prev_emit_idx, prev_prev_emit_idx).

    Sparse dict-backed storage — only seen (prev2, prev) pairs occupy
    memory. Trigram storage is O(alphabet³) dense; sparse keeps it
    bounded to ~observed pairs (typically O(stream_length)).
    """

    name = "trigram"

    def __init__(self, max_alphabet: int):
        self.max_alphabet = max_alphabet
        self.rows: dict = {}     # key (prev2, prev) → count row (np.ndarray)

    def _row(self, context):
        prev, prev2 = _context_pair(context)
        if prev is None or prev2 is None:
            return np.zeros(self.max_alphabet, dtype=np.int64)
        key = (prev2, prev)
        return self.rows.get(key,
                              np.zeros(self.max_alphabet, dtype=np.int64))

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self._row(context), alphabet_size)

    def update(self, emit_idx, context=None):
        prev, prev2 = _context_pair(context)
        if prev is None or prev2 is None:
            return
        key = (prev2, prev)
        row = self.rows.get(key)
        if row is None:
            row = np.zeros(self.max_alphabet, dtype=np.int64)
            self.rows[key] = row
        elif emit_idx >= row.shape[0]:
            new_row = np.zeros(self.max_alphabet, dtype=np.int64)
            new_row[:row.shape[0]] = row
            self.rows[key] = new_row
            row = new_row
        row[emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        if new_alphabet_size > self.max_alphabet:
            old = self.max_alphabet
            self.max_alphabet = new_alphabet_size
            for key in list(self.rows):
                old_row = self.rows[key]
                new_row = np.zeros(new_alphabet_size, dtype=np.int64)
                new_row[:old_row.shape[0]] = old_row
                self.rows[key] = new_row


class ChamberContextPredictor(Predictor):
    """Context = current walk-chamber (S₄ index 0..23 or -1 if absent).

    Storage: 24 rows × alphabet (small, dense). Captures the
    chain-walk's chamber-state correlation with the next emission.
    """

    name = "chamber-context"
    N_CHAMBERS = 24

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros(
            (self.N_CHAMBERS, max_alphabet), dtype=np.int64)

    def _row(self, context):
        _, _, chamber, _ = _context_full(context)
        if chamber is None or chamber < 0 or chamber >= self.N_CHAMBERS:
            return np.zeros(self.counts.shape[1], dtype=np.int64)
        return self.counts[chamber]

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self._row(context), alphabet_size)

    def update(self, emit_idx, context=None):
        _, _, chamber, _ = _context_full(context)
        if chamber is None or chamber < 0 or chamber >= self.N_CHAMBERS:
            return
        self.counts[chamber, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        old = self.counts.shape[1]
        if new_alphabet_size > old:
            new_counts = np.zeros(
                (self.N_CHAMBERS, new_alphabet_size), dtype=np.int64)
            new_counts[:, :old] = self.counts
            self.counts = new_counts


class QuaternionContextPredictor(Predictor):
    """Context = current basis_state.quat (Q₈ index 0..7).

    Constructive use of V2's quaternion-bearing state. Storage:
    8 rows × alphabet.
    """

    name = "quat-context"
    N_QUAT = 8

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros((self.N_QUAT, max_alphabet), dtype=np.int64)

    def _row(self, context):
        _, _, _, quat = _context_full(context)
        if quat is None or quat < 0 or quat >= self.N_QUAT:
            return np.zeros(self.counts.shape[1], dtype=np.int64)
        return self.counts[quat]

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self._row(context), alphabet_size)

    def update(self, emit_idx, context=None):
        _, _, _, quat = _context_full(context)
        if quat is None or quat < 0 or quat >= self.N_QUAT:
            return
        self.counts[quat, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        old = self.counts.shape[1]
        if new_alphabet_size > old:
            new_counts = np.zeros(
                (self.N_QUAT, new_alphabet_size), dtype=np.int64)
            new_counts[:, :old] = self.counts
            self.counts = new_counts
