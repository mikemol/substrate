"""Eliza.Orbit — V₄-cocycle decomposition of chambers.

Per Substrate.Cocycles.V4Signature: every chamber x ∈ S₄ decomposes
uniquely as (orbit, fiber) with orbit ∈ 6-element invariant set and
fiber ∈ V₄. The orbit is itself indexed by (Pairing, Chirality).

This module is the SOLE access point to the V₄ quotient. The orbit map
is what makes downstream outputs gauge-invariant (Substrate.Discipline
Rule 5): functions on `orbit_of(x)` cannot distinguish chambers in the
same V₄-coset.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Tuple

from eliza.alphabets import (
    Chamber,
    Chirality,
    V4_LABELS,
    V4_PERMS,
    perm_compose,
    perm_inverse,
)
from eliza.manifold import Manifold


@dataclass(frozen=True)
class OrbitInfo:
    """Per-chamber V₄ decomposition view."""
    canonical: Chamber       # the shortlex-minimum element of x · V₄
    canonical_word: str      # shortlex word of `canonical` (e.g. "s1·s2")
    chirality: Chirality
    fiber_label: str         # one of V4_LABELS = ("e", "α", "β", "γ")


class Cocycle:
    """The V₄ quotient on the 24-chamber Manifold.

    Computed once at construction by enumerating right cosets and
    picking shortlex-min representatives. After that, lookups are O(1).
    """

    def __init__(self, manifold: Manifold) -> None:
        self._manifold = manifold
        self._info: Dict[Chamber, OrbitInfo] = {}
        self._compute()
        self._orbit_reps: Dict[str, Chamber] = {}
        self._s3_on_v4: Dict[Tuple[str, str], str] = {}
        self._s3_compose: Dict[Tuple[str, str], str] = {}
        self._s3_inverse: Dict[str, str] = {}
        self._build_s3_tables()

    def _compute(self) -> None:
        from eliza.manifold import word_str

        for x in self._manifold.nodes:
            coset = tuple(perm_compose(x, v) for v in V4_PERMS)
            # Canonical = shortlex-min member of the coset.
            canonical = min(
                coset,
                key=lambda c: (
                    self._manifold.bruhat_distance(c),
                    [g.value for g in self._manifold.shortlex_word(c)],
                ),
            )
            # V₄ position: v ∈ V₄ such that canonical · v = x.
            v = perm_compose(perm_inverse(canonical), x)
            v_idx = V4_PERMS.index(v)
            chir = (
                Chirality.even
                if self._manifold.bruhat_distance(x) % 2 == 0
                else Chirality.odd
            )
            self._info[x] = OrbitInfo(
                canonical=canonical,
                canonical_word=word_str(self._manifold.shortlex_word(canonical)),
                chirality=chir,
                fiber_label=V4_LABELS[v_idx],
            )

    def _build_s3_tables(self) -> None:
        """Three S₃ ≅ S₄/V₄ tables, computed once from manifold canonicals:

          * `_orbit_reps` : orbit_label → canonical S₄ representative.
          * `_s3_on_v4`   : (orbit, v4) → v4. Aut(V₄) ≅ S₃ by conjugation,
                            fixing e and permuting {α, β, γ}.
          * `_s3_compose` : (o1, o2) → o1·o2 in S₃ (group multiplication
                            in the quotient).
          * `_s3_inverse` : o → o⁻¹ in S₃.

        The compose/inverse tables let the AG flow compute relative
        rotations: `o_now · o_prev⁻¹` is "the rotation we just made,"
        distinct from `o_now` (the absolute orientation).
        """
        for x in self._manifold.nodes:
            info = self._info[x]
            if info.canonical_word not in self._orbit_reps:
                self._orbit_reps[info.canonical_word] = info.canonical
        for orbit_label, g in self._orbit_reps.items():
            g_inv = perm_inverse(g)
            for v_label, v in zip(V4_LABELS, V4_PERMS):
                rotated = perm_compose(perm_compose(g, v), g_inv)
                rotated_label = V4_LABELS[V4_PERMS.index(rotated)]
                self._s3_on_v4[(orbit_label, v_label)] = rotated_label
            inv_orbit = self._info[g_inv].canonical_word
            self._s3_inverse[orbit_label] = inv_orbit
        for o1, g1 in self._orbit_reps.items():
            for o2, g2 in self._orbit_reps.items():
                g_composed = perm_compose(g1, g2)
                self._s3_compose[(o1, o2)] = self._info[g_composed].canonical_word

    def s3_on_v4(self, orbit_label: str, fiber_label: str) -> str:
        """Apply the S₃ orbit's automorphism to a V₄ fiber label.
        Used by the AG flow: `slot = orbit · fiber` selects which V₄ slot
        of a quad-rule to read, with rule-canonical layout at orbit=e."""
        return self._s3_on_v4[(orbit_label, fiber_label)]

    def s3_compose(self, o1: str, o2: str) -> str:
        """Group multiplication in S₃ ≅ S₄/V₄."""
        return self._s3_compose[(o1, o2)]

    def s3_inverse(self, o: str) -> str:
        """Inverse in S₃ ≅ S₄/V₄."""
        return self._s3_inverse[o]

    def relative_orbit(self, o_now: str, o_ref: str) -> str:
        """`o_now · o_ref⁻¹` — the S₃ rotation from o_ref to o_now.
        This is the delta-reading of orbit: "what move did we make,"
        as distinct from "where did we land."""
        return self._s3_compose[(o_now, self._s3_inverse[o_ref])]

    # --- Public interface --------------------------------------------------

    def info(self, x: Chamber) -> OrbitInfo:
        return self._info[x]

    def orbit_of(self, x: Chamber) -> str:
        """The orbit's canonical word — the invariant address."""
        return self._info[x].canonical_word

    def chirality_of(self, x: Chamber) -> Chirality:
        return self._info[x].chirality

    def fiber_of(self, x: Chamber) -> str:
        return self._info[x].fiber_label

    def orbits(self) -> List[str]:
        """All six orbit canonical words, sorted (even first, then odd,
        then by length, then lexicographically)."""
        seen: Dict[str, Tuple[int, int, str]] = {}
        for x in self._manifold.nodes:
            info = self._info[x]
            chir_rank = 0 if info.chirality is Chirality.even else 1
            length = self._manifold.bruhat_distance(info.canonical)
            seen[info.canonical_word] = (chir_rank, length, info.canonical_word)
        return [w for w, _ in sorted(seen.items(), key=lambda kv: kv[1])]

    def coset_members(self, orbit_word: str) -> FrozenSet[Chamber]:
        """The four chambers in the named V₄-coset."""
        return frozenset(
            x for x, info in self._info.items() if info.canonical_word == orbit_word
        )

    def project_trajectory(self, traj: List[Chamber]) -> List[str]:
        """Word Chamber → Word Orbit. The Rule-1 lift through Word.map."""
        return [self._info[x].canonical_word for x in traj]
