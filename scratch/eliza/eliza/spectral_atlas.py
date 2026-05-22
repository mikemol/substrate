"""Eliza.SpectralAtlas — GG2/GG3/GG4 multi-prime spectral analysis.

For each prime p ∈ {2, 3, 5, 7}, computes:
  - sliding-window symbol counts at p-bit width
  - WHT coefficients (Fourier-like spectrum)
  - dominant-coefficient subset (top-k by absolute value)
  - sparsity index (effective support of the spectrum)

The cross-prime correlation matrix M_pq measures structural
agreement between the p-bit and q-bit views (Pearson correlation
of the normalised sparsity vectors).

Per [[multi-reading-ambient-discipline]]: each prime view is one
substrate-honest reading; the atlas is the orbit, not any single
point.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.walsh_hadamard import multi_prime_profile, prime_spectrum


PRIMES_DEFAULT: Tuple[int, ...] = (2, 3, 5, 7)


# --- GG3: dominant-coefficient extraction --------------------------


def dominant_coefficients(coeffs: np.ndarray, k: int = None,
                            threshold_fraction: float = 0.05,
                            ) -> List[Tuple[int, int]]:
    """Return the top-k WHT coefficients by |value|.

    If k is None, returns all coefficients whose |value| ≥
    threshold_fraction × max(|coeffs|).

    Skips the DC component (index 0) which equals the total count.

    Returns list of (index, signed-value) sorted by descending |value|.
    """
    n = len(coeffs)
    if n == 0:
        return []
    ac = np.abs(coeffs).astype(np.int64)
    ac[0] = 0   # skip DC
    if k is None:
        max_ac = int(ac.max())
        if max_ac == 0:
            return []
        cutoff = int(max_ac * threshold_fraction)
        idxs = np.where(ac >= cutoff)[0]
    else:
        order = np.argsort(-ac)
        idxs = order[:k]
    out = [(int(i), int(coeffs[i])) for i in idxs if ac[i] > 0]
    out.sort(key=lambda t: -abs(t[1]))
    return out


def sparsity_index(coeffs: np.ndarray) -> float:
    """Effective spectral support, normalised: |non-trivial coeffs| / 2ᵖ.

    Defines "non-trivial" as |coeff| ≥ 5% of max(|coeffs|). Smaller
    means more structured (peaked spectrum).
    """
    n = len(coeffs)
    if n == 0:
        return 0.0
    ac = np.abs(coeffs).astype(np.int64)
    ac[0] = 0   # skip DC
    max_ac = int(ac.max())
    if max_ac == 0:
        return 0.0
    cutoff = max_ac * 0.05
    nontrivial = int((ac >= cutoff).sum())
    return nontrivial / n


def spectral_entropy(coeffs: np.ndarray) -> float:
    """Entropy of the absolute-value-normalised spectrum (excluding DC).

    Lower entropy = more peaked Fourier spectrum = more structured.
    Returned in bits.
    """
    ac = np.abs(coeffs).astype(np.float64)
    ac[0] = 0.0
    total = ac.sum()
    if total == 0:
        return 0.0
    p = ac / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


# --- GG4: cross-prime correlation -----------------------------------


def _normalised_spectrum_vector(coeffs: np.ndarray) -> np.ndarray:
    """Return |coeffs| / sum (zero-DC normalisation), to compute
    Pearson correlation across different-length spectra.

    Reduces each prime's spectrum to its dominant-coefficient
    distribution; for correlation purposes we project onto the
    "non-DC sparsity profile" vector.

    Returns a length-K vector of the top-K absolute coefficients
    sorted descending, K = min(8, 2ᵖ - 1).
    """
    n = len(coeffs)
    if n <= 1:
        return np.zeros(8, dtype=np.float64)
    ac = np.abs(coeffs).astype(np.float64)
    ac[0] = 0.0
    sorted_ac = np.sort(ac)[::-1]
    K = min(8, n - 1)
    out = np.zeros(8, dtype=np.float64)
    total = float(sorted_ac.sum())
    if total > 0:
        out[:K] = sorted_ac[:K] / total
    return out


def cross_prime_correlation(data: bytes,
                              primes: Tuple[int, ...] = PRIMES_DEFAULT
                              ) -> np.ndarray:
    """4×4 cross-prime correlation matrix.

    M[i, j] = Pearson correlation of the normalised top-8 sparsity
    vector at prime[i] vs prime[j]. M[i, i] = 1.0.

    High M[i, j] means the two primes "see" similar structure (their
    dominant coefficients align in magnitude pattern).
    """
    profile = multi_prime_profile(data, primes=primes)
    vectors = [_normalised_spectrum_vector(profile[p]["coeffs"])
               for p in primes]
    n = len(primes)
    M = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            x = vectors[i]
            y = vectors[j]
            xm = x - x.mean()
            ym = y - y.mean()
            denom = (np.linalg.norm(xm) * np.linalg.norm(ym))
            M[i, j] = float(xm @ ym) / denom if denom > 0 else 0.0
    return M


# --- GG2/3/4 unified atlas builder ---------------------------------


def spectral_atlas(data: bytes,
                     primes: Tuple[int, ...] = PRIMES_DEFAULT) -> Dict:
    """Build the multi-prime spectral atlas.

    Returns a dict with:
      profiles[p] = {counts, coeffs}
      dominant[p] = list of (index, value) for top-8 WHT coefficients
      sparsity[p] = sparsity_index (effective support fraction)
      entropy[p]  = spectral entropy in bits
      cross_prime = (n, n) correlation matrix
      primes      = primes tuple
    """
    profile = multi_prime_profile(data, primes=primes)
    dominant: Dict[int, List[Tuple[int, int]]] = {}
    sparsity: Dict[int, float] = {}
    entropy: Dict[int, float] = {}
    for p in primes:
        coeffs = profile[p]["coeffs"]
        dominant[p] = dominant_coefficients(coeffs, k=8)
        sparsity[p] = sparsity_index(coeffs)
        entropy[p] = spectral_entropy(coeffs)
    cross = cross_prime_correlation(data, primes=primes)
    return {
        "profiles": profile,
        "dominant": dominant,
        "sparsity": sparsity,
        "entropy": entropy,
        "cross_prime": cross,
        "primes": tuple(primes),
    }


# --- Self-check -----------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Empty data atlas is well-formed.
    atlas = spectral_atlas(b"")
    if set(atlas["sparsity"].keys()) != {2, 3, 5, 7}:
        if verbose:
            print(f"FAIL: empty data sparsity keys {atlas['sparsity'].keys()}")
        ok = False

    # 2. Non-trivial data: sparsity indices in [0, 1].
    data = bytes(range(256))
    atlas = spectral_atlas(data)
    for p, s in atlas["sparsity"].items():
        if not (0.0 <= s <= 1.0):
            if verbose:
                print(f"FAIL: sparsity[{p}] = {s} out of [0, 1]")
            ok = False

    # 3. Cross-prime matrix is symmetric and diagonal == 1.
    M = atlas["cross_prime"]
    if not np.allclose(M, M.T, atol=1e-6):
        if verbose:
            print(f"FAIL: cross-prime matrix not symmetric")
        ok = False
    if not np.allclose(np.diag(M), 1.0, atol=1e-6):
        if verbose:
            print(f"FAIL: cross-prime diagonal ≠ 1")
        ok = False

    # 4. Dominant coefficients respect ordering.
    for p, doms in atlas["dominant"].items():
        for k in range(1, len(doms)):
            if abs(doms[k][1]) > abs(doms[k - 1][1]):
                if verbose:
                    print(f"FAIL: dominant ordering at p={p}")
                ok = False

    # 5. Structured input (all zeros) gives peaked spectrum.
    zeros = bytes([0] * 256)
    atlas_zero = spectral_atlas(zeros)
    # For zeros, every p-bit window is 0; spectrum is all-zero except DC.
    for p in (2, 3, 5, 7):
        coeffs = atlas_zero["profiles"][p]["coeffs"]
        # Skip DC; everything else should equal the count of 0 at p (positive).
        # WHT of (N, 0, ..., 0) = (N, N, N, ..., N).
        if int(coeffs[1]) != int(coeffs[0]):
            if verbose:
                print(f"FAIL: zero-input WHT shape at p={p}")
            ok = False

    if verbose:
        print(f"spectral_atlas self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
