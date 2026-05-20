"""tests/test_recursive_grammar_witness.py — substrate-honest gates for
the recursive chain-grammar inference.

Three algebraic properties that must hold at every level:

  (W1) Lift consistency: lift(rule).lifted = product(lift.terminal_closure)
       at every rule of every level.

  (W2) Chain-product preservation across rewrite: for every level i,
       product(level_i.input_stream) = product(level_{i+1}.input_stream).
       This is the substrate's [[homology-cohomology-recursion]]
       discipline at runtime: the catalogued grammar preserves the
       observed group element.

  (W3) Contraction: |level_{i+1}.input_stream| ≤ |level_i.input_stream|.
       The rewriting reduces the stream length (or terminates the
       recursion if no reduction is possible).

No gt involvement; no compression-rate gate; pure algebraic witness.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.chain_emitter import chain_stream
from eliza.chain_symbol import ChainSymbol, product as chain_product
from eliza.multilevel_chain_sequitur import MultiLevelChainSequitur


def witness_lift_consistency(ml: MultiLevelChainSequitur) -> dict:
    """W1: every rule's lifted symbol equals product(terminal_closure)."""
    failures = []
    for lv in ml.levels:
        for rid, lift in lv.lifts.items():
            recomputed = chain_product(lift.terminal_closure)
            if recomputed != lift.lifted:
                failures.append((lv.index, rid, lift.lifted, recomputed))
    return {"failures": failures, "ok": len(failures) == 0}


def witness_product_preservation(ml: MultiLevelChainSequitur) -> dict:
    """W2: product of input_stream is invariant across rewriting.

    The level-i+1 input is the level-i stream with rule occurrences
    replaced by lifted symbols. Since each lifted symbol's chain
    EQUALS the product of its terminal closure, the overall stream
    product is preserved.
    """
    products = [chain_product(lv.input_stream) for lv in ml.levels]
    all_equal = all(p == products[0] for p in products)
    return {"products": products, "all_equal": all_equal}


def witness_contraction(ml: MultiLevelChainSequitur) -> dict:
    """W3: stream length is monotonically non-increasing."""
    lengths = [len(lv.input_stream) for lv in ml.levels]
    violations = [(i, lengths[i], lengths[i+1])
                  for i in range(len(lengths) - 1)
                  if lengths[i+1] > lengths[i]]
    return {"lengths": lengths, "violations": violations,
            "ok": len(violations) == 0}


def run_witnesses(data_size: int = 65536, window_size: int = 256,
                  max_levels: int = 6) -> dict:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < data_size:
        data = data + data
    data = data[:data_size]

    stream = chain_stream(data, window_size=window_size)
    ml = MultiLevelChainSequitur.from_stream(stream, max_levels=max_levels)

    w1 = witness_lift_consistency(ml)
    w2 = witness_product_preservation(ml)
    w3 = witness_contraction(ml)
    all_ok = w1["ok"] and w2["all_equal"] and w3["ok"]
    return {
        "n_levels": len(ml.levels),
        "level_stats": ml.all_stats(),
        "W1_lift_consistency": w1,
        "W2_product_preservation": w2,
        "W3_contraction": w3,
        "all_ok": all_ok,
    }


def main() -> int:
    print("=== Recursive grammar witness ===\n")
    r = run_witnesses()
    print(f"Levels traversed: {r['n_levels']}\n")
    print("Per-level stats:")
    for s in r["level_stats"]:
        print(f"  L{s['level']}: |stream|={s['input_length']:>5}, "
              f"distinct={s['distinct_symbols']:>3}, "
              f"n_rules={s['n_rules']}")
    print()
    print("(W1) Lift consistency:")
    w1 = r["W1_lift_consistency"]
    print(f"  failures: {len(w1['failures'])}    {'OK' if w1['ok'] else 'FAIL'}")
    print()
    print("(W2) Chain-product preservation across rewrites:")
    w2 = r["W2_product_preservation"]
    for i, p in enumerate(w2["products"]):
        print(f"  L{i} product: {p}")
    print(f"  all equal:  {w2['all_equal']}    "
          f"{'OK' if w2['all_equal'] else 'FAIL'}")
    print()
    print("(W3) Contraction:")
    w3 = r["W3_contraction"]
    print(f"  lengths:    {w3['lengths']}")
    print(f"  violations: {len(w3['violations'])}    {'OK' if w3['ok'] else 'FAIL'}")
    print()
    print(f"Result: {'OK' if r['all_ok'] else 'FAILURE'}")
    return 0 if r["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
