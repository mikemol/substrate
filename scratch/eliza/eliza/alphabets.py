"""Eliza.Alphabets — Char, Gen, Chamber, Orbit + V₄ table.

Per the Agda module: Char is open-ended (Unicode strings); Gen is a closed
3-element type; Chamber is a 24-element type bijective to S₄; Orbit is a
6-element type indexed by Pairing × Chirality.

The Python representation uses simple types: Gen and Chirality as Enums,
Chamber as a 4-tuple of ints (the permutation), V₄ elements as 4-tuples,
Orbit as a 2-tuple (canonical chamber, chirality).
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple


# --- Atomic types ----------------------------------------------------------

class Gen(Enum):
    s1 = 0
    s2 = 1
    s3 = 2

    def __str__(self) -> str:
        return self.name


class Chirality(Enum):
    even = 0
    odd = 1

    def __str__(self) -> str:
        return self.name


# A Chamber is a permutation of (1, 2, 3, 4).
Chamber = Tuple[int, int, int, int]

# An Orbit is identified by its canonical chamber word (str) together with
# its chirality. Equivalently a (Pairing, Chirality) pair, but the
# canonical-chamber representation is more legible in displays.
Orbit = Tuple[str, Chirality]


# --- V₄ ≤ S₄ table ---------------------------------------------------------
# The four elements e, α=(12)(34), β=(13)(24), γ=(14)(23) as permutation
# tuples acting on (1, 2, 3, 4).

V4_PERMS: Tuple[Chamber, ...] = (
    (1, 2, 3, 4),  # e
    (2, 1, 4, 3),  # α
    (3, 4, 1, 2),  # β
    (4, 3, 2, 1),  # γ
)

V4_LABELS: Tuple[str, ...] = ("e", "α", "β", "γ")


# --- Permutation arithmetic ------------------------------------------------

def perm_compose(p: Chamber, q: Chamber) -> Chamber:
    """(p ∘ q)[i] = p[q[i] - 1]. Apply q first, then p."""
    return tuple(p[q[i] - 1] for i in range(len(q)))  # type: ignore[return-value]


def perm_inverse(p: Chamber) -> Chamber:
    """The unique q such that perm_compose(p, q) = identity."""
    n = len(p)
    inv = [0] * n
    for i in range(n):
        inv[p[i] - 1] = i + 1
    return tuple(inv)  # type: ignore[return-value]


# --- Canonical extremes ----------------------------------------------------

ORIGIN: Chamber = (1, 2, 3, 4)
W0: Chamber = (4, 3, 2, 1)
GENERATORS: Tuple[Gen, ...] = (Gen.s1, Gen.s2, Gen.s3)


# --- 4-bit nibble action: quaternion-shaped chamber step --------------------
# V₄ ≅ Q₈ / {±1}, so 4 V₄ slots are the 4 quaternion basis units {1, i, j, k}
# with the ± sign collapsed. The substrate's 3+1 parity universal places that
# ± as a separate chirality F₂ alongside V₄. A nibble (4 bits = 16 values)
# packs (V₄, ±, parity) into one quaternion-shaped chamber action:
#
#   bits 0–1: V₄ slot index (0=e, 1=α, 2=β, 3=γ) — the rotation axis class.
#   bits 2–3: S₃-involution index (0=e, 1=s1, 2=s2, 3=s1·s2·s1) — the
#             4-element involutive subset of S₃, i.e. the 3 transpositions
#             plus identity. The 3-cycles {s1·s2, s2·s1} are excluded; they
#             come back via composition of involutions, never as a unit.
#
# The chamber action for nibble n is right-multiplication by V₄[v] · S₃[s]:
#   new_chamber = chamber_before · V₄_PERMS[v] · S3_INVOLUTIONS[s]
#
# Each nibble maps to a unique S₄ permutation, so the chamber walk is
# bijective per nibble — decode is unambiguous from (chamber_before, after).

S3_INVOLUTIONS: Tuple[Chamber, ...] = (
    (1, 2, 3, 4),  # e
    (2, 1, 3, 4),  # s1 = (1 2)
    (1, 3, 2, 4),  # s2 = (2 3)
    (3, 2, 1, 4),  # s1·s2·s1 = (1 3)
)


def nibble_to_perm(n: int) -> Chamber:
    """Map nibble ∈ 0..15 to its S₄ permutation: V₄[low 2 bits] · S₃-invol[hi 2 bits]."""
    v_idx = n & 0b11
    s_idx = (n >> 2) & 0b11
    return perm_compose(V4_PERMS[v_idx], S3_INVOLUTIONS[s_idx])


NIBBLE_TO_PERM: Tuple[Chamber, ...] = tuple(nibble_to_perm(n) for n in range(16))
