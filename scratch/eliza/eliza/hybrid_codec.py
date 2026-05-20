"""Eliza.HybridCodec — two-stream codec: chain-trigram + byte-trigram.

For each window of input bytes:
  1. Compute the chain symbol of the rotated window (rotation chooser
     plug-in same as dim2_codec).
  2. Encode the chain symbol via ChainTrigramPredictor.
  3. Encode the byte sequence via a plain byte trigram predictor
     (NOT chain-conditioned, because E2 showed conditioning hurts
     at standard granularity).

The chain stream is encoded ADJACENT to the byte stream, both into
one arithmetic-coded output. The decoder reverses by decoding the
chain symbol then the bytes per window.

This codec gives an honest measurement of the chain layer's COST: how
many bits the chain stream adds. The chain layer doesn't help byte
compression here, but it's part of the W-axis substrate content.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_emitter import emit_chain_for_window
from eliza.chain_symbol import ChainSymbol
from eliza.chain_trigram import ChainTrigramPredictor, VOCAB_SIZE as N_CHAIN
from eliza.chain_conditioned_byte import BaselineBytePredictor
from eliza.manifold import Manifold


# Enumerate the 24 chain symbols once for the codec's bijection.
_MANIFOLD = Manifold()
_S4_ELEMENTS = list(_MANIFOLD.nodes)
_CHAIN_BY_INDEX = [ChainSymbol.from_s4(g) for g in _S4_ELEMENTS]
_INDEX_BY_CHAIN = {c: i for i, c in enumerate(_CHAIN_BY_INDEX)}


def _chain_cumfreqs(pred: ChainTrigramPredictor) -> Tuple[list, int]:
    """Convert predictor's smoothed distribution over chain symbols
    into cumulative frequencies for the arithmetic coder.
    """
    SCALE = 1024
    freqs = []
    for c in _CHAIN_BY_INDEX:
        p = pred.smoothed_prob(c)
        freqs.append(max(1, int(round(p * SCALE))))
    cumfreqs = [0]
    s = 0
    for f in freqs:
        s += f
        cumfreqs.append(s)
    return cumfreqs, s


def _byte_cumfreqs(pred: BaselineBytePredictor) -> Tuple[list, int]:
    SCALE = 1024
    freqs = []
    for b in range(256):
        p = pred.smoothed_prob(b)
        freqs.append(max(1, int(round(p * SCALE))))
    cumfreqs = [0]
    s = 0
    for f in freqs:
        s += f
        cumfreqs.append(s)
    return cumfreqs, s


def encode(data: bytes, window_size: int = 256) -> Tuple[bytes, dict]:
    """Encode data via hybrid chain + byte streams.

    No rotation in this codec — focus is on isolating the chain
    contribution. Comparison to gt baseline (which DOES use rotation)
    in E6.
    """
    chain_pred = ChainTrigramPredictor()
    byte_pred = BaselineBytePredictor()
    enc = RangeEncoder()
    n_chain_bits_proxy = 0.0
    n_byte_bits_proxy = 0.0

    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        if not window:
            break
        chain = emit_chain_for_window(window)
        # Encode chain.
        cumfreqs, total = _chain_cumfreqs(chain_pred)
        idx = _INDEX_BY_CHAIN[chain]
        enc.encode(cumfreqs, idx, total)
        n_chain_bits_proxy += -__import__("math").log2(max(chain_pred.smoothed_prob(chain), 1e-30))
        chain_pred.update(chain)
        # Encode bytes.
        for b in window:
            cf, t = _byte_cumfreqs(byte_pred)
            enc.encode(cf, b, t)
            n_byte_bits_proxy += -__import__("math").log2(max(byte_pred.smoothed_prob(b), 1e-30))
            byte_pred.update(b)

    encoded = enc.finish()
    stats = {
        "encoded_bytes": len(encoded),
        "n_windows": (len(data) + window_size - 1) // window_size,
        "n_bytes": len(data),
        "model_chain_bits": n_chain_bits_proxy,
        "model_byte_bits": n_byte_bits_proxy,
        "model_total_bits": n_chain_bits_proxy + n_byte_bits_proxy,
        "window_size": window_size,
    }
    return encoded, stats


def decode(encoded: bytes, n_bytes: int, window_size: int = 256) -> bytes:
    """Reverse of encode. The decoder maintains the same predictor
    states by replaying the same observations in lockstep.

    Decoded chain at each window is verified consistent with the
    decoded bytes' actual chain (an algebraic round-trip check; if
    they disagree the encoder/decoder are mis-synced).
    """
    chain_pred = ChainTrigramPredictor()
    byte_pred = BaselineBytePredictor()
    dec = RangeDecoder(encoded)

    out = bytearray()
    n_windows = (n_bytes + window_size - 1) // window_size
    for w in range(n_windows):
        # Decode chain.
        cumfreqs, total = _chain_cumfreqs(chain_pred)
        idx = dec.decode(cumfreqs, total)
        decoded_chain = _CHAIN_BY_INDEX[idx]
        chain_pred.update(decoded_chain)
        # Decode bytes for this window.
        remaining = n_bytes - len(out)
        this_size = min(window_size, remaining)
        decoded_bytes = bytearray()
        for _ in range(this_size):
            cf, t = _byte_cumfreqs(byte_pred)
            b = dec.decode(cf, t)
            decoded_bytes.append(b)
            byte_pred.update(b)
        # Sanity: the decoded bytes' chain must match the decoded chain.
        actual_chain = emit_chain_for_window(bytes(decoded_bytes))
        if actual_chain != decoded_chain:
            raise ValueError(
                f"window {w}: decoded chain {decoded_chain} != "
                f"bytes-actual chain {actual_chain}")
        out.extend(decoded_bytes)
    return bytes(out)


# --- Self-check: round-trip ---------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:8192]

    encoded, stats = encode(data)
    decoded = decode(encoded, len(data))
    ok = decoded == data

    if verbose:
        print("=== HybridCodec self-check ===")
        print(f"  input:                {len(data)} bytes")
        print(f"  encoded:              {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  round-trip:           {'OK' if ok else 'FAIL'}")
        print(f"  model chain bits:     {stats['model_chain_bits']:.1f}")
        print(f"  model byte bits:      {stats['model_byte_bits']:.1f}")
        print(f"  model total bits:     {stats['model_total_bits']:.1f}  "
              f"({stats['model_total_bits'] / len(data):.3f} b/byte)")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
