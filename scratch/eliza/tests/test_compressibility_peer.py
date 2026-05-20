"""tests/test_compressibility_peer.py — gt-codec vs chain-codec (peers).

Two codecs differing only in rotation chooser:
  * gt    (PresentedGroup):       adaptive -log P scoring
  * chain (ConjugationCoalgebra): Sylow-chain norm with adaptive ref

Both rates emitted as facts. Neither is canonical. Compared to the
prior Bezout-of-scalars chooser (deleted per [[codec-as-pfg-witness]]),
the chain chooser IS rotation-discriminating by construction — it
should land closer to gt's compression than the Bezout chooser did.
"""

from __future__ import annotations

import sys
from pathlib import Path
from math import log2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from typing import Callable, Tuple

from eliza.arith import RangeEncoder
from eliza.chain_chooser import AdaptiveReferenceChainChooser, ChainNormChooser
from eliza.codec import _cumfreqs_from_predictor
from eliza.dim2_codec import (
    ROT_TAG_TOTAL,
    _choose_rotation_canonical,
)
from eliza.octonion import rotate_bytes
from eliza.predictor import TrigramPredictor
from eliza.sequitur import Sequitur


def encode_with_chooser(
    data: bytes, chooser_factory: Callable[[TrigramPredictor], Callable],
    window_size: int = 256
) -> Tuple[bytes, dict]:
    pred = TrigramPredictor(vocab_size=256)
    chooser = chooser_factory(pred)
    seq_rot = Sequitur()
    enc = RangeEncoder()
    rotation_counter = [0] * 16
    rot_cumfreqs = list(range(ROT_TAG_TOTAL + 1))

    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        r = chooser(window, pred) if callable(chooser) else chooser(window)
        enc.encode(rot_cumfreqs, r, ROT_TAG_TOTAL)
        rotation_counter[r] += 1
        rotated = rotate_bytes(window, r)
        for b in rotated:
            cumfreqs, total = _cumfreqs_from_predictor(pred, 256)
            enc.encode(cumfreqs, b, total)
            pred.update(chr(b))
        seq_rot.observe(r)
    encoded = enc.finish()
    return encoded, {
        "encoded_bytes": len(encoded),
        "rotation_counts": rotation_counter,
        "n_windows": sum(rotation_counter),
    }


def main(corpus_size: int = 5000) -> int:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        base = f.read()
    while len(base) < corpus_size:
        base = base + base
    text = base[:corpus_size]
    n3 = len(text) // 3
    mixed = (
        text[:n3] +
        rotate_bytes(text[n3:2 * n3], 6) +
        rotate_bytes(text[2 * n3:3 * n3], 11)
    )

    print("=== Peer-codec compressibility (gt vs chain) ===\n")
    print(f"Input: {len(mixed)} bytes (engine.py × 3, mixed orientation)\n")

    peers = [
        ("gt    (PresentedGroup)",
            lambda p: lambda w, _p=p: _choose_rotation_canonical(w, _p)),
        ("chain-static  (chain norm vs ORIGIN)",
            lambda p: ChainNormChooser()),
        ("chain-adaptive (chain norm vs rolling ref)",
            lambda p: AdaptiveReferenceChainChooser()),
    ]
    results = []
    for label, factory in peers:
        encoded, stats = encode_with_chooser(mixed, factory)
        bpb = len(encoded) * 8 / len(mixed)
        n_w = stats["n_windows"]
        rot_entropy = 0.0
        for c in stats["rotation_counts"]:
            if c > 0:
                p = c / n_w
                rot_entropy -= p * log2(p)
        results.append((label, len(encoded), bpb, rot_entropy,
                        stats["rotation_counts"]))
        print(f"{label}:")
        print(f"  encoded:           {len(encoded)} bytes ({bpb:.3f} b/byte)")
        print(f"  rotation entropy:  {rot_entropy:.3f} bits  (max {log2(16):.3f})")
        print(f"  rotation counts:   {stats['rotation_counts']}\n")

    # Compare deltas.
    gt_size = results[0][1]
    print("Deltas relative to gt:")
    for label, n, _, _, _ in results[1:]:
        delta = n - gt_size
        pct = 100 * delta / gt_size
        print(f"  {label:>40}: {delta:+d} bytes  ({pct:+.1f}%)")
    print()
    print("Reading: both chain variants are facts about a substrate-honest")
    print("ConjugationCoalgebra commitment; the gt-vs-chain delta is the")
    print("Galois adjunction's bitstream-level signal under the chain ATLAS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
