"""Follow-up to EE13: phase-shifted Golay mask sweep.

EE13 applied Golay [24, 12, 8] at byte-phase 0 only — the 3-byte frame
starts at data[0]. The chain walk's natural unit is the nibble (2 per
byte), so the "phase" axis has 6 nibble-positions but 3 byte-positions
within a 3-byte frame.

Try byte-phase ∈ {0, 1, 2} × all 4096 Golay codewords. If any phase ×
codeword combo unlocks compression, the off-axis verdict from EE13
becomes "off-axis under naive alignment, recoverable under phase".

Per the user's prompt: 'we should be able to work around this with
the clifford offset work we did for backref; it ought to be possible
to change the phase of the golay code'.
"""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.golay import all_extended_golay_codewords
from eliza.multiscale_rotation import chain_symbol_entropy_estimator
from tests.test_substrate_atlas import CORPORA


def apply_golay_mask_phase(data: bytes, mask24: int, phase: int) -> bytes:
    """Apply 24-bit Golay codeword as XOR, with byte-phase ∈ {0, 1, 2}.

    phase = 0: data[0] ^= triple[0], data[1] ^= triple[1], data[2] ^= triple[2], ...
    phase = 1: data[0] ^= triple[2], data[1] ^= triple[0], ...
    phase = 2: data[0] ^= triple[1], data[1] ^= triple[2], ...
    """
    if mask24 == 0:
        return bytes(data)
    triple = [(mask24 >> 16) & 0xFF,
              (mask24 >> 8) & 0xFF,
              mask24 & 0xFF]
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = b ^ triple[(i - phase) % 3]
    return bytes(out)


def find_best_phase_shifted_golay(
    data: bytes,
    n_phases: int = 3,
    two_stage: bool = True,
):
    """Sweep (phase, codeword) for the best chain-symbol entropy."""
    codewords = all_extended_golay_codewords()

    def best_in(window: bytes):
        best_score = chain_symbol_entropy_estimator(window)
        best_m = 0
        best_p = 0
        for phase in range(n_phases):
            for m in codewords:
                if m == 0:
                    continue
                score = chain_symbol_entropy_estimator(
                    apply_golay_mask_phase(window, m, phase))
                if score < best_score:
                    best_score = score
                    best_m = m
                    best_p = phase
        return (best_m, best_p, best_score)

    g_m, g_p, g_s = best_in(data)
    if not two_stage:
        return (g_m, g_p, g_s)
    half = max(1, len(data) // 2)
    f_m, f_p, _ = best_in(data[:half])
    s_m, s_p, _ = best_in(data[half:])
    if g_m == f_m == s_m and g_p == f_p == s_p:
        return (g_m, g_p, g_s)
    return (0, 0, chain_symbol_entropy_estimator(data))


def main() -> int:
    print("Follow-up to EE13: phase-shifted Golay sweep")
    print()
    sizes = (512, 1024)   # smaller sizes; sweep is 4096 × 3 phases
    for size in sizes:
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'identity':>10} {'best Golay':>12} "
              f"{'phase':>5} {'mask24':>10} {'ms':>6}")
        for name, builder in CORPORA.items():
            data = builder(size)
            h0 = chain_symbol_entropy_estimator(data)
            t0 = time.perf_counter()
            m, p, s = find_best_phase_shifted_golay(data)
            ms = int((time.perf_counter() - t0) * 1000)
            print(f"{name:<22} {h0:>10.4f} {s:>12.4f} "
                  f"{p:>5} 0x{m:>08x} {ms:>6}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
