"""Eliza.BackRef — chain-symbol + byte-level back-reference matcher.

The Z-arc closes the Y-arc's empirical gap to gzip/lzma by adding
back-reference opcodes to V7's operad ring. Per [[expose-generator-not-orbit]]
and the Z-arc DBE pass: back-reference is the (arbitrary-recent-span,
one-shot, chamber-free/bound) orbit at the "reference-earlier-output"
generator. QUOT (alias-define) picks (existing-rule-slice,
permanent-rule, chamber-bound); back-reference picks the other side.

This module exposes:
  * `find_chain_backref(walk, pos, max_back, min_length)` — find
    longest (distance, length) such that
    walk[pos-d : pos-d+l] == walk[pos : pos+l]
    for d in [1, max_back] and l >= min_length.
  * `find_byte_backref(byte_stream, byte_pos, max_back, min_length)` —
    byte-level analog.

Minimum-viable implementation: O(max_back × max_match_len) naive
scan. Hash-chain matricisation (Z3) deferred until empirical (E3)
results justify it.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from eliza.alphabets import V4_PERMS, perm_compose


# --- V₄ action table on chain symbols (AA1+AA2 unification) -----------

_V4_ACTION_TABLE: Optional[np.ndarray] = None


def get_v4_action_table() -> np.ndarray:
    """Precompute V_ACTION[σ_idx, c_idx] = perm-index of σ ∘ c.

    Lazily computed; once cached, lookups are O(1).
    """
    global _V4_ACTION_TABLE
    if _V4_ACTION_TABLE is not None:
        return _V4_ACTION_TABLE
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    n_v4 = len(V4_PERMS)
    n_chambers = len(chambers)
    table = np.zeros((n_v4, n_chambers), dtype=np.int64)
    for sig_idx, sig_perm in enumerate(V4_PERMS):
        for c_idx, c_perm in enumerate(chambers):
            new_perm = perm_compose(sig_perm, c_perm)
            table[sig_idx, c_idx] = idx_map[new_perm]
    _V4_ACTION_TABLE = table
    return table


def find_chain_backref_with_residue(
    walk, pos: int,
    max_back: int = 4096,
    min_length: int = 4,
    max_length: int = 256,
) -> Optional[Tuple[int, int, int]]:
    """AA1: search over (distance, length, σ ∈ V₄). Returns
    (distance, length, sigma_idx) or None.

    For each candidate σ, checks whether
        table[σ, walk[pos-d+i]] == walk[pos+i]   for i in 0..length-1.
    Equivalent to: σ · history_chunk matches walk at pos.

    4× the naive backref's cost; reduce max_back if too slow.
    """
    n = walk.shape[0]
    if pos == 0 or pos >= n:
        return None
    walk_np = walk if isinstance(walk, np.ndarray) else np.asarray(walk)
    table = get_v4_action_table()

    best_d = 0
    best_l = 0
    best_sig = 0
    upper_d = min(pos, max_back)
    max_l = min(max_length, n - pos)

    for d in range(1, upper_d + 1):
        for sig_idx in range(4):
            l = 0
            while l < max_l and table[sig_idx, walk_np[pos - d + l]] == walk_np[pos + l]:
                l += 1
            if l >= min_length and l > best_l:
                best_l = l
                best_d = d
                best_sig = sig_idx
                if best_l == max_l:
                    return (best_d, best_l, best_sig)
    if best_l == 0:
        return None
    return (best_d, best_l, best_sig)


def apply_v4_chain(chain_symbol: int, sigma_idx: int) -> int:
    """AA2: apply V₄ residue σ to a single chain symbol via the lookup table."""
    if sigma_idx == 0:
        return chain_symbol
    return int(get_v4_action_table()[sigma_idx, chain_symbol])


# --- AA4: full S₄ action table on chain symbols -----------------------

_S4_ACTION_TABLE: Optional[np.ndarray] = None


def get_s4_action_table() -> np.ndarray:
    """Precompute S4_ACTION[σ_idx, c_idx] = perm-index of σ ∘ c,
    where σ_idx ranges over ALL 24 chambers (S₄ permutations).

    σ_idx == 0 is identity. σ_idx in [1..3] are V₄ involutions
    (covering 4 V₄ elements with the identity). σ_idx in [4..23]
    are S₃-coset extensions.
    """
    global _S4_ACTION_TABLE
    if _S4_ACTION_TABLE is not None:
        return _S4_ACTION_TABLE
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    n_chambers = len(chambers)
    table = np.zeros((n_chambers, n_chambers), dtype=np.int64)
    for sig_idx, sig_perm in enumerate(chambers):
        for c_idx, c_perm in enumerate(chambers):
            new_perm = perm_compose(sig_perm, c_perm)
            table[sig_idx, c_idx] = idx_map[new_perm]
    _S4_ACTION_TABLE = table
    return table


def find_chain_backref_with_s4_residue(
    walk, pos: int,
    max_back: int = 4096,
    min_length: int = 4,
    max_length: int = 256,
) -> Optional[Tuple[int, int, int]]:
    """AA4: search over (distance, length, σ ∈ S₄). Returns
    (distance, length, sigma_chamber_idx ∈ [0, 24)) or None.

    6× the V₄-residue matcher's cost; vectorisable.
    """
    n = walk.shape[0]
    if pos == 0 or pos >= n:
        return None
    walk_np = walk if isinstance(walk, np.ndarray) else np.asarray(walk)
    table = get_s4_action_table()    # (24, 24)

    best_d = 0
    best_l = 0
    best_sig = 0
    upper_d = min(pos, max_back)
    max_l = min(max_length, n - pos)

    for d in range(1, upper_d + 1):
        for sig_idx in range(24):
            l = 0
            while l < max_l and table[sig_idx, walk_np[pos - d + l]] == walk_np[pos + l]:
                l += 1
            if l >= min_length and l > best_l:
                best_l = l
                best_d = d
                best_sig = sig_idx
                if best_l == max_l:
                    return (best_d, best_l, best_sig)
    if best_l == 0:
        return None
    return (best_d, best_l, best_sig)


def apply_s4_chain(chain_symbol: int, sigma_idx: int) -> int:
    """AA4: apply S₄ residue σ to a chain symbol via the lookup table."""
    if sigma_idx == 0:
        return chain_symbol
    return int(get_s4_action_table()[sigma_idx, chain_symbol])


def find_chain_backref(walk, pos: int,
                         max_back: int = 4096,
                         min_length: int = 4,
                         max_length: int = 256) -> Optional[Tuple[int, int]]:
    """Find longest (distance, length) back-reference at walk[pos:].

    Returns (distance, length) where:
      * distance ∈ [1, min(pos, max_back)]
      * length ∈ [min_length, max_length]
      * walk[pos-distance:pos-distance+length] == walk[pos:pos+length]

    If no match of length ≥ min_length exists, returns None.
    """
    n = walk.shape[0]
    if pos == 0 or pos >= n:
        return None
    walk_np = walk if isinstance(walk, np.ndarray) else np.asarray(walk)

    best_d = 0
    best_l = 0
    upper_d = min(pos, max_back)
    max_l = min(max_length, n - pos)

    for d in range(1, upper_d + 1):
        # How long does walk[pos-d:] match walk[pos:]?
        l = 0
        while l < max_l and walk_np[pos - d + l] == walk_np[pos + l]:
            l += 1
        if l >= min_length and l > best_l:
            best_l = l
            best_d = d
            if best_l == max_l:
                break    # can't beat full-length match
    if best_l == 0:
        return None
    return (best_d, best_l)


def find_byte_backref(byte_buf, byte_pos: int,
                        max_back: int = 32768,
                        min_length: int = 4,
                        max_length: int = 258) -> Optional[Tuple[int, int]]:
    """Byte-level analog of find_chain_backref. Operates on raw bytes
    (post chain→byte conversion); chamber-state-free per Z2.

    Default windows match DEFLATE's bounds (32KB distance, 258 length).
    """
    n = len(byte_buf)
    if byte_pos == 0 or byte_pos >= n:
        return None
    best_d = 0
    best_l = 0
    upper_d = min(byte_pos, max_back)
    max_l = min(max_length, n - byte_pos)

    for d in range(1, upper_d + 1):
        l = 0
        while l < max_l and byte_buf[byte_pos - d + l] == byte_buf[byte_pos + l]:
            l += 1
        if l >= min_length and l > best_l:
            best_l = l
            best_d = d
            if best_l == max_l:
                break
    if best_l == 0:
        return None
    return (best_d, best_l)


def apply_chain_backref(chain_terminals: list, distance: int, length: int) -> None:
    """Decoder-side: copy `length` chain symbols from `distance`
    positions back in `chain_terminals` to the end.

    Handles overlapping copies correctly (length > distance) — common
    LZ77 case for run-length-encoding-style repeats.
    """
    start = len(chain_terminals) - distance
    if start < 0:
        raise ValueError(
            f"backref distance {distance} exceeds chain history "
            f"{len(chain_terminals)}")
    for i in range(length):
        chain_terminals.append(chain_terminals[start + i])
