"""tests/test_bwt_emergence.py — does BWT structure emerge from rotation
full-speculation?

Per the user: "done correctly, BWT should be _emergent_ from the CD
rotations." Test: for each window, full-speculate across all 16
nibble-rotations. For each rotation, encode the rest of the input under
that rotation. Pick the cheapest. Examine the committed rotation pattern.

BWT-emergence diagnostic: the committed rotation pattern should
correlate with BWT's sorted-rotations principle — rotations that put
"frequent" suffixes at the front should win, mimicking BWT's last-column
selection that places similar contexts together.

This is a small diagnostic on short input due to O(16N²) cost. The
finding is structural — if rotation choices cluster by content
similarity, BWT-emergence is real.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import time
from collections import Counter

from eliza.adaptive_opcode_codec import encode as ad_enc, decode as ad_dec
from eliza.octonion import rotate_bytes


def encode_under_rotation(data: bytes, r: int) -> int:
    """Encode `data` after rotating each byte by `r`. Return byte count."""
    rotated = rotate_bytes(data, r)
    enc, _ = ad_enc(rotated)
    return len(enc)


def full_spec_rotation_per_window(data: bytes, window_size: int = 32) -> dict:
    """For each window, try all 16 rotations; pick the cheapest by
    encoded-byte-count of just that window. Returns rotation pattern."""
    windows = []
    for start in range(0, len(data), window_size):
        windows.append(data[start:start + window_size])

    chosen_rotations = []
    for w in windows:
        if not w:
            continue
        best_r = 0
        best_size = float("inf")
        for r in range(16):
            sz = encode_under_rotation(w, r)
            if sz < best_size:
                best_size = sz
                best_r = r
        chosen_rotations.append(best_r)
    return {
        "n_windows": len(windows),
        "chosen_rotations": chosen_rotations,
        "rotation_histogram": Counter(chosen_rotations),
        "distinct_rotations": len(set(chosen_rotations)),
    }


def main(size: int = 128) -> int:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:size]

    print("=== BWT-emergence diagnostic ===\n")
    print(f"Input: first {size} bytes of engine.py")
    print(f"Window size: 32 bytes; 16 rotations × N windows full-spec\n")

    t0 = time.perf_counter()
    report = full_spec_rotation_per_window(data, window_size=32)
    dt = time.perf_counter() - t0

    print(f"Windows: {report['n_windows']}")
    print(f"Time: {dt:.2f}s")
    print(f"Distinct rotations chosen: {report['distinct_rotations']} / 16")
    print()
    print("Rotation histogram (which rotations did the encoder commit to):")
    for r in sorted(report['rotation_histogram'].keys()):
        count = report['rotation_histogram'][r]
        bar = "█" * count
        print(f"  r={r:>2}: {count:>3} windows {bar}")

    # BWT-emergence reading: if a few rotations dominate (top-3 covers
    # ≥80% of windows), the codec is committing to a small alignment
    # vocabulary, consistent with BWT-like coherence.
    sorted_counts = sorted(report['rotation_histogram'].values(), reverse=True)
    top3 = sum(sorted_counts[:3])
    top3_pct = 100 * top3 / report['n_windows']
    print()
    print(f"Top 3 rotations cover {top3} / {report['n_windows']} windows "
          f"({top3_pct:.1f}%)")
    if top3_pct >= 80:
        print("  → STRONG concentration; consistent with BWT-emergent coherence")
    elif top3_pct >= 60:
        print("  → moderate concentration; partial BWT-like behaviour")
    else:
        print("  → diffuse; no clear emergent rotation preference")

    return 0


if __name__ == "__main__":
    sys.exit(main())
