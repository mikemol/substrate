"""tests/test_lossless_chain_comparison.py — three lossless modes head-to-head.

Three lossless paths, all measured on the same corpora at the same sizes:

  * gt-baseline:    dim2_codec (rotation + byte trigram). The existing codec.
  * per-nibble:     LosslessChainCodec — per-nibble chain stream via
                    adaptive chain trigram + arithmetic coding.
  * sppf:           GrammarEventCodec — SPPF (rule definitions) +
                    coefficients (start rule body) = the free Markov
                    model + the input's path through it.

All three round-trip byte-for-byte. Numbers in bits-per-input-byte.

Per the user's framing: the SPPF mode SHIPS THE GRAMMAR (free Markov
model) and the input's specific traversal (start rule body) as the
algebraic-content output.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.dim2_codec import encode as gt_encode, decode as gt_decode
from eliza.lossless_chain_codec import (
    encode as per_nibble_encode, decode as per_nibble_decode,
)
from eliza.grammar_event_codec import (
    encode as sppf_encode, decode as sppf_decode,
)


def _text(n: int) -> bytes:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < n:
        data = data + data
    return data[:n]


def _elf(n: int) -> bytes:
    with open("/bin/true", "rb") as f:
        return f.read(n)


def _zeros(n: int) -> bytes:
    return b"\x00" * n


CORPORA = {"text": _text, "elf": _elf, "zeros": _zeros}
SIZES = (1024, 4096, 16384)


def main() -> int:
    print("=== Lossless three-way comparison (gt / per-nibble / SPPF) ===\n")
    print(f"All numbers in BITS-PER-INPUT-BYTE. All modes round-trip\n"
          f"byte-for-byte (lossless).\n")

    for size in SIZES:
        print(f"--- {size}B inputs ---")
        print(f"{'corpus':>8}  {'gt-baseline':>12}  {'per-nibble':>11}  {'sppf':>8}"
              f"  {'sppf-rules':>11}  {'sppf-body':>10}")
        for name, factory in CORPORA.items():
            data = factory(size)
            # gt-baseline.
            enc_gt, _ = gt_encode(data)
            dec_gt = gt_decode(enc_gt, len(data))
            assert dec_gt == data, "gt round-trip failed"
            bpb_gt = 8 * len(enc_gt) / len(data)

            # per-nibble chain codec.
            enc_pn, stats_pn = per_nibble_encode(data)
            dec_pn = per_nibble_decode(enc_pn, len(data))
            assert dec_pn == data, "per-nibble round-trip failed"
            bpb_pn = 8 * len(enc_pn) / len(data)

            # SPPF codec.
            enc_sppf, stats_sppf = sppf_encode(data)
            dec_sppf = sppf_decode(enc_sppf)
            assert dec_sppf == data, "sppf round-trip failed"
            bpb_sppf = 8 * len(enc_sppf) / len(data)

            print(f"{name:>8}  {bpb_gt:>12.3f}  {bpb_pn:>11.3f}  "
                  f"{bpb_sppf:>8.3f}  {stats_sppf['n_rules']:>11}"
                  f"  {stats_sppf['start_rule_body_length']:>10}")
        print()

    print("Reading:")
    print("  gt-baseline:  byte trigram + rotation chooser (the deployed codec).")
    print("  per-nibble:   chain stream at per-nibble granularity, adaptive")
    print("                trigram over the 24-chain alphabet + arithmetic")
    print("                coding. Output is exclusively chain information.")
    print("  sppf:         SPPF (rule definitions) = the free Markov model")
    print("                + start rule body (the coefficients = input's path")
    print("                through the model). Decoder unfolds the body via")
    print("                the grammar.")
    print()
    print("All three are LOSSLESS. SPPF carries an explicit substrate")
    print("artefact (the grammar) along with the input. Per-nibble carries")
    print("the chain stream losslessly. gt-baseline carries bytes directly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
