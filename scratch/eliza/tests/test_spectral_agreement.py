"""tests/test_spectral_agreement.py — V₄⋊S₃ duality verification.

Per the DATAFLOW_REMODEL correction: the spectral basis and the V₄⋊S₃
algebraic basis are dual coordinate systems for the same algebra. If
the claim holds, two rotation choosers operating in the two bases
should pick the same rotation per window (in the asymptote).

This test runs both choosers on mixed-orientation input and reports
the agreement rate. Gate: ≥0.95 agreement on a tripartite-mixed input.
Below that signals a tuning bug in one of the choosers; the disagreement
windows are diagnostic.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.dim2_codec import _choose_rotation_canonical
from eliza.manifold import Manifold
from eliza.octonion import rotate_bytes
from eliza.orbit import Cocycle
from eliza.predictor import TrigramPredictor
from eliza.spectral import (
    SpectralBasis, SpectralChooser, s3_irrep_blocks,
)


def chamber_sequence(window: bytes, manifold: Manifold) -> list:
    """Walk through a window's bytes via nibble routing; return the
    chamber-index sequence."""
    chamber = ORIGIN
    indices = []
    for byte in window:
        # Each byte produces 2 nibbles; we walk per-nibble.
        for nib in [(byte >> 4) & 0xF, byte & 0xF]:
            perm = NIBBLE_TO_PERM[nib]
            chamber = perm_compose(chamber, perm)
            indices.append(manifold.node_index(chamber))
    return indices


def gt_chooser(window: bytes, pred: TrigramPredictor) -> int:
    """Wrap the existing dim2_codec chooser."""
    return _choose_rotation_canonical(window, pred)


def spectral_chooser_for_window(
    window: bytes, chooser: SpectralChooser, manifold: Manifold
) -> int:
    """Score each of 16 rotations by spectral score; return argmin."""
    best_r = 0
    best_score = float("inf")
    for r in range(16):
        rotated = rotate_bytes(window, r)
        seq = chamber_sequence(rotated, manifold)
        s = chooser.score(seq)
        if s < best_score:
            best_score = s
            best_r = r
    return best_r


def run_agreement(window_size: int = 256, corpus_size: int = 5000) -> float:
    """Run both choosers on mixed-orientation input; return agreement rate."""
    # Build mixed input: thirds rotated by 0 / 6 / 11.
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

    m = Manifold()
    basis = SpectralBasis.from_manifold(m)
    blocks = s3_irrep_blocks(basis)
    spec_chooser = SpectralChooser(basis=basis, manifold=m)
    pred = TrigramPredictor(vocab_size=256)
    # Warm the predictor with a small prefix so it can score rotations.
    for byte in text[:512]:
        pred.update(chr(byte))

    n_windows = len(mixed) // window_size
    agreements = 0
    disagreements = []
    for i in range(n_windows):
        window = mixed[i * window_size:(i + 1) * window_size]
        gt_pick = gt_chooser(window, pred)
        spec_pick = spectral_chooser_for_window(window, spec_chooser, m)
        if gt_pick == spec_pick:
            agreements += 1
        else:
            disagreements.append((i, gt_pick, spec_pick))
        # Update predictor with the gt-pick's rotation (lockstep with what
        # the codec would actually emit).
        for byte in rotate_bytes(window, gt_pick):
            pred.update(chr(byte))

    rate = agreements / n_windows if n_windows > 0 else 0.0
    print(f"Mixed-orientation agreement test:")
    print(f"  windows: {n_windows}")
    print(f"  agreements: {agreements}")
    print(f"  rate: {rate:.3f}")
    print(f"  disagreements (first 5): "
          f"{disagreements[:5] if disagreements else '(none)'}")
    return rate


if __name__ == "__main__":
    rate = run_agreement()
    threshold = 0.95
    status = "PASS" if rate >= threshold else "BELOW GATE"
    print(f"\nGate (≥{threshold}): {status}")
    sys.exit(0 if rate >= threshold else 1)
