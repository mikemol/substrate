"""Eliza.WordMask — scale-4 RM(2, 4) XOR-mask sweep for the EE-arc.

DD-arc operates at byte-level (scale 3): masks are bytes,
XOR'd independently into each input byte. EE-arc lifts to scale 4:
masks are 16-bit words, XOR'd into word-aligned pairs of input bytes.

The natural mask-search restriction is RM(2, 4) = [16, 11, 4], 2048
codewords, GL(4, F₂)-invariant. Per [[expose-generator-not-orbit]]:
GL(4, F₂) is the gauge generator at scale 4; RM(r, 4) is its orbit
decomposition.

Per [[chain-walk-blocks-rotation-factor]]: scale 4 lets the codec
exploit cross-byte structure that scale 3 cannot see at all (each
byte XOR'd independently); the chain walk's stateful S₄ structure
ALSO can't factor cross-byte changes, so scale 4 is genuinely new
gauge freedom.
"""

from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np

try:
    import cupy as cp   # type: ignore
    HAS_CUPY = True
except Exception:
    cp = None
    HAS_CUPY = False

from eliza.reed_muller import all_codewords


def apply_word_mask(data: bytes, word_mask: int) -> bytes:
    """Apply 16-bit XOR mask to word-aligned byte pairs.

    Layout: bytes are processed in pairs (high, low) with the mask's
    high byte XOR'd into the high byte of the pair and the mask's low
    byte into the low byte. Odd-length data: last byte XOR'd with the
    mask's high byte.

    Involution: apply_word_mask(apply_word_mask(d, m), m) == d.
    """
    if word_mask == 0:
        return bytes(data)
    hi = (word_mask >> 8) & 0xFF
    lo = word_mask & 0xFF
    out = bytearray(len(data))
    for i in range(0, len(data) - 1, 2):
        out[i] = data[i] ^ hi
        out[i + 1] = data[i + 1] ^ lo
    if len(data) & 1:
        out[-1] = data[-1] ^ hi
    return bytes(out)


def word_mask_grade(word_mask: int) -> int:
    """Popcount of the 16-bit mask = Clifford grade in Cl(ℝ¹⁶)."""
    return bin(word_mask & 0xFFFF).count("1")


def rm_codewords_at_scale_4(r: int = 2):
    """Cached RM(r, 4) codewords as 16-bit integers."""
    return all_codewords(4, r)


def _chain_walk_indices(data: bytes) -> np.ndarray:
    """Cached chain-walk indices used by the entropy estimator.

    Returns int8 array of length 2 * len(data), one entry per nibble's
    resulting chamber index in [0, 24).
    """
    from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
    from eliza.matrix_ops import _manifold_index
    _, idx_map = _manifold_index()
    state = ORIGIN
    out = np.zeros(2 * len(data), dtype=np.int8)
    pos = 0
    for byte in data:
        for nib in ((byte >> 4) & 0xF, byte & 0xF):
            state = perm_compose(state, NIBBLE_TO_PERM[nib])
            out[pos] = idx_map[state]
            pos += 1
    return out


