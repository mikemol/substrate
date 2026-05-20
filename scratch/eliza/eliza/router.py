"""Eliza.Router — Char → chamber action.

The router is a gauge selection per Substrate.Discipline Rule 1; concrete
choices are interchangeable as long as their downstream orbit-level
statistics agree (the `route-is-gauge` Agda postulate).

A router maps a 1-char symbol to either a Gen (s1/s2/s3) — a single
Coxeter generator — or a Chamber (S₄ permutation) for richer per-symbol
actions such as the 4-bit-nibble quaternion-shaped step.

This module provides three named instances:

  * `ord_mod_3`: ord(ch) % 3 → Gen. Content-blind, uniform on uniformly
    distributed input. The "raw" router.

  * `char_class`: vowel/consonant/other → s1/s2/s3. Linguistically
    aligned; convergence is faster on natural-language input because the
    chamber walk inherits the vowel/consonant rhythm.

  * `nibble`: chr(0)..chr(15) → S₄ permutation via NIBBLE_TO_PERM. Used
    with the --nibbles input mode: input bytes split into two 4-bit
    nibbles, each driving a quaternion-shaped (V₄ × S₃-involution) step.

The Engine takes a `Router` and remains agnostic to which it has — but
will dispatch on the return type when applying to a chamber.
"""

from __future__ import annotations

from typing import Callable, Union

from eliza.alphabets import Chamber, Gen, NIBBLE_TO_PERM

Router = Callable[[str], Union[Gen, Chamber]]


# --- Default: ord(ch) % 3 --------------------------------------------------

_GENS = (Gen.s1, Gen.s2, Gen.s3)


def ord_mod_3(ch: str) -> Gen:
    """Deterministic 3-way partition of chars by their codepoint."""
    return _GENS[ord(ch) % 3]


# --- Alternative: char-class router ----------------------------------------

_VOWELS = frozenset("aeiouAEIOU")
_LETTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
)


def char_class(ch: str) -> Gen:
    """vowel→s1, consonant→s2, other→s3."""
    if ch in _VOWELS:
        return Gen.s1
    if ch in _LETTERS:
        return Gen.s2
    return Gen.s3


# --- Nibble router: chr(0..15) → S₄ permutation ---------------------------


def nibble(ch: str) -> Chamber:
    """Map a 1-char string ch with ord(ch) ∈ 0..15 to the corresponding
    quaternion-shaped S₄ permutation. Paired with run.py --nibbles mode,
    which yields two chr(nibble) per input byte (high nibble first)."""
    return NIBBLE_TO_PERM[ord(ch) & 0xF]


# --- Crumb router: chr(0..3) → V₄ element ----------------------------------


def crumb(ch: str) -> Chamber:
    """Map a 1-char string ch with ord(ch) ∈ 0..3 to a V₄ element.

    The substrate-natural unit: V₄ ≅ F₂² is the additive group of GF(4),
    so a 2-bit crumb is the right primitive. The chamber walk under this
    router stays within the V₄ subgroup of S₄ (4 chambers, never escapes
    to the other 20). Higher-order structure (4-bit, 8-bit groupings)
    must be DISCOVERED by the grammar via composition of crumbs — never
    baked into a single chamber step.

    Paired with run.py --crumbs mode, which yields four chr(crumb) per
    input byte (MSB pair first).
    """
    from eliza.alphabets import V4_PERMS
    return V4_PERMS[ord(ch) & 0b11]


# Default export.
default: Router = ord_mod_3
