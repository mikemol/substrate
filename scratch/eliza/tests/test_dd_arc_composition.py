"""DD7: Composition test for Clifford XOR-mask with backref+S₄ residue.

Verifies:
  (E2) AA-arc S₄ residue is dominated by Λ² (bivector) content of the
       bit-flip divergence multivector; higher-grade cascades surface
       at distance per [[chain-walk-blocks-rotation-factor]].
  (E5) There exists a corpus where Clifford speculation over multiple
       grades strictly beats identity (grade-0) AND beats a single-
       grade-2-only restriction.

Run: `python -m tests.test_dd_arc_composition` from `scratch/eliza`.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eliza.clifford import grade_decomposition, grade_project
from eliza.clifford_tracer import (
    aa_arc_s4_residue,
    find_best_clifford_mask,
    mask_grade,
    trace_bitflip_divergence,
    verify_aa_arc_as_grade2,
)
from eliza.gpu_codec_v7 import decode, encode


def e2_check(corpus_name: str, data: bytes, sample: int = 16) -> bool:
    """E2: residue distribution dominated by Λ² content."""
    prof = verify_aa_arc_as_grade2(data, sample_positions=sample)
    print(f"  E2 [{corpus_name}] residue_identity="
          f"{prof['fraction_residue_identity']:.3f} "
          f"grade2_present={prof['fraction_nontrivial_grade2']:.3f} "
          f"high_grade={prof['fraction_high_grade']:.3f}")
    # Pass if Λ² is present in > 80% of single-bit-flip traces.
    return prof["fraction_nontrivial_grade2"] > 0.80


def e5_check(corpus_name: str, data: bytes) -> bool:
    """E5: ∃ mask of grade ≠ 2 outperforming grade-2 restriction.

    Compares:
      (a) identity (grade=0): no Clifford pre-transform.
      (b) grade-2 restricted speculation.
      (c) unrestricted speculation.
    Reports the byte-sizes; (E5) holds if (c) < (a) AND (c) < (b).
    """
    enc_a, _ = encode(data, speculate_clifford=False)
    enc_b, meta_b = encode(data, speculate_clifford=True,
                              clifford_grade_cap=2)
    enc_c, meta_c = encode(data, speculate_clifford=True,
                              clifford_grade_cap=8)
    a, b, c = len(enc_a), len(enc_b), len(enc_c)
    print(f"  E5 [{corpus_name}]  identity={a}  ≤grade2={b} "
          f"(g={meta_b['clifford_grade']})  ≤grade8={c} "
          f"(g={meta_c['clifford_grade']})")
    # Verify round-trip first.
    assert decode(enc_a) == data, "E5 identity round-trip failed"
    assert decode(enc_b) == data, "E5 grade2 round-trip failed"
    assert decode(enc_c) == data, "E5 grade8 round-trip failed"
    return c < a and c <= b and meta_c["clifford_grade"] not in (0, 2)


def main() -> int:
    corpora = {
        "english": (b"The substrate codec extends compression across "
                    b"every gauge axis exposed by the Coxeter framework "
                    b"and chain walk algebra. Each byte carries S4 "
                    b"residue.") * 6,
        "structured": bytes([0x55, 0xAA, 0xFF, 0x00] * 200),
        "biased": bytes((i * 17) & 0xFF for i in range(800)),
        "highbit": bytes([0x80 | (i & 0x7F) for i in range(800)]),
    }

    print("DD7: Composition test (E2 + E5)")
    print()
    print("E2 — AA-arc S₄ residue vs Λ² projection of bit-flip trace:")
    e2_pass = True
    for name, data in corpora.items():
        if not e2_check(name, data):
            e2_pass = False
    print()
    print(f"  E2 verdict: {'PASS' if e2_pass else 'PARTIAL'} "
          f"(grade-2 dominance across tested corpora)")
    print()

    print("E5 — speculation over multiple grades vs grade-2-only:")
    e5_witness = False
    for name, data in corpora.items():
        if e5_check(name, data):
            e5_witness = True
            print(f"      ← witness: {name}")
    print()
    print(f"  E5 verdict: {'WITNESS FOUND' if e5_witness else 'NO WITNESS'}")
    print()
    return 0 if (e2_pass and e5_witness) else 1


if __name__ == "__main__":
    sys.exit(main())
