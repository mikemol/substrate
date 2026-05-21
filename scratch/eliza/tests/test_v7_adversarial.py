"""tests/test_v7_adversarial.py — V7 (predictor-ring) sweep across the
adversarial corpora used for the U-arc + V-arc.

Reuses the corpus constructors from test_adversarial_e3 but switches
the codec under test to gpu_codec_v7 with all five predictor variants
bound to BasisLabel slots and the two-stage lookahead cost-gate.

Reports (E3) per (corpus, mode) pair, where mode is:
  * identity   — speculate_basis=False (= V6-equivalent, unigram only)
  * two-stage  — speculate_basis=True  (per-position two-stage agreement)
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v7 import encode, decode    # noqa: E402
from tests.test_adversarial_e3 import (
    phase_biased, length_biased, patch1_biased,
    patchk_biased, span_biased, random_baseline,
)

CORPORA = {
    "phase_biased":   phase_biased,
    "length_biased":  length_biased,
    "patch1_biased":  patch1_biased,
    "patchk_biased":  patchk_biased,
    "span_biased":    span_biased,
    "random":         random_baseline,
}


def main(size: int = 1024) -> int:
    print(f"=== V7 adversarial (E3) sweep — {size}B per corpus ===\n")
    print(f"{'corpus':<18}{'mode':<14}{'b/byte':>9}"
          f"  {'switches':>9}  {'ok':>5}")
    any_benefit = False
    for cname, ctor in CORPORA.items():
        data = ctor(n_bytes=size)
        base_bpb = None
        for mname, flag in (("identity", False), ("two-stage", True)):
            try:
                enc, stats = encode(data, speculate_basis=flag)
                dec = decode(enc)
                ok = dec == data
                bpb = 8 * len(enc) / len(data)
            except Exception as e:
                bpb = -1.0
                ok = False
                stats = {"n_basis_at": 0}
            if base_bpb is None:
                base_bpb = bpb
            delta = bpb - base_bpb if base_bpb > 0 else 0.0
            verdict = (
                "B" if delta < -0.01 else
                "R" if delta > 0.01 else
                "="
            )
            if verdict == "B":
                any_benefit = True
            print(f"{cname:<18}{mname:<14}{bpb:>8.3f}{verdict}"
                  f"  {stats.get('n_basis_at', 0):>9}"
                  f"  {'OK' if ok else 'FAIL':>5}")
        print()
    print(("BENEFIT observed on at least one (corpus, mode) pair."
           if any_benefit else
           "No mode beat baseline on any tested corpus."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
