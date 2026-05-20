"""tests/test_chain_grammar_compression.py — per-level diagnostic.

Measurement, not a gate. For each level of the recursive grammar:
  * stream length (input size)
  * empirical entropy (in bits) of the symbol distribution
  * number of rules
  * mean rule's terminal-closure length
  * effective bits-per-symbol given the empirical entropy

Per [[reject-lem-in-substrate]]: emit measurements as facts, not as
pass/fail. Compression DELTA per level is the interesting quantity —
it tells us how much structure each successive grammar level extracts.
"""

from __future__ import annotations

import sys
from math import log2
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.chain_emitter import chain_stream
from eliza.multilevel_chain_sequitur import MultiLevelChainSequitur


def empirical_entropy(stream) -> float:
    counts = Counter(stream)
    n = sum(counts.values())
    if n == 0:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c / n
        H -= p * log2(p)
    return H


def level_diagnostic(level, n_symbols_alphabet: int) -> dict:
    H = empirical_entropy(level.input_stream)
    # Max entropy log₂(|alphabet|).
    H_max = log2(n_symbols_alphabet) if n_symbols_alphabet > 0 else 0.0
    rule_lengths = [len(lift.terminal_closure) for lift in level.lifts.values()]
    mean_rule_len = (sum(rule_lengths) / len(rule_lengths)
                     if rule_lengths else 0.0)
    return {
        "level": level.index,
        "stream_length": len(level.input_stream),
        "distinct_symbols": len(set(level.input_stream)),
        "alphabet_max_size": n_symbols_alphabet,
        "empirical_entropy_bits": H,
        "max_entropy_bits": H_max,
        "redundancy": H_max - H,
        "n_rules": level.n_rules(),
        "mean_rule_closure_length": mean_rule_len,
        "total_bits_at_this_level": H * len(level.input_stream),
    }


def main(data_size: int = 65536, window_size: int = 256,
         max_levels: int = 6) -> int:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < data_size:
        data = data + data
    data = data[:data_size]

    stream = chain_stream(data, window_size=window_size)
    ml = MultiLevelChainSequitur.from_stream(stream, max_levels=max_levels)

    # Alphabet size: ChainSymbol carries |S₄| = 24 distinct values at
    # level 0. After lifting, each new lifted symbol is ALSO a
    # ChainSymbol (one of 24), but in PRACTICE the alphabet observed at
    # level i is bounded by 24 because the lift folds back into S₄.
    n_symbols = 24

    print("=== Per-level chain-grammar compression diagnostic ===\n")
    print(f"Input bytes: {len(data)}")
    print(f"Window size: {window_size}")
    print(f"Initial stream: {len(stream)} chain symbols\n")

    print(f"{'Lvl':<4}{'|stream|':>9}{'distinct':>10}{'H/sym':>9}"
          f"{'redund':>9}{'rules':>7}{'avg|R|':>9}{'tot bits':>11}")
    print("-" * 67)
    for lv in ml.levels:
        d = level_diagnostic(lv, n_symbols)
        print(f"L{d['level']:<3}{d['stream_length']:>9}"
              f"{d['distinct_symbols']:>10}"
              f"{d['empirical_entropy_bits']:>9.3f}"
              f"{d['redundancy']:>9.3f}"
              f"{d['n_rules']:>7}"
              f"{d['mean_rule_closure_length']:>9.2f}"
              f"{d['total_bits_at_this_level']:>11.1f}")

    # Deltas across levels.
    print("\nCompression delta (Δ total-bits across levels):")
    bits = [level_diagnostic(lv, n_symbols)["total_bits_at_this_level"]
            for lv in ml.levels]
    for i in range(1, len(bits)):
        delta = bits[i] - bits[i-1]
        pct = 100 * delta / bits[i-1] if bits[i-1] > 0 else 0.0
        print(f"  L{i-1} → L{i}: {delta:+.1f} bits ({pct:+.1f}%)")

    # As fraction of raw byte count (sanity check).
    raw_bits = len(data) * 8
    final_bits = bits[-1] if bits else 0.0
    print(f"\nRaw input:        {raw_bits} bits ({len(data)} bytes)")
    print(f"Final L{len(bits)-1} bits: {final_bits:.1f}  "
          f"(ratio {final_bits / raw_bits:.4f}) — chain-grammar only,")
    print(f"  does NOT include the substrate cost of describing the rules.")
    print()
    print("Reading: this is the chain-grammar's compressive content "
          "(rule-induced entropy reduction). The codec's gt cost remains "
          "the operational bitstream measure; chain-grammar's value is "
          "structural (recursive substrate-grammar inference), not raw "
          "compression.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
