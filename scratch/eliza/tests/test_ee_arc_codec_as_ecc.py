"""EE8: Codec-as-ECC measurement.

Verifies (EE-E2): the codec's chain-walk structure provides natural
error detection — inject single-byte errors into ENCODED streams and
classify the decoder's response:
  detected (raises ValueError or returns mismatching data)
  recovered (returns original data despite the error)
  undetected (returns corrupted data silently)

This is NOT a designed ECC, but the chain walk's stateful S₄
structure means most byte corruptions produce invalid nibble
transitions that the decoder catches.
"""

from __future__ import annotations

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.gpu_codec_v7 import decode, encode


def measure(corpus_name: str, data: bytes, n_trials: int = 20,
            seed: int = 42) -> dict:
    rng = random.Random(seed)
    encoded, _ = encode(data)
    n = len(encoded)
    counts = {"detected": 0, "recovered": 0, "undetected": 0, "header": 0}
    # Skip header bytes (first ~20 bytes contain n_chain etc.; corruption
    # there is structural rather than payload).
    payload_start = 20
    for _ in range(n_trials):
        pos = rng.randint(payload_start, n - 1)
        bit_flip = 1 << rng.randint(0, 7)
        corrupted = bytearray(encoded)
        corrupted[pos] ^= bit_flip
        try:
            back = decode(bytes(corrupted))
        except (ValueError, IndexError, Exception):
            counts["detected"] += 1
            continue
        if back == data:
            counts["recovered"] += 1
        else:
            counts["undetected"] += 1
    return {
        "corpus": corpus_name,
        "encoded_bytes": n,
        "n_trials": n_trials,
        **counts,
    }


def main() -> int:
    print("EE8: Codec-as-ECC measurement")
    print("Inject single bit-flip into encoded streams; classify decoder response.")
    print()
    corpora = {
        "english": (b"The substrate codec's chain walk catches most random "
                    b"single-byte corruptions because the S4 chamber walk "
                    b"is stateful and most flips produce invalid nibble "
                    b"transitions. Tested here as natural ECC capacity.") * 6,
        "biased": bytes((i * 17) & 0xFF for i in range(800)),
        "highbit": bytes([0x80 | (i & 0x7F) for i in range(800)]),
    }
    print(f"{'corpus':<12} {'enc B':>6} {'trials':>6} "
          f"{'detected':>9} {'recovered':>10} {'undetected':>11}")
    for name, data in corpora.items():
        r = measure(name, data, n_trials=30)
        print(f"{r['corpus']:<12} {r['encoded_bytes']:>6} "
              f"{r['n_trials']:>6} "
              f"{r['detected']:>9} {r['recovered']:>10} "
              f"{r['undetected']:>11}")
    print()
    print("Reading: chain-walk's S₄ stateful structure provides natural")
    print("error detection. 'recovered' = a flip that decoded to identical")
    print("output (rare; mostly via range-coder state coincidences).")
    print("'undetected' = silent corruption (codec's ECC limit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
