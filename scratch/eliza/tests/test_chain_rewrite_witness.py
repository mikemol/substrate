"""tests/test_chain_rewrite_witness.py — rewrite-step propagates to bytes.

The user's substrate-native claim: "Sequitur's rewrite step can apply
to the input that was used to construct the walk chain."

This test substantiates that claim concretely. For each Sequitur rule
R created over chain symbols:

  (R1) Every chain-stream occurrence of R's terminal closure corresponds
       to a CONTIGUOUS SPAN of byte-windows in the original input.

  (R2) For each such span, the SEQUENCE of per-window chains over that
       span equals R's terminal closure exactly (definition; algebraic
       cross-check).

  (R3) The PRODUCT of those window-chains equals R's lifted symbol
       (= the chain product of R's terminal closure). Bridge round-trip.

  (R4) For the chain-byte-bridge canonical representative b_R:
       bridge_chain_to_bytes(R.lifted) folds to R.lifted.to_s4(). This
       is the substrate-honest "byte pattern for R" deliverable —
       a substrate-native witness that R can be expanded back into a
       fold-equivalent byte sequence.

Together (R1)–(R4) witness: rule occurrences at the chain level ARE
contiguous byte-window patterns, and the rule has a bridge representative
at the byte level. The grammar is substrate-native because the rules
themselves are workspace-axis objects.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from typing import List, Tuple

from eliza.chain_bytes_bridge import bridge_chain_to_bytes
from eliza.chain_emitter import chain_stream, emit_chain_for_window
from eliza.chain_sequitur import ChainSequitur, RuleLift
from eliza.chain_symbol import ChainSymbol, product as chain_product
from eliza.walk_carrier import walk_to_s4


def find_occurrences(stream: List[ChainSymbol],
                     pattern: List[ChainSymbol]) -> List[int]:
    """Indices i where stream[i:i+len(pattern)] == pattern."""
    n, m = len(stream), len(pattern)
    out = []
    for i in range(n - m + 1):
        if stream[i:i + m] == pattern:
            out.append(i)
    return out


def witness_rule_occurrences(
    data: bytes, lifts: List[RuleLift], stream: List[ChainSymbol],
    window_size: int = 256, skip_top_rule_id: int = 0,
) -> dict:
    """For each non-start rule, find its chain-stream occurrences and
    verify (R2) and (R3) at every occurrence."""
    r2_failures: List[Tuple[int, int]] = []   # (rule_id, occurrence_index)
    r3_failures: List[Tuple[int, int]] = []
    n_per_rule = {}
    for lift in lifts:
        if lift.rule_id == skip_top_rule_id:
            continue
        pattern = lift.terminal_closure
        if not pattern:
            continue
        occurrences = find_occurrences(stream, pattern)
        n_per_rule[lift.rule_id] = len(occurrences)
        for occ in occurrences:
            # R2: the chain-stream span equals the terminal closure
            # (definition; we already used this to find occurrences,
            # but cross-check via window slices).
            byte_span = data[occ * window_size:(occ + len(pattern)) * window_size]
            window_chains = [
                emit_chain_for_window(byte_span[i * window_size:(i + 1) * window_size])
                for i in range(len(pattern))
            ]
            if window_chains != list(pattern):
                r2_failures.append((lift.rule_id, occ))
            # R3: product of window chains equals lifted symbol.
            recomputed_lift = chain_product(window_chains)
            if recomputed_lift != lift.lifted:
                r3_failures.append((lift.rule_id, occ))
    return {
        "rule_occurrences": n_per_rule,
        "R2_failures": r2_failures,
        "R3_failures": r3_failures,
    }


def witness_bridge_representatives(lifts: List[RuleLift]) -> dict:
    """R4: each rule's bridge representative folds back to the rule's
    lifted symbol's S₄ element."""
    failures: List[int] = []
    for lift in lifts:
        if not lift.terminal_closure:
            continue
        bytes_for_rule = bridge_chain_to_bytes(lift.lifted)
        carrier = walk_to_s4(bytes_for_rule)
        if carrier.state != lift.lifted.to_s4():
            failures.append(lift.rule_id)
    return {"failures": failures}


def main(data_size: int = 65536, window_size: int = 256) -> int:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < data_size:
        data = data + data
    data = data[:data_size]

    stream = chain_stream(data, window_size=window_size)
    cs = ChainSequitur()
    cs.observe_stream(stream)
    lifts = list(cs.all_lifts().values())

    print("=== Chain rewrite-step witness ===\n")
    print(f"Input: {data_size} bytes; window size {window_size}; "
          f"{len(stream)} chain symbols")
    print(f"Rules inferred: {cs.n_rules()}\n")

    occ_report = witness_rule_occurrences(
        data, lifts, stream, window_size=window_size,
    )
    bridge_report = witness_bridge_representatives(lifts)

    print("(R1+R2+R3) Each rule's occurrences in the chain stream "
          "correspond to contiguous byte-window spans whose chains")
    print("compose to the rule's lifted symbol:")
    print(f"  rule occurrence counts: {occ_report['rule_occurrences']}")
    print(f"  R2 failures (chain mismatch):    {len(occ_report['R2_failures'])}")
    print(f"  R3 failures (lift mismatch):     {len(occ_report['R3_failures'])}")
    print()
    print("(R4) Each rule has a representative byte sequence that "
          "folds back to its lifted symbol:")
    print(f"  bridge failures: {len(bridge_report['failures'])} / "
          f"{sum(1 for l in lifts if l.terminal_closure)} non-empty rules")
    print()
    all_ok = (not occ_report["R2_failures"] and
              not occ_report["R3_failures"] and
              not bridge_report["failures"])
    print(f"Result: {'OK' if all_ok else 'FAILURE'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
