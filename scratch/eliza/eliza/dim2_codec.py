"""Eliza.Dim2Codec — the two-Sequitur architecture realized.

Per-window:
  1. Compute the unrotated window's recursive-2-bin signature at fixed depth.
  2. Choose a rotation (16 candidates) — query the rotation cache by
     signature; on miss, search by gt-cost from the input predictor.
  3. Encode the 4-bit rotation tag.
  4. Encode the rotated window via gt + arithmetic coding.
  5. Observe (signature, rotation) into Sequitur_rotations.
  6. Predictor sees the ROTATED bytes (so its counts are over the
     post-rotation distribution).

Decoder runs in lockstep: read tag, decode rotated bytes, apply inverse
rotation, re-derive signature, observe (signature, rotation) into the
decoder's Sequitur_rotations, advance predictor.

This is the dimension-2 codec: input Sequitur (predictor.counts) +
rotation Sequitur (Sequitur_rotations). The chooser is the 2-cell that
witnesses their coherence; round-trip correctness is the 2-cell being
natural.

Categorical type emitted: DirectProduct(FreeCyclic_input, Z_16_rotations).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.codec import _cumfreqs_from_predictor
from eliza.octonion import ROTATION_LUT, compose_rotations, rotate_bytes
from eliza.predictor import TrigramPredictor
from eliza.sequitur import Sequitur
from eliza.signature import quantize, signature


SIG_DEPTH = 4         # H-rung resolution: 16-bin signature
SIG_LEVELS = 8        # quantize signature counts to 8 levels per bin
ROT_TAG_BITS = 4      # 16 rotations
ROT_TAG_TOTAL = 16    # uniform


def _key_for_signature(window: bytes) -> Tuple[int, ...]:
    return quantize(signature(window, depth=SIG_DEPTH), levels=SIG_LEVELS)


def _score_rotation(rotated_bytes: bytes, pred: TrigramPredictor) -> float:
    """Sum of -log₂ P over rotated bytes, READ-ONLY against pred's state.
    Identifies which rotation makes the window look most familiar to the
    current predictor."""
    c1, c2 = pred.context
    cost = 0.0
    alpha = pred.alpha
    vocab = pred.vocab_size
    for b in rotated_bytes:
        ch = chr(b)
        if c1 and c2:
            inner = pred.counts.get((c1, c2), {})
            total = sum(inner.values())
            p = (inner.get(ch, 0) + alpha) / (total + alpha * vocab)
            cost += -math.log2(p) if p > 0 else 32.0
        c1, c2 = c2, ch
    return cost


def _choose_rotation_canonical(
    window: bytes, pred: TrigramPredictor
) -> int:
    """Score each rotation r by the SINGLE canonical predictor's surprise
    on rotation_r(window). The rotation that brings the window closest
    to the predictor's learned canonical distribution wins. The group
    acts on the input; the predictor stays canonical. This is the
    DirectProduct 2-cell: predictor is the FreeCyclic side, rotation is
    the Zₙ side, chooser is the projection."""
    best_r = 0
    best_cost = float("inf")
    for r in range(16):
        rotated = rotate_bytes(window, r)
        cost = _score_rotation(rotated, pred)
        if cost < best_cost:
            best_cost = cost
            best_r = r
    return best_r


def encode(
    data: bytes, window_size: int = 256,
    rotation_chooser=None,
) -> Tuple[bytes, dict]:
    """Encode `data` via the dim-2 codec with canonical predictor.

    `rotation_chooser`, if provided, is called as `chooser(window, pred)`
    and must return r ∈ 0..15. Default = the canonical PresentedGroup
    chooser. Per [[multi-route-equivariance-recovery]] / S9, the codec
    exposes the chooser slot so peer-views (atlas, etc.) can plug in
    without changing the rest of the pipeline.
    """
    chooser = rotation_chooser if rotation_chooser is not None else _choose_rotation_canonical
    pred = TrigramPredictor(vocab_size=256)
    seq_rot = Sequitur()
    # D8: ChainSequitur observes the per-window walk chain alongside
    # the rotation tag. Substrate-native recursive grammar over the
    # workspace (W-axis) carrier.
    from eliza.chain_sequitur import ChainSequitur
    from eliza.chain_symbol import ChainSymbol
    from eliza.walk_carrier import walk_to_s4
    chain_seq = ChainSequitur()
    enc = RangeEncoder()
    rotation_counter = [0] * 16

    rot_cumfreqs = list(range(ROT_TAG_TOTAL + 1))

    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        # 1: choose rotation via the (default canonical / injected peer) chooser.
        r = chooser(window, pred)
        enc.encode(rot_cumfreqs, r, ROT_TAG_TOTAL)
        rotation_counter[r] += 1
        # 2: encode rotated bytes (canonical view of this window).
        rotated = rotate_bytes(window, r)
        for b in rotated:
            cumfreqs, total = _cumfreqs_from_predictor(pred, 256)
            enc.encode(cumfreqs, b, total)
            pred.update(chr(b))
        # 3: observe rotation choice + chain symbol (substrate-native
        # workspace observation; D8 of the chain-Sequitur arc).
        seq_rot.observe(r)
        chain_seq.observe(ChainSymbol.from_s4(walk_to_s4(rotated).state))
    encoded = enc.finish()
    stats = {
        "encoded_bytes": len(encoded),
        "rotation_counts": rotation_counter,
        "n_windows": sum(rotation_counter),
        "seq_rot_n_rules": seq_rot.n_rules(),
        "chain_seq_n_rules": chain_seq.n_rules(),
        "categorical_type": "DirectProduct(FreeCyclic_canonical, Z_16_rotations)",
    }
    return encoded, stats


def decode(encoded: bytes, n_bytes: int, window_size: int = 256) -> bytes:
    """Decode `encoded` back to the original bytes. Single canonical
    predictor in lockstep with the encoder."""
    pred = TrigramPredictor(vocab_size=256)
    seq_rot = Sequitur()
    dec = RangeDecoder(encoded)

    rot_cumfreqs = list(range(ROT_TAG_TOTAL + 1))

    out = bytearray()
    n_full = n_bytes // window_size
    leftover = n_bytes - n_full * window_size

    for window_idx in range(n_full + (1 if leftover else 0)):
        # 1: decode rotation tag.
        r = dec.decode(rot_cumfreqs, ROT_TAG_TOTAL)
        # 2: decode canonical-view bytes via the single predictor.
        n_in_window = window_size if window_idx < n_full else leftover
        rotated = bytearray()
        for _ in range(n_in_window):
            cumfreqs, total = _cumfreqs_from_predictor(pred, 256)
            b = dec.decode(cumfreqs, total)
            rotated.append(b)
            pred.update(chr(b))
        # 3: apply inverse rotation to recover original bytes.
        unrotated = rotate_bytes(bytes(rotated), r)
        out.extend(unrotated)
        # 4: observe rotation choice.
        seq_rot.observe(r)
    return bytes(out)
