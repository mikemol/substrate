"""Eliza.CoarseResidue — FF-arc V₄-coarsening of S₄ chamber residue.

Per the user's prompt: 'with EE7, we could permit ourselves to get a
little sloppy and use EE7 to recover without preserving as much
residue'. The σ ∈ S₄ residue in S_REF_RECENT (24-value alphabet,
~4.58 bits) is coarsened to σ_coarse ∈ V₄ (4 values, 2 bits). The
decoder recovers σ_full via lookup keyed on chain-walk context.

The V₄ × S₃ decomposition (per [[substrate-primitives-index]] and
the alphabets module's encoding):
  V₄ subgroup: {e, (12)(34), (13)(24), (14)(23)} — 4 elements
  S₃ via cosets: 6 cosets of V₄ in S₄ — but only 4 representable
  via the substrate's S3_INVOLUTIONS (e, s₁, s₂, s₁s₂s₁).

Each chamber c ∈ S₄ has a unique coset decomposition c = v · s where
v ∈ V₄ and s ∈ S₃-representatives (mod V₄). Coarsening keeps v,
discards s.

Disambiguation strategy: given (prev_state, σ_coarse), the decoder
enumerates σ_full ∈ V₄-coset of σ_coarse, picks the one whose
chain-walk consistency with prev_state is unique. If multiple
consistent values exist, fall back to predictor probability mass.

Per [[3plus1-parity-universal]]: V₄ has 3+1 structure (identity +
3 transposition-pairs). The coarse encoding IS a structural
projection onto the universal pattern.

Per [[chain-walk-blocks-rotation-factor]]: the chain walk's stateful
S₄ structure means most σ-residues at most prev_states have a
unique consistent recovery. The disambiguation table will identify
these cases.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from eliza.alphabets import (
    NIBBLE_TO_PERM, ORIGIN, S3_INVOLUTIONS, V4_PERMS,
    perm_compose, perm_inverse,
)
from eliza.matrix_ops import _manifold_index


def _build_v4_coarse_map() -> Tuple[Dict[int, int], Dict[int, List[int]]]:
    """Build:
      v4_coset[chamber_idx] = which V₄-coset (0..5) c belongs to.
      coset_members[coset_idx] = [chamber_idx, ...] in that coset.

    Cosets are left cosets V₄·g for g ∈ S₄ / V₄ (6 cosets, since
    [S₄ : V₄] = 6). We pick canonical representatives ordered by
    chamber index.
    """
    chambers, idx_map = _manifold_index()
    v4_set = set(V4_PERMS)
    visited: Dict[int, int] = {}
    coset_members: Dict[int, List[int]] = {}
    next_coset = 0
    # Order: assign cosets in order of chamber_idx of canonical reps.
    for ci, c in enumerate(chambers):
        if ci in visited:
            continue
        # New coset: all c · v for v ∈ V₄.
        coset = []
        for v in V4_PERMS:
            elt = perm_compose(c, v)
            elt_idx = idx_map.get(elt)
            if elt_idx is not None:
                coset.append(elt_idx)
        coset = sorted(set(coset))
        for member_idx in coset:
            visited[member_idx] = next_coset
        coset_members[next_coset] = coset
        next_coset += 1
    return visited, coset_members


def v4_coset_index(chamber_idx: int) -> int:
    """Coset index (0..5) of chamber c in S₄ / V₄.

    Per the build_map above; cached at module load.
    """
    return _V4_COSET[chamber_idx]


def coset_members(coset_idx: int) -> List[int]:
    """Chamber indices belonging to coset `coset_idx`."""
    return list(_COSET_MEMBERS[coset_idx])


def n_cosets() -> int:
    return len(_COSET_MEMBERS)


# Module-level cache built at import time.
_V4_COSET, _COSET_MEMBERS = _build_v4_coarse_map()


# --- Disambiguation table -----------------------------------------


def _build_disambiguation_table() -> Dict[Tuple[int, int], List[int]]:
    """Build (prev_chamber_idx, coset_idx) → consistent σ_full list.

    Consistency: σ ∈ S₄ is "consistent" with prev_state c_prev if
    there exists some nibble n such that c_prev · NIBBLE_TO_PERM[n]
    equals σ ∘ c_prev (i.e., σ matches the next chain-walk step).

    Equivalently: σ is reachable as a one-step chain-walk transition
    relative to c_prev's orbit.
    """
    chambers, idx_map = _manifold_index()
    n_cham = len(chambers)
    out: Dict[Tuple[int, int], List[int]] = {}
    # For each prev state, the reachable σ values are those σ for which
    # σ ∘ prev = prev ∘ NIBBLE_TO_PERM[n] for some n ∈ [0, 16).
    # Equivalently: σ = (prev ∘ NIBBLE_TO_PERM[n]) ∘ prev^{-1}.
    for prev_idx in range(n_cham):
        prev = chambers[prev_idx]
        prev_inv = perm_inverse(prev)
        for n in range(16):
            next_state = perm_compose(prev, NIBBLE_TO_PERM[n])
            sigma = perm_compose(next_state, prev_inv)
            sigma_idx = idx_map[sigma]
            coset_idx = _V4_COSET[sigma_idx]
            key = (prev_idx, coset_idx)
            members = out.setdefault(key, [])
            if sigma_idx not in members:
                members.append(sigma_idx)
    return out


_DISAMBIGUATION_TABLE: Optional[Dict[Tuple[int, int], List[int]]] = None


def disambiguation_table() -> Dict[Tuple[int, int], List[int]]:
    global _DISAMBIGUATION_TABLE
    if _DISAMBIGUATION_TABLE is None:
        _DISAMBIGUATION_TABLE = _build_disambiguation_table()
    return _DISAMBIGUATION_TABLE


def is_coarse_unique(prev_chamber_idx: int, sigma_full_idx: int) -> bool:
    """Returns True iff (prev_state, σ_coarse) uniquely determines σ_full.

    When True, the encoder can emit σ_coarse alone; the decoder
    recovers σ_full from the table.
    """
    coset_idx = _V4_COSET[sigma_full_idx]
    table = disambiguation_table()
    candidates = table.get((prev_chamber_idx, coset_idx), [])
    return len(candidates) == 1 and candidates[0] == sigma_full_idx


def recover_sigma_full(prev_chamber_idx: int, coset_idx: int,
                          fine_bits: int = 0) -> int:
    """Given (prev_state, σ_coarse) and an optional fine-tune bit
    sequence, recover σ_full.

    fine_bits ∈ [0, 2^k); the encoder emits k bits selecting between
    candidates when the coset isn't uniquely consistent.
    """
    table = disambiguation_table()
    candidates = table.get((prev_chamber_idx, coset_idx), [])
    if not candidates:
        # No reachable σ in this coset from prev — fall back to identity.
        return 0
    if len(candidates) == 1:
        return candidates[0]
    idx = fine_bits % len(candidates)
    return candidates[idx]


# --- Diagnostics --------------------------------------------------


def disambiguation_statistics() -> Dict[str, float]:
    """Per-emission empirical statistics over all (prev, σ) pairs."""
    table = disambiguation_table()
    chambers, _ = _manifold_index()
    n_cham = len(chambers)
    total = 0
    unique = 0
    pair = 0   # 2-candidate
    multi = 0
    for prev_idx in range(n_cham):
        for coset_idx in range(n_cosets()):
            cands = table.get((prev_idx, coset_idx), [])
            if not cands:
                continue
            total += 1
            if len(cands) == 1:
                unique += 1
            elif len(cands) == 2:
                pair += 1
            else:
                multi += 1
    return {
        "total_reachable_pairs": total,
        "unique_fraction": unique / total if total else 0.0,
        "pair_fraction": pair / total if total else 0.0,
        "multi_fraction": multi / total if total else 0.0,
    }


# --- FF2: NIBBLE_TO_PERM image bijection -------------------------
#
# The substrate's chain walk transitions are exactly the 16
# NIBBLE_TO_PERM elements. As σ values (chamber indices), these
# 16 form a proper subset of the 24-chamber S₄. The 8 "missing"
# chambers are those NOT reachable as single-step chain-walk
# transitions — they live "off the V₄ × S₃-involution lattice".
#
# Empirically: image chamber indices = {0,1,2,3,5,9,10,11,12,13,14,
# 18,20,21,22,23}; missing = {4,6,7,8,15,16,17,19}.
#
# Encoder can emit σ as a 4-bit nibble index (the NIBBLE_TO_PERM
# preimage) IF σ falls in the image. Savings: log₂(24) − 4 ≈ 0.58
# bits per S_REF_RECENT emission in the common case.


def _build_sigma_nibble_bijection() -> Tuple[Dict[int, int], List[int]]:
    """Return (sigma_to_nibble: dict, nibble_to_sigma: list).

    sigma_to_nibble[sigma_idx] = nibble n with NIBBLE_TO_PERM[n] at
    that chamber, or -1 if σ is not in the image.

    nibble_to_sigma[n] = chamber_idx of NIBBLE_TO_PERM[n].
    """
    _, idx_map = _manifold_index()
    nibble_to_sigma_arr: List[int] = [idx_map[NIBBLE_TO_PERM[n]]
                                          for n in range(16)]
    sigma_to_nibble_map: Dict[int, int] = {
        nibble_to_sigma_arr[n]: n for n in range(16)
    }
    return sigma_to_nibble_map, nibble_to_sigma_arr


_SIGMA_TO_NIBBLE, _NIBBLE_TO_SIGMA = _build_sigma_nibble_bijection()


def sigma_in_image(sigma_idx: int) -> bool:
    """True if σ is reachable as a single chain-walk step
    (= it's in NIBBLE_TO_PERM image).
    """
    return sigma_idx in _SIGMA_TO_NIBBLE


def sigma_to_nibble(sigma_idx: int) -> int:
    """Encode σ as a 4-bit nibble index. Caller must check
    sigma_in_image first; returns -1 otherwise.
    """
    return _SIGMA_TO_NIBBLE.get(sigma_idx, -1)


def nibble_to_sigma(nibble: int) -> int:
    """Decode a 4-bit nibble index back to σ chamber index.

    Inverse of sigma_to_nibble on the NIBBLE_TO_PERM image.
    """
    return _NIBBLE_TO_SIGMA[nibble & 0xF]


def image_size() -> int:
    """|NIBBLE_TO_PERM image| = 16."""
    return len(_NIBBLE_TO_SIGMA)


# --- Self-check ---------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Coset map covers all 24 chambers.
    if len(_V4_COSET) != 24:
        if verbose:
            print(f"FAIL: coset map has {len(_V4_COSET)} entries ≠ 24")
        ok = False

    # 2. Each coset has 4 members (size of V₄).
    for ci, members in _COSET_MEMBERS.items():
        if len(members) != 4:
            if verbose:
                print(f"FAIL: coset {ci} has {len(members)} members ≠ 4")
            ok = False

    # 3. 6 cosets total.
    if n_cosets() != 6:
        if verbose:
            print(f"FAIL: {n_cosets()} cosets ≠ 6")
        ok = False

    # 4. Disambiguation table is consistent: all entries refer to
    #    chambers in the correct coset.
    table = disambiguation_table()
    for (prev_idx, coset_idx), members in table.items():
        for m in members:
            if _V4_COSET[m] != coset_idx:
                if verbose:
                    print(f"FAIL: σ {m} not in coset {coset_idx} "
                          f"under (prev {prev_idx})")
                ok = False

    # 5. recover_sigma_full round-trip on unique entries.
    chambers, _ = _manifold_index()
    n_cham = len(chambers)
    for prev_idx in range(n_cham):
        for sigma_idx in range(n_cham):
            if is_coarse_unique(prev_idx, sigma_idx):
                ci = _V4_COSET[sigma_idx]
                recovered = recover_sigma_full(prev_idx, ci)
                if recovered != sigma_idx:
                    if verbose:
                        print(f"FAIL: recover ({prev_idx}, {ci}) = "
                              f"{recovered} ≠ {sigma_idx}")
                    ok = False

    # 6. FF2: NIBBLE_TO_PERM image bijection.
    if image_size() != 16:
        if verbose:
            print(f"FAIL: image size {image_size()} ≠ 16")
        ok = False
    # Round-trip: every nibble → σ → nibble identity.
    for n in range(16):
        s = nibble_to_sigma(n)
        if sigma_to_nibble(s) != n:
            if verbose:
                print(f"FAIL: nibble {n} ↔ σ {s} round-trip")
            ok = False
    # Image membership.
    if not sigma_in_image(nibble_to_sigma(0)):
        if verbose:
            print(f"FAIL: image membership check")
        ok = False

    # 7. Statistics sanity.
    stats = disambiguation_statistics()
    if verbose:
        print(f"  disambiguation stats: {stats}")
    if stats["unique_fraction"] + stats["pair_fraction"] + \
       stats["multi_fraction"] > 1.001:
        if verbose:
            print(f"FAIL: fractions sum > 1")
        ok = False

    if verbose:
        print(f"coarse_residue self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
