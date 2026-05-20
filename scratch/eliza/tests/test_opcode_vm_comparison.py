"""tests/test_opcode_vm_comparison.py — five-way lossless comparison.

  * gt-baseline:         dim2_codec (rotation + byte trigram)
  * per-nibble:          LosslessChainCodec
  * sppf:                GrammarEventCodec (no pre-seed)
  * preseeded-sppf:      PreseededSPPFCodec (pre-seeded opcodes,
                          rule-utility disabled)
  * opcode-vm:           OpcodeVMCodec (static opcode set, speculative-
                          commit / exploding-bitmap)
  * adaptive-vm:         AdaptiveOpcodeCodec (opcode set GROWS during
                          encoding via Sequitur-style digram detection)

All modes round-trip byte-for-byte. The adaptive-vm row IS the user's
"each rule is an opcode + speculative-commit + grammar grows" design.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.adaptive_opcode_codec import (
    encode as adaptive_encode, decode as adaptive_decode,
)
from eliza.dim2_codec import encode as gt_encode, decode as gt_decode
from eliza.grammar_event_codec import (
    encode as sppf_encode, decode as sppf_decode,
)
from eliza.lossless_chain_codec import (
    encode as per_nibble_encode, decode as per_nibble_decode,
)
from eliza.opcode_vm_codec import (
    encode as vm_encode, decode as vm_decode,
)
from eliza.preseeded_sppf_codec import (
    encode as preseeded_encode, decode as preseeded_decode,
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
SIZES = (1024, 4096)   # keep small — adaptive Python is slow


def main() -> int:
    print("=== Five-way lossless comparison ===\n")
    print(f"All numbers in BITS-PER-INPUT-BYTE; all modes round-trip"
          f" byte-for-byte.\n")

    for size in SIZES:
        print(f"--- {size}B inputs ---")
        print(f"{'corpus':>8}  {'gt':>6}  {'per-nibble':>11}  "
              f"{'sppf':>6}  {'pre-seed':>9}  {'op-vm':>7}  {'adaptive':>9}")
        for name, factory in CORPORA.items():
            data = factory(size)

            # gt
            enc_gt, _ = gt_encode(data)
            assert gt_decode(enc_gt, len(data)) == data
            bpb_gt = 8 * len(enc_gt) / len(data)

            # per-nibble lossless
            enc_pn, _ = per_nibble_encode(data)
            assert per_nibble_decode(enc_pn, len(data)) == data
            bpb_pn = 8 * len(enc_pn) / len(data)

            # SPPF without pre-seed
            enc_sppf, _ = sppf_encode(data)
            assert sppf_decode(enc_sppf) == data
            bpb_sppf = 8 * len(enc_sppf) / len(data)

            # Pre-seeded SPPF
            enc_ps, _ = preseeded_encode(data)
            assert preseeded_decode(enc_ps) == data
            bpb_ps = 8 * len(enc_ps) / len(data)

            # Static opcode-VM
            enc_vm, _ = vm_encode(data)
            assert vm_decode(enc_vm) == data
            bpb_vm = 8 * len(enc_vm) / len(data)

            # Adaptive opcode-VM
            enc_adapt, _ = adaptive_encode(data)
            assert adaptive_decode(enc_adapt) == data
            bpb_adapt = 8 * len(enc_adapt) / len(data)

            print(f"{name:>8}  {bpb_gt:>6.2f}  {bpb_pn:>11.2f}  "
                  f"{bpb_sppf:>6.2f}  {bpb_ps:>9.2f}  "
                  f"{bpb_vm:>7.2f}  {bpb_adapt:>9.2f}")
        print()

    print("Reading:")
    print("  gt          — existing codec (rotation + byte trigram)")
    print("  per-nibble  — per-nibble chain stream + chain trigram + AC")
    print("  sppf        — grammar (rules) + start rule body, no pre-seed")
    print("  pre-seed    — pre-seeded opcodes, _maybe_inline_underused disabled")
    print("  op-vm       — speculative-commit/exploding-bitmap, static opcode set")
    print("  adaptive    — speculative-commit + opcode set GROWS by digram detection")
    return 0


if __name__ == "__main__":
    sys.exit(main())
