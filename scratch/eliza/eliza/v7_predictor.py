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


class BigramPredictor(Predictor):
    """Context = previous emit_idx; one row of counts per prev symbol.

    For context=None (no previous emission), falls back to a uniform-
    prior row.
    """

    name = "bigram"

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros((max_alphabet, max_alphabet), dtype=np.int64)

    def _row(self, context):
        if context is None or context < 0 or context >= self.counts.shape[0]:
            # No context — use a synthetic uniform row.
            return np.zeros(self.counts.shape[1], dtype=np.int64)
        return self.counts[context]

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self._row(context), alphabet_size)

    def update(self, emit_idx, context=None):
        if context is None or context < 0 or context >= self.counts.shape[0]:
            return  # nothing to update without context
        self.counts[context, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        old = self.counts.shape[0]
        if new_alphabet_size > old:
            new_counts = np.zeros(
                (new_alphabet_size, new_alphabet_size), dtype=np.int64)
            new_counts[:old, :old] = self.counts
            self.counts = new_counts
