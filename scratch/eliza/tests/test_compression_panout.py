"""tests/test_compression_panout.py — head-to-head compression measurements.

E5: gt baseline (dim2_codec.encode with default chooser)
E6: hybrid codec (chain stream + byte stream, no rotation)
E7: chain stream alone (just the W-axis content, no bytes)
E8: byte stream alone (just bytes, no chain) — baseline trigram
E9: chain stream via multi-level grammar (replace ChainTrigram with
    MultiLevelChainSequitur-based encoding — see E9 caveats below)

Three corpora: text (engine.py repeated), elf (/bin/true), zeros.
Three sizes: 4KB, 16KB, 64KB.

Honest accounting:
  * The chain stream is computable from bytes, so encoding it
    separately is REDUNDANT — bits paid without saving.
  * The hybrid codec measures "chain layer's standalone cost," not a
    competitive codec.
  * The interest is in the structural finding: how much does the W-axis
    stream cost, and how does it compare to byte cost?
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from typing import Tuple

from eliza.arith import RangeDecoder, RangeEncoder
from eliza.chain_emitter import chain_stream as chain_stream_fn, emit_chain_for_window
from eliza.chain_trigram import ChainTrigramPredictor
from eliza.chain_conditioned_byte import (
    BaselineBytePredictor, ChainConditionedBytePredictor,
    V4ConditionedBytePredictor,
)
from eliza.dim2_codec import encode as dim2_encode, decode as dim2_decode
from eliza.hybrid_codec import (
    encode as hybrid_encode, decode as hybrid_decode,
    _chain_cumfreqs, _CHAIN_BY_INDEX, _INDEX_BY_CHAIN,
)
from eliza.multilevel_chain_sequitur import MultiLevelChainSequitur


# --- Corpora -----------------------------------------------------------


def _text_bytes(n: int) -> bytes:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < n:
        data = data + data
    return data[:n]


def _elf_bytes(n: int) -> bytes:
    with open("/bin/true", "rb") as f:
        return f.read(n)


def _zeros_bytes(n: int) -> bytes:
    return b"\x00" * n


CORPORA = {"text": _text_bytes, "elf": _elf_bytes, "zeros": _zeros_bytes}
SIZES = (4096, 16384, 65536)


# --- E5: gt baseline ----------------------------------------------------


def measure_gt(data: bytes) -> Tuple[float, int]:
    enc, _ = dim2_encode(data)
    return 8 * len(enc) / len(data), len(enc)


# --- E6: hybrid codec --------------------------------------------------


def measure_hybrid(data: bytes) -> Tuple[float, int, dict]:
    enc, stats = hybrid_encode(data)
    return 8 * len(enc) / len(data), len(enc), stats


# --- E7: chain-stream alone --------------------------------------------


def measure_chain_only(data: bytes, window_size: int = 256) -> float:
    """Encode just the chain stream via chain trigram. Returns total
    bits / number of bytes — the chain-stream's cost normalised by
    the data size."""
    chains = chain_stream_fn(data, window_size=window_size)
    pred = ChainTrigramPredictor()
    enc = RangeEncoder()
    for c in chains:
        cf, total = _chain_cumfreqs(pred)
        idx = _INDEX_BY_CHAIN[c]
        enc.encode(cf, idx, total)
        pred.update(c)
    encoded = enc.finish()
    return 8 * len(encoded) / len(data)


# --- E8: byte-stream alone via baseline trigram ------------------------


def measure_byte_only(data: bytes) -> float:
    """Baseline byte trigram (no rotation, no chain). The same predictor
    as gt's `_choose_rotation_canonical` underlying model, run on the
    unrotated bytes."""
    pred = BaselineBytePredictor()
    enc = RangeEncoder()
    SCALE = 1024
    for b in data:
        # Build cumfreqs from predictor.
        freqs = [max(1, int(round(pred.smoothed_prob(x) * SCALE))) for x in range(256)]
        cumfreqs = [0]
        s = 0
        for f in freqs:
            s += f
            cumfreqs.append(s)
        enc.encode(cumfreqs, b, s)
        pred.update(b)
    encoded = enc.finish()
    return 8 * len(encoded) / len(data)


# --- E8b: chain-conditioned byte streams (raw bits, no AC overhead) ---


def measure_byte_with_chain_context(data: bytes, window_size: int = 256
                                     ) -> Tuple[float, float]:
    """Byte trigram + (full chain | V₄-only chain) context.

    Returns (bits_per_byte_full_chain, bits_per_byte_v4_only). No AC
    encode — just model entropy proxy.
    """
    full = ChainConditionedBytePredictor()
    v4 = V4ConditionedBytePredictor()
    total_full = 0.0
    total_v4 = 0.0
    counted = 0
    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        if not window:
            break
        c = emit_chain_for_window(window)
        full.set_chain(c)
        v4.set_chain(c)
        for b in window:
            total_full += full.surprise_bits(b)
            total_v4 += v4.surprise_bits(b)
            full.update(b)
            v4.update(b)
            counted += 1
    return total_full / counted, total_v4 / counted


# --- E9: chain stream via multi-level grammar -------------------------


def measure_chain_via_grammar(data: bytes, window_size: int = 256,
                              max_levels: int = 6) -> Tuple[float, dict]:
    """Encode chain stream by encoding only the FINAL level's stream +
    a description of the rule tables.

    This is a lower-bound proxy: bits = entropy(final-level stream) +
    Σ rules-cost-at-each-level. We use raw model entropy + a fixed
    cost per rule (32 bits ≈ rule_id pointer + 2 chain-symbol IDs at
    the rule's body).
    """
    chains = chain_stream_fn(data, window_size=window_size)
    ml = MultiLevelChainSequitur.from_stream(chains, max_levels=max_levels)
    # Final-level stream entropy.
    final_stream = ml.levels[-1].input_stream
    from collections import Counter
    counts = Counter(final_stream)
    n = sum(counts.values())
    H = 0.0
    for c in counts.values():
        p = c / n
        H -= p * math.log2(p)
    final_bits = H * len(final_stream)
    # Rule cost: 2 symbols × 5 bits per rule (a rough proxy).
    total_rule_cost = 0
    for lv in ml.levels:
        total_rule_cost += lv.n_rules() * 2 * 5
    total_bits = final_bits + total_rule_cost
    info = {
        "n_levels": len(ml.levels),
        "final_stream_len": len(final_stream),
        "final_entropy_bits_per_sym": H,
        "final_stream_total_bits": final_bits,
        "rule_cost_bits": total_rule_cost,
        "total_bits": total_bits,
    }
    return total_bits / len(data), info


# --- Main ---------------------------------------------------------------


def main():
    print("=== Compression measurement panout ===\n")
    print(f"Across corpora ∈ {list(CORPORA.keys())} at sizes {SIZES}")
    print(f"All numbers in BITS-PER-INPUT-BYTE.\n")

    # Compact table per (corpus, size).
    for size in SIZES:
        print(f"--- {size}B inputs ---")
        print(f"{'corpus':>8}  {'gt-baseline':>12}  {'hybrid':>8}"
              f"  {'chain-only':>11}  {'byte-only':>10}"
              f"  {'+v4-cond':>9}  {'+chain-cond':>11}  {'ml-grammar':>11}")
        for name, factory in CORPORA.items():
            data = factory(size)
            bpb_gt, _ = measure_gt(data)
            bpb_hybrid, _, _ = measure_hybrid(data)
            bpb_chain = measure_chain_only(data)
            bpb_byte = measure_byte_only(data)
            bpb_full, bpb_v4 = measure_byte_with_chain_context(data)
            bpb_grammar, _ = measure_chain_via_grammar(data)
            print(f"{name:>8}  {bpb_gt:>12.3f}  {bpb_hybrid:>8.3f}"
                  f"  {bpb_chain:>11.3f}  {bpb_byte:>10.3f}"
                  f"  {bpb_v4:>9.3f}  {bpb_full:>11.3f}  {bpb_grammar:>11.3f}")
        print()

    print("Reading:")
    print(" - gt-baseline: existing codec (rotation + byte trigram)")
    print(" - hybrid: chain trigram + byte trigram (no rotation)")
    print(" - chain-only: just the W-axis stream cost, normalised by input size")
    print(" - byte-only: byte trigram alone (no chain, no rotation)")
    print(" - +v4-cond: byte trigram conditioned on V₄ component of window's chain")
    print(" - +chain-cond: byte trigram conditioned on full chain (24-element)")
    print(" - ml-grammar: chain stream via multi-level grammar (proxy bits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
