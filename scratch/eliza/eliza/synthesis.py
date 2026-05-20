"""Eliza.Synthesis — text projection (actual + branched + grammar).

Per the Agda contract:

  * `actual(predictor, length, temperature)`: unbiased sample from the
    trigram model. Delegates to predictor.project_text.

  * `branched(predictor, manifold, start_chamber, flips, length)`: at
    each step, sample what the trigram would emit; compute the spectral
    delta of that generator; sign-flip per axis; pick the generator
    whose delta best matches; sample a char in the trigram context
    emitting that generator. Falls back to the unbiased sample if no
    such char exists.

  * `from_grammar(seq, length)`: expand a random nonterminal from the
    Sequitur grammar, recursively unrolling references to terminals.
"""

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Tuple

import numpy as np

from eliza.alphabets import Chamber, Gen
from eliza.holonomy import spectral_deltas
from eliza.manifold import Manifold, apply
from eliza.predictor import TrigramPredictor
from eliza.router import Router
from eliza.sequitur import NT, Sequitur


def actual(
    predictor: TrigramPredictor,
    length: int = 60,
    temperature: float = 1.0,
    rng: random.Random | None = None,
) -> str:
    return predictor.project_text(length=length, temperature=temperature, rng=rng)


def branched(
    predictor: TrigramPredictor,
    manifold: Manifold,
    start_chamber: Chamber,
    router: Router,
    flips: Tuple[int, int],
    length: int = 60,
    rng: random.Random | None = None,
) -> str:
    """Generate a continuation whose chamber walk is biased toward the
    axis-flipped reflection of the unbiased walk's spectral delta."""
    rng = rng or random
    out: List[str] = []
    c1, c2 = predictor.context
    chamber = start_chamber
    signs = np.array(flips, dtype=float)
    for _ in range(length):
        if not c1 or not c2:
            break
        inner = predictor.counts.get((c1, c2))
        if not inner:
            break
        # 1. What would the unbiased trigram emit?
        chars = list(inner.keys())
        weights = list(inner.values())
        actual_ch = rng.choices(chars, weights=weights)[0]
        actual_gen = router(actual_ch)
        # 2. The sign-flipped target spectral delta.
        deltas = spectral_deltas(manifold, chamber)
        desired = deltas[actual_gen] * signs
        # 3. The generator whose delta best matches the target.
        shadow_gen: Gen = min(
            deltas.items(), key=lambda kv: float(np.linalg.norm(kv[1] - desired))
        )[0]
        # 4. Sample a char from the trigram context whose router output
        #    is the shadow generator. Fall back to actual_ch otherwise.
        valid = [(c, w) for c, w in zip(chars, weights) if router(c) is shadow_gen]
        if valid:
            vchars, vweights = zip(*valid)
            ch = rng.choices(list(vchars), weights=list(vweights))[0]
        else:
            ch = actual_ch
        out.append(ch)
        chamber = apply(router(ch), chamber)
        c1, c2 = c2, ch
    return "".join(out)


def from_grammar(
    grammar: Sequitur,
    length: int = 60,
    rng: random.Random | None = None,
) -> List[object]:
    """Expand a random nonterminal (or top-rule prefix) to length terminals."""
    rng = rng or random
    out: List[object] = []
    # Pick the top-rule and walk forward, expanding nonterminals greedily.
    rules = grammar.all_rules()
    if not rules:
        return out
    work: List[object] = list(rules.get(0, []))
    while work and len(out) < length:
        sym = work.pop(0)
        if isinstance(sym, NT):
            body = rules.get(sym.rule_id, [])
            work[:0] = body
        else:
            out.append(sym)
    return out[:length]
