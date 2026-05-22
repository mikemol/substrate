"""Eliza.SpectralPredictor — GG5 multi-prime spectrum-conditioned
predictor.

Maintains N_SPECTRAL_BUCKETS separate count tables; selects bucket
by a hash of the global spectral atlas computed once at start.

Per [[multi-reading-ambient-discipline]]: the spectral class is one
ambient reading of the input; the predictor's per-class adaptation
is the local consequence.

For empirical use within a single-pass codec, the bucket selection
adds 3 bits to the header (8 buckets) but allows the encoder to
trade per-bucket-adaptation against bucket-id overhead. The actual
compression gain depends on whether bucket-conditional distributions
are meaningfully more peaked than the universal one — measured by
GG7.
"""

from __future__ import annotations

from math import log2
from typing import Optional

import numpy as np

from eliza.spectral_atlas import spectral_atlas
from eliza.v7_predictor import Predictor, _smoothed_cumfreqs


N_SPECTRAL_BUCKETS = 8


def classify_spectrum(data: bytes) -> int:
    """Map `data` to a spectral bucket index ∈ [0, N_SPECTRAL_BUCKETS).

    Signature: 3 bits derived from three thresholded readings:
      bit_0: cross_prime[2, 7] > 0.7  (high p2/p7 alignment)
      bit_1: cross_prime[3, 7] > 0.7  (high p3/p7 alignment)
      bit_2: sparsity[7] > 0.95         (sparse top-of-spectrum)
    """
    if not data:
        return 0
    atlas = spectral_atlas(data)
    M = atlas["cross_prime"]
    sparsity = atlas["sparsity"]
    # Primes order: (2, 3, 5, 7); indices 0..3.
    b0 = 1 if M[0, 3] > 0.7 else 0
    b1 = 1 if M[1, 3] > 0.7 else 0
    b2 = 1 if sparsity.get(7, 0.0) > 0.95 else 0
    return (b2 << 2) | (b1 << 1) | b0


class SpectralBucketPredictor(Predictor):
    """N_SPECTRAL_BUCKETS separate count tables; bucket fixed at init.

    The bucket parameter is set via `set_bucket(bucket_idx)` before
    encoding/decoding starts. All subsequent updates/queries route
    to that bucket's table.
    """

    name = "spectral_bucket"

    def __init__(self, max_alphabet: int):
        self.counts = np.zeros((N_SPECTRAL_BUCKETS, max_alphabet),
                                 dtype=np.int64)
        self.bucket = 0

    def set_bucket(self, bucket: int) -> None:
        self.bucket = bucket % N_SPECTRAL_BUCKETS

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self.counts[self.bucket], alphabet_size)

    def update(self, emit_idx, context=None):
        self.counts[self.bucket, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        if new_alphabet_size > self.counts.shape[1]:
            new_counts = np.zeros(
                (N_SPECTRAL_BUCKETS, new_alphabet_size), dtype=np.int64)
            new_counts[:, :self.counts.shape[1]] = self.counts
            self.counts = new_counts


# --- Self-check -----------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Classifier returns valid bucket on all inputs.
    test_cases = [
        b"",
        bytes([0] * 64),
        bytes(range(64)),
        b"The quick brown fox jumps over the lazy dog" * 8,
        bytes([0x55, 0xAA] * 32),
    ]
    for d in test_cases:
        b = classify_spectrum(d)
        if not (0 <= b < N_SPECTRAL_BUCKETS):
            if verbose:
                print(f"FAIL: classify -> {b} out of range")
            ok = False

    # 2. Different corpora may give different buckets.
    p = SpectralBucketPredictor(32)
    p.set_bucket(3)
    p.update(5, None)
    if p.counts[3, 5] != 1:
        if verbose:
            print(f"FAIL: update didn't reach bucket 3")
        ok = False

    # 3. cumfreqs returns valid distribution.
    cf = p.cumfreqs(32, None)
    if cf.shape[0] != 33 or cf[-1] <= 0:
        if verbose:
            print(f"FAIL: cumfreqs malformed")
        ok = False

    # 4. Grow works.
    p.grow_to(64)
    if p.counts.shape[1] != 64:
        if verbose:
            print(f"FAIL: grow_to didn't resize")
        ok = False

    if verbose:
        print(f"spectral_predictor self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
