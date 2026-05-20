"""Eliza.Codec — gt + arithmetic coding = real lossless codec.

Wraps the TrigramPredictor in a range coder so the input stream is
encoded to bytes and decoded back to the same bytes. The encoder
and decoder both maintain an identical TrigramPredictor that updates
in lockstep with each emission.

For binary input (vocab=256) this is the canonical baseline: Markov-3
adaptive arithmetic coding. Sequitur rule extensions are out of scope
for this module; they live on top of this primitive.
"""

from __future__ import annotations

from typing import List, Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.predictor import TrigramPredictor


def _cumfreqs_from_predictor(
    pred: TrigramPredictor,
    vocab_size: int,
    resolution: int = 1 << 20,
) -> Tuple[List[int], int]:
    """Build a cumulative-frequency table over the full vocab from the
    predictor's current (c1, c2) context. Smooth with the predictor's
    alpha. `resolution` is the integer-precision the AC operates at;
    cumfreqs are integers ∈ [0, resolution]."""
    c1, c2 = pred.context
    # Compute per-symbol weighted prob, then scale to integers.
    inner = pred.counts.get((c1, c2), {})
    total_count = sum(inner.values())
    alpha = pred.alpha
    denom = total_count + alpha * vocab_size
    # Build integer cumfreqs. Floor each, then add 1 to ensure non-zero.
    cumfreqs = [0]
    acc = 0
    for i in range(vocab_size):
        ch = chr(i)
        p = (inner.get(ch, 0) + alpha) / denom
        # +1 ensures each symbol has at least 1 freq for AC validity.
        freq = max(1, int(p * (resolution - vocab_size)))
        acc += freq
        cumfreqs.append(acc)
    return cumfreqs, acc


def encode(data: bytes, vocab_size: int = 256) -> bytes:
    """Encode a byte stream via Markov-3 adaptive AC."""
    pred = TrigramPredictor(vocab_size=vocab_size)
    enc = RangeEncoder()
    for byte in data:
        cumfreqs, total = _cumfreqs_from_predictor(pred, vocab_size)
        enc.encode(cumfreqs, byte, total)
        pred.update(chr(byte))
    return enc.finish()


def decode(encoded: bytes, n_symbols: int, vocab_size: int = 256) -> bytes:
    """Decode a byte stream encoded by `encode`. Caller must supply the
    original length `n_symbols` (we don't frame it for simplicity)."""
    pred = TrigramPredictor(vocab_size=vocab_size)
    dec = RangeDecoder(encoded)
    out = bytearray()
    for _ in range(n_symbols):
        cumfreqs, total = _cumfreqs_from_predictor(pred, vocab_size)
        idx = dec.decode(cumfreqs, total)
        out.append(idx)
        pred.update(chr(idx))
    return bytes(out)


def encode_crumbs(crumbs, vocab_size: int = 4) -> bytes:
    """Markov-3 adaptive AC over a crumb sequence. Each crumb ∈ [0,4)."""
    pred = TrigramPredictor(vocab_size=vocab_size)
    enc = RangeEncoder()
    for c in crumbs:
        cumfreqs, total = _cumfreqs_from_predictor(pred, vocab_size)
        enc.encode(cumfreqs, c, total)
        pred.update(chr(c))
    return enc.finish()


def decode_crumbs(encoded: bytes, n_crumbs: int, vocab_size: int = 4):
    """Inverse of encode_crumbs."""
    pred = TrigramPredictor(vocab_size=vocab_size)
    dec = RangeDecoder(encoded)
    out = []
    for _ in range(n_crumbs):
        cumfreqs, total = _cumfreqs_from_predictor(pred, vocab_size)
        idx = dec.decode(cumfreqs, total)
        out.append(idx)
        pred.update(chr(idx))
    return out


def bits_to_crumbs(data: bytes):
    """Sliding-stride-1 crumbs over the bit stream of `data`. Each crumb
    is an int ∈ [0,4), encoding (prev_bit, new_bit) MSB-first. Yields
    8N-1 crumbs for N input bytes."""
    prev = None
    for byte in data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            if prev is not None:
                yield (prev << 1) | bit
            prev = bit
