"""tests/test_galois_adjunction.py — chain-level peer-view measurement.

gt and the chain chooser are Galois-conjugate peer views:
  * gt    (PresentedGroup):       adaptive -log P(byte | context)
  * chain (ConjugationCoalgebra): Sylow-chain norm against a reference

Both read the same algebra through different functorial lenses. The
report exposes the CHAIN SHAPE at gt's choice vs the chain shape at
chain's choice — not a scalar agreement rate.

Per `MultiRouteEquivariance.agda`: the chain shape (v, s3, s2) IS the
load-bearing structural content. Two choosers landing at chains with
the same v-component (Sylow-2 agreement) but different s3-components
(Sylow-3 disagreement) is the precise diagnostic the prior scalar
report could not produce.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from collections import Counter

from eliza.chain_chooser import ChainNormChooser
from eliza.dim2_codec import _choose_rotation_canonical
from eliza.gauge_element import gauge_element
from eliza.octonion import rotate_bytes
from eliza.predictor import TrigramPredictor
from eliza.sylow_chain import (
    V4_E, S3_E, build_chain,
)
from eliza.walk_carrier import walk_to_s4


def chain_at_rotation(window: bytes, r: int, reference) -> "SylowChain":
    rotated = rotate_bytes(window, r)
    carrier = walk_to_s4(rotated)
    return build_chain(gauge_element(carrier.state, reference))


def run_report(window_size: int = 256, corpus_size: int = 5000) -> dict:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < corpus_size:
        data = data + data
    text = data[:corpus_size]
    n3 = len(text) // 3
    mixed = (
        text[:n3] +
        rotate_bytes(text[n3:2*n3], 6) +
        rotate_bytes(text[2*n3:3*n3], 11)
    )

    pred = TrigramPredictor(vocab_size=256)
    for byte in text[:512]:
        pred.update(chr(byte))

    chain_chooser = ChainNormChooser()

    n_windows = len(mixed) // window_size
    rows = []
    for i in range(n_windows):
        window = mixed[i * window_size:(i + 1) * window_size]
        gt_pick = _choose_rotation_canonical(window, pred)
        chain_pick = chain_chooser(window)
        gt_chain = chain_at_rotation(window, gt_pick, chain_chooser.reference)
        chain_chain = chain_at_rotation(window, chain_pick, chain_chooser.reference)
        rows.append({
            "i": i,
            "gt_pick": gt_pick,
            "chain_pick": chain_pick,
            "agree": gt_pick == chain_pick,
            "gt_chain_len": gt_chain.word_length,
            "chain_chain_len": chain_chain.word_length,
            "gt_v": gt_chain.v,
            "gt_s3": gt_chain.s3,
            "gt_s2": gt_chain.s2,
            "chain_v": chain_chain.v,
            "chain_s3": chain_chain.s3,
            "chain_s2": chain_chain.s2,
        })
        # Update predictor on the gt-picked rotation (lockstep with codec).
        for byte in rotate_bytes(window, gt_pick):
            pred.update(chr(byte))

    n_agree = sum(1 for r in rows if r["agree"])
    n_disagree = n_windows - n_agree

    # Chain-component agreement: gt and chain both land at the same v?
    # Same s3? Same s2?
    v_agree = sum(1 for r in rows if r["gt_v"] == r["chain_v"])
    s3_agree = sum(1 for r in rows if r["gt_s3"] == r["chain_s3"])
    s2_agree = sum(1 for r in rows if r["gt_s2"] == r["chain_s2"])

    # Chain-length distribution per chooser.
    gt_len_dist = Counter(r["gt_chain_len"] for r in rows)
    chain_len_dist = Counter(r["chain_chain_len"] for r in rows)

    # gt's chain-shape distribution (what gt is "discovering" in chain
    # space, even though it doesn't read chains).
    gt_v_dist = Counter(r["gt_v"] for r in rows)
    chain_v_dist = Counter(r["chain_v"] for r in rows)
    gt_s3_dist = Counter(r["gt_s3"] for r in rows)
    chain_s3_dist = Counter(r["chain_s3"] for r in rows)

    return {
        "n_windows": n_windows,
        "rotation_agree": n_agree,
        "rotation_disagree": n_disagree,
        "v_component_agree": v_agree,
        "s3_component_agree": s3_agree,
        "s2_component_agree": s2_agree,
        "gt_chain_length_dist": gt_len_dist,
        "chain_chain_length_dist": chain_len_dist,
        "gt_v_dist": gt_v_dist,
        "chain_v_dist": chain_v_dist,
        "gt_s3_dist": gt_s3_dist,
        "chain_s3_dist": chain_s3_dist,
        "rows_sample": rows[:3],
    }


def main():
    print("=== Galois Adjunction Report (chain level) — gt ↔ chain ===\n")
    report = run_report()
    nw = report["n_windows"]
    print(f"Windows: {nw}")
    print()
    print("Per-window agreement at each chain component:")
    print(f"  rotation-level:     {report['rotation_agree']:>4} / {nw}  "
          f"({100*report['rotation_agree']/nw:.1f}%)")
    print(f"  V₄ component (v):   {report['v_component_agree']:>4} / {nw}  "
          f"({100*report['v_component_agree']/nw:.1f}%)")
    print(f"  Sylow-3 (s3):       {report['s3_component_agree']:>4} / {nw}  "
          f"({100*report['s3_component_agree']/nw:.1f}%)")
    print(f"  S₃-Sylow-2 (s2):    {report['s2_component_agree']:>4} / {nw}  "
          f"({100*report['s2_component_agree']/nw:.1f}%)")
    print()
    print("Chain-length distribution per chooser:")
    print(f"  gt:    {dict(sorted(report['gt_chain_length_dist'].items()))}")
    print(f"  chain: {dict(sorted(report['chain_chain_length_dist'].items()))}")
    print()
    print("V₄-component distribution per chooser (4 elements):")
    print(f"  gt:    {dict(sorted(report['gt_v_dist'].items()))}")
    print(f"  chain: {dict(sorted(report['chain_v_dist'].items()))}")
    print()
    print("Sylow-3-component distribution per chooser (3 elements):")
    print(f"  gt:    {dict(sorted(report['gt_s3_dist'].items()))}")
    print(f"  chain: {dict(sorted(report['chain_s3_dist'].items()))}")
    print()
    print("Sample chain row 0:")
    r0 = report["rows_sample"][0]
    print(f"  gt_pick={r0['gt_pick']} → chain (v={r0['gt_v']}, s3={r0['gt_s3']}, "
          f"s2={r0['gt_s2']}, |w|={r0['gt_chain_len']})")
    print(f"  chain_pick={r0['chain_pick']} → chain (v={r0['chain_v']}, "
          f"s3={r0['chain_s3']}, s2={r0['chain_s2']}, |w|={r0['chain_chain_len']})")
    print()
    print("Reading: per-component agreement decomposes the rotation-level")
    print("delta into substrate-honest Sylow contributions. Disagreement")
    print("at v but agreement at s3 = Sylow-2 is the diverging axis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
