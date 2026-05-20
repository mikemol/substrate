"""Eliza.Predictor — char trigram with Laplace smoothing.

Implements the Agda contract:

  * update(ch): the coalgebraic step (append one observation).
  * smoothed_prob(c): P(c | last two chars), Laplace α-smoothed.
  * surprise_bits(c): -log₂ smoothed_prob(c).
  * top_predictions(n): top-n (char, prob) pairs at the current context.
  * project_text(length, temperature): sample a continuation.

Counts live in-memory as a nested dict; persistence is the Recorder's
job. The Predictor doesn't know about SQLite.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


DEFAULT_VOCAB_SIZE = 128  # ASCII; pass vocab_size=256 for byte streams


@dataclass
class TrigramPredictor:
    alpha: float = 0.5
    vocab_size: int = DEFAULT_VOCAB_SIZE
    # counts[(c1, c2)][c3] = N
    counts: Dict[Tuple[str, str], Dict[str, int]] = field(default_factory=dict)
    context: Tuple[str, str] = ("", "")

    # --- Coalgebraic update -----------------------------------------------

    def update(self, ch: str) -> None:
        c1, c2 = self.context
        if c1 and c2:
            inner = self.counts.setdefault((c1, c2), {})
            inner[ch] = inner.get(ch, 0) + 1
        self.context = (c2, ch)

    # --- Bulk load (for warm-start from persistent storage) ---------------

    def load_counts(self, raw: Dict[Tuple[str, str], Dict[str, int]]) -> None:
        self.counts = {k: dict(v) for k, v in raw.items()}

    def export_counts(self) -> Dict[Tuple[str, str], Dict[str, int]]:
        return {k: dict(v) for k, v in self.counts.items()}

    # --- Diagnostics ------------------------------------------------------

    def n_contexts(self) -> int:
        return len(self.counts)

    def n_observations(self) -> int:
        return sum(sum(inner.values()) for inner in self.counts.values())

    # --- Probability + surprise -------------------------------------------

    def smoothed_prob(self, ch: str, context: Tuple[str, str] | None = None) -> float:
        c1, c2 = context if context is not None else self.context
        inner = self.counts.get((c1, c2), {})
        total = sum(inner.values())
        return (inner.get(ch, 0) + self.alpha) / (total + self.alpha * self.vocab_size)

    def surprise_bits(self, ch: str) -> float | None:
        c1, c2 = self.context
        if not c1 or not c2:
            return None
        p = self.smoothed_prob(ch)
        return -math.log2(p) if p > 0 else float("inf")

    # --- Top-N + sampling -------------------------------------------------

    def top_predictions(self, n: int = 5) -> List[Tuple[str, float]]:
        c1, c2 = self.context
        if not c1 or not c2:
            return []
        inner = self.counts.get((c1, c2), {})
        if not inner:
            return []
        total = sum(inner.values())
        ranked = sorted(inner.items(), key=lambda kv: -kv[1])[:n]
        return [(c, v / total) for c, v in ranked]

    def project_text(
        self,
        length: int = 60,
        temperature: float = 1.0,
        rng: random.Random | None = None,
    ) -> str:
        if temperature <= 0:
            temperature = 0.01
        rng = rng or random
        out: List[str] = []
        c1, c2 = self.context
        for _ in range(length):
            if not c1 or not c2:
                break
            inner = self.counts.get((c1, c2))
            if not inner:
                break
            chars = list(inner.keys())
            weights = [v ** (1.0 / temperature) for v in inner.values()]
            total = sum(weights)
            r = rng.random() * total
            cum = 0.0
            chosen = chars[-1]
            for c, w in zip(chars, weights):
                cum += w
                if r <= cum:
                    chosen = c
                    break
            out.append(chosen)
            c1, c2 = c2, chosen
        return "".join(out)