def _chain_symbol_entropies_gpu(
    data: bytes, candidate_masks: np.ndarray,
) -> np.ndarray:
    """Compute chain-symbol entropy for each candidate word-mask in
    parallel on the GPU (CuPy).

    `candidate_masks` is a (K,) array of 16-bit ints. Returns (K,)
    float64 entropies.

    Per the chain-walk: each nibble of the masked data maps via
    NIBBLE_TO_PERM to an S₄ element; the chain product evolves
    state through 24 chambers. We compute the histogram of chamber
    indices for each masked-data variant, then entropy.

    For tractability the chain walk is reconstructed per candidate
    via a pre-tabulated nibble-XOR transition; the heavy lift is
    the histogram which is fully vectorised.
    """
    n = len(data)
    if n == 0:
        return np.zeros(len(candidate_masks), dtype=np.float64)

    # Build (K, n) masked-data table.
    xp = cp if HAS_CUPY else np
    data_arr = xp.frombuffer(data, dtype=xp.uint8).copy()
    masks = xp.asarray(candidate_masks, dtype=xp.uint16)
    K = masks.shape[0]
    # word-mask: pair (high, low) repeated; for odd n the trailing
    # byte gets the high half.
    pairs = xp.zeros((K, 2), dtype=xp.uint8)
    pairs[:, 0] = (masks >> 8) & 0xFF
    pairs[:, 1] = masks & 0xFF
    # Tile mask over data length.
    full_mask_per_k = xp.tile(pairs, (1, (n + 1) // 2))[:, :n]
    masked = data_arr[None, :] ^ full_mask_per_k

    # Nibble extraction: (K, 2n) array of nibbles.
    hi = (masked >> 4) & 0xF
    lo = masked & 0xF
    nibbles = xp.empty((K, 2 * n), dtype=xp.uint8)
    nibbles[:, 0::2] = hi
    nibbles[:, 1::2] = lo

    # Build chain walk per candidate via scan.
    # Lookup table: state_after = perm_compose(state, NIBBLE_TO_PERM[n])
    # We need the (24 × 16) → 24 transition table.
    from eliza.alphabets import NIBBLE_TO_PERM, perm_compose
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    n_cham = len(chambers)
    transition = np.zeros((n_cham, 16), dtype=np.int8)
    for ci, c in enumerate(chambers):
        for nib in range(16):
            transition[ci, nib] = idx_map[perm_compose(c, NIBBLE_TO_PERM[nib])]
    transition_xp = xp.asarray(transition)

    # Scan: state[k, t+1] = transition[state[k, t], nibble[k, t]]
    states = xp.zeros((K, 2 * n), dtype=xp.int8)
    cur = xp.full((K,), idx_map[(1, 2, 3, 4)], dtype=xp.int8)
    for t in range(2 * n):
        cur = transition_xp[cur, nibbles[:, t]]
        states[:, t] = cur

    # Histogram per row, then entropy.
    # Use bincount-equivalent: one_hot then sum.
    one_hot = xp.zeros((K, n_cham), dtype=xp.int64)
    for t in range(2 * n):
        idx = states[:, t]
        one_hot[xp.arange(K), idx] += 1
    total = float(2 * n)
    probs = one_hot.astype(xp.float64) / total
    # Avoid log(0) via safe mask.
    log_probs = xp.where(probs > 0, xp.log2(probs), xp.zeros_like(probs))
    entropies = -(probs * log_probs).sum(axis=1)
    if HAS_CUPY:
        entropies = cp.asnumpy(entropies)
    return np.asarray(entropies)


def find_best_word_mask_gpu(
    data: bytes,
    candidates: Iterable[int] = None,
    two_stage: bool = True,
) -> Tuple[int, int]:
    """GPU-parallel version of find_best_word_mask. Same semantics
    (two-stage gate over halves), evaluates all candidates in one
    fused kernel.
    """
    if not data:
        return (0, 0)
    cands_list = list(candidates) if candidates is not None \
        else rm_codewords_at_scale_4(2)
    if 0 not in cands_list:
        cands_list = [0] + cands_list
    cands_arr = np.array(cands_list, dtype=np.uint16)

    def best_in(window: bytes) -> int:
        entropies = _chain_symbol_entropies_gpu(window, cands_arr)
        return int(cands_arr[int(np.argmin(entropies))])

    global_m = best_in(data)
    if not two_stage:
        return (global_m, word_mask_grade(global_m))
    half = max(1, len(data) // 2)
    first_m = best_in(data[:half])
    second_m = best_in(data[half:])
    if first_m == second_m == global_m:
        return (global_m, word_mask_grade(global_m))
    return (0, 0)


def find_best_word_mask(
    data: bytes,
    candidates: Iterable[int] = None,
    estimator=None,
    two_stage: bool = True,
    use_gpu: bool = True,
) -> Tuple[int, int]:
    """EE3: 16-bit XOR-mask sweep over `candidates` (default RM(2, 4)).

    Two-stage gate per DD5: first-half AND second-half AND global
    must agree, else fall back to mask = 0.

    `use_gpu=True` (default) uses the GPU-vectorised path with
    NumPy CPU fallback (no CuPy required); explicitly pass an
    `estimator` to force the per-candidate Python-loop variant.

    Returns (best_word_mask, grade).
    """
    if estimator is None and use_gpu:
        return find_best_word_mask_gpu(data, candidates, two_stage=two_stage)
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return (0, 0)
    if candidates is None:
        candidates = rm_codewords_at_scale_4(2)
    cands = list(candidates)
    if 0 not in cands:
        cands = [0] + cands

    def best_in(window: bytes) -> Tuple[int, float]:
        best_m = 0
        best_score = estimator(window)
        for m in cands:
            if m == 0:
                continue
            score = estimator(apply_word_mask(window, m))
            if score < best_score:
                best_score = score
                best_m = m & 0xFFFF
        return best_m, best_score

    global_m, _ = best_in(data)
    if not two_stage:
        return (global_m, word_mask_grade(global_m))
    half = max(1, len(data) // 2)
    first_m, _ = best_in(data[:half])
    second_m, _ = best_in(data[half:])
    if first_m == second_m == global_m:
        return (global_m, word_mask_grade(global_m))
    return (0, 0)


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Involution: applying the same mask twice returns the input.
    data = bytes(range(64))
    for m in (0x0001, 0x00FF, 0x1234, 0xFFFF, 0xABCD):
        twice = apply_word_mask(apply_word_mask(data, m), m)
        if twice != data:
            if verbose:
                print(f"FAIL: word mask {m:04x} not involution")
            ok = False

    # 2. Grade equals popcount.
    if word_mask_grade(0xF00F) != 8:
        if verbose:
            print(f"FAIL: grade(0xF00F) ≠ 8")
        ok = False

    # 3. RM(2, 4) cardinality.
    cws = rm_codewords_at_scale_4(2)
    if len(cws) != 2048:
        if verbose:
            print(f"FAIL: |RM(2,4)| = {len(cws)} ≠ 2048")
        ok = False

    # 4. Best-mask sweep returns a valid candidate.
    data = bytes((i * 13) & 0xFF for i in range(512))
    mask, grade = find_best_word_mask(data)
    if mask != 0 and mask not in set(cws):
        if verbose:
            print(f"FAIL: best mask {mask:04x} not in RM(2, 4)")
        ok = False

    # 5. Empty data returns identity.
    m, g = find_best_word_mask(b"")
    if m != 0 or g != 0:
        if verbose:
            print(f"FAIL: empty data returned ({m}, {g})")
        ok = False

    if verbose:
        print(f"word_mask self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
