"""Eliza.LosslessChainCodec — encode bytes as a per-nibble chain stream.

Per Door 2 of the chain-compression design: emit one ChainSymbol per
nibble, arithmetic-coded under an adaptive chain trigram. Decode by
inverting (chamber_before, chamber_after) → nibble at every step.

The codec output is EXCLUSIVELY chain information (no raw bytes); the
decoder reconstructs bytes byte-for-byte via the inverse lookup.

A key optimisation: at each step only 16 of the 24 chambers are
REACHABLE in one nibble-transition from the current chamber. We
restrict the predictor's probability mass to the reachable set when
encoding/decoding — this is a substrate-honest information narrowing
that strictly bounds the per-step entropy at ≤ log₂(16) = 4 bits,
matching the per-nibble bound.
"""

from __future__ import annotations

from typing import List, Tuple

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_symbol import ChainSymbol
from eliza.chain_trigram import ChainTrigramPredictor
from eliza.manifold import Manifold
from eliza.per_nibble_chain import (
    nibble_from_transition, nibbles_to_bytes, per_nibble_chain_stream,
)


# Stable global ordering of the 24 ChainSymbols (must match between
# encoder and decoder).
_MANIFOLD = Manifold()
_S4_ELEMENTS = list(_MANIFOLD.nodes)
_CHAIN_BY_INDEX = [ChainSymbol.from_s4(g) for g in _S4_ELEMENTS]
_INDEX_BY_CHAIN = {c: i for i, c in enumerate(_CHAIN_BY_INDEX)}


def _reachable_chains_from(state: Chamber) -> List[ChainSymbol]:
    """The 16 chain symbols reachable from `state` in one nibble step.
    Returned in nibble order (n=0..15) so the encoder and decoder agree."""
    return [ChainSymbol.from_s4(perm_compose(state, NIBBLE_TO_PERM[n]))
            for n in range(16)]


def _restricted_cumfreqs(
    pred: ChainTrigramPredictor, reachable: List[ChainSymbol],
) -> Tuple[List[int], int]:
    """Cumulative frequencies over the 16 reachable chains only.

    Restricting to reachable chambers is the substrate-honest narrowing:
    we know the next chain MUST be one of these 16, so probability mass
    on the other 8 is wasted bits.
    """
    SCALE = 1024
    freqs = []
    for c in reachable:
        p = pred.smoothed_prob(c)
        freqs.append(max(1, int(round(p * SCALE))))
    cumfreqs = [0]
    s = 0
    for f in freqs:
        s += f
        cumfreqs.append(s)
    return cumfreqs, s


def encode(data: bytes) -> Tuple[bytes, dict]:
    """Encode `data` as a per-nibble chain stream via adaptive trigram +
    arithmetic coding. Output contains ONLY chain information."""
    pred = ChainTrigramPredictor()
    enc = RangeEncoder()
    state = ORIGIN
    n_bits_proxy = 0.0

    from math import log2

    nibbles = 0
    for byte in data:
        for shift in (4, 0):
            n = (byte >> shift) & 0xF
            new_state = perm_compose(state, NIBBLE_TO_PERM[n])
            new_chain = ChainSymbol.from_s4(new_state)
            reachable = _reachable_chains_from(state)
            cumfreqs, total = _restricted_cumfreqs(pred, reachable)
            # Index of new_chain within reachable list = the nibble itself.
            local_idx = n
            enc.encode(cumfreqs, local_idx, total)
            # Proxy bits via the chosen mass / total.
            mass = cumfreqs[local_idx + 1] - cumfreqs[local_idx]
            n_bits_proxy += -log2(mass / total)
            pred.update(new_chain)
            state = new_state
            nibbles += 1

    encoded = enc.finish()
    return encoded, {
        "encoded_bytes": len(encoded),
        "n_nibbles": nibbles,
        "n_bytes": len(data),
        "model_total_bits": n_bits_proxy,
        "model_bits_per_byte": n_bits_proxy / len(data) if len(data) else 0.0,
    }


def decode(encoded: bytes, n_bytes: int) -> bytes:
    """Reverse of encode: arithmetic-decode chain stream, invert each
    transition to its producing nibble, pair into bytes."""
    pred = ChainTrigramPredictor()
    dec = RangeDecoder(encoded)
    state = ORIGIN
    nibbles: List[int] = []
    for _ in range(2 * n_bytes):
        reachable = _reachable_chains_from(state)
        cumfreqs, total = _restricted_cumfreqs(pred, reachable)
        local_idx = dec.decode(cumfreqs, total)
        n = local_idx     # by construction the local index IS the nibble
        new_chain = reachable[local_idx]
        new_state = new_chain.to_s4()
        # Sanity: invert and confirm consistency.
        inv_nibble = nibble_from_transition(state, new_state)
        if inv_nibble != n:
            raise ValueError(
                f"decoder inconsistency at nibble #{len(nibbles)}: "
                f"local_idx={n} but inverse-lookup says {inv_nibble}"
            )
        nibbles.append(n)
        pred.update(new_chain)
        state = new_state
    return nibbles_to_bytes(nibbles)


# --- Self-check: round-trip + measurement ------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:4096]

    encoded, stats = encode(data)
    decoded = decode(encoded, len(data))
    ok = decoded == data

    if verbose:
        print("=== LosslessChainCodec self-check ===")
        print(f"  input:                {len(data)} bytes")
        print(f"  encoded:              {len(encoded)} bytes "
              f"({8 * len(encoded) / len(data):.3f} b/byte)")
        print(f"  round-trip:           {'OK' if ok else 'FAIL'}")
        print(f"  model proxy bits:     {stats['model_total_bits']:.1f}  "
              f"({stats['model_bits_per_byte']:.3f} b/byte)")
        print(f"  n_nibbles encoded:    {stats['n_nibbles']}")
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
