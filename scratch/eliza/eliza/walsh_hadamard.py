"""Eliza.WalshHadamard — Walsh-Hadamard Transform + sliding p-bit
window counts at prime widths for the GG-arc.

Per [[168-tower-as-fanout]]: GL(3, F₂) Sylow primes are 2, 3, 7;
GL(4, F₂) adds 5. The substrate's prime structure is {2, 3, 5, 7}
— exactly the small primes for which sliding-bit-width analysis
yields gauge-aligned spectral readings.

For F₂-valued signals the natural Fourier is the WHT: for a
2ⁿ-dimensional count vector v, WHT(v)[k] = Σ_x v[x] · (−1)^⟨k, x⟩
where ⟨·,·⟩ is the standard F₂-bilinear form. The transform is
self-inverse up to scaling: WHT(WHT(v)) = 2ⁿ · v.

Sliding window: for prime width p, slide a p-bit window at every
bit position (NOT byte-aligned) and count occurrences of each
2ᵖ symbol. The resulting count vector is the "p-bit symbol
distribution" of the input.

Per the user 2026-05-21: 'sniffing at prime numbers of bits ...
producing a multidimensional profile of the input over a small
fourier series'.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import numpy as np


# --- Walsh-Hadamard Transform ----------------------------------------


def walsh_hadamard(v: np.ndarray) -> np.ndarray:
    """In-place Sylvester WHT of a 2ⁿ-length integer vector.

    Returns a NEW array; original unchanged. WHT is self-inverse up
    to scaling: walsh_hadamard(walsh_hadamard(v)) == 2ⁿ · v.
    """
    n = len(v)
    if n & (n - 1) != 0:
        raise ValueError(f"length {n} must be a power of 2")
    out = v.astype(np.int64, copy=True)
    h = 1
    while h < n:
        for i in range(0, n, h * 2):
            for j in range(i, i + h):
                x = out[j]
                y = out[j + h]
                out[j] = x + y
                out[j + h] = x - y
        h *= 2
    return out


def inverse_walsh_hadamard(v: np.ndarray) -> np.ndarray:
    """Inverse WHT (same transform, divided by length)."""
    n = len(v)
    return walsh_hadamard(v) // n


# --- Bit-stream extraction -------------------------------------------


def bits_msb_first(data: bytes) -> np.ndarray:
    """Return the MSB-first bit array of `data` as int8."""
    if not data:
        return np.zeros(0, dtype=np.int8)
    arr = np.frombuffer(data, dtype=np.uint8)
    # Unpack each byte to 8 bits in MSB-first order.
    return np.unpackbits(arr).astype(np.int8)


def sliding_window_counts(bits: np.ndarray, p: int) -> np.ndarray:
    """Count occurrences of each 2ᵖ p-bit symbol over sliding bit
    windows (stride 1, not byte-aligned).

    Returns int64 array of length 2ᵖ.
    """
    counts = np.zeros(1 << p, dtype=np.int64)
    n = len(bits)
    if p <= 0 or p > 16 or n < p:
        return counts
    # Vectorise via numpy: build the (n - p + 1, p) window matrix,
    # convert each row to an integer.
    # Use a stride trick to avoid O(n*p) loop where possible.
    # For small p we can compute via bit-shifts.
    windows = np.lib.stride_tricks.sliding_window_view(bits.astype(np.int64),
                                                          p)
    # Combine bits MSB-first into an integer.
    weights = (1 << np.arange(p - 1, -1, -1, dtype=np.int64))
    sym = (windows * weights).sum(axis=1)
    # Bin counts.
    counts = np.bincount(sym, minlength=(1 << p))
    return counts.astype(np.int64)


# --- Spectrum -------------------------------------------------------


def prime_spectrum(data: bytes, p: int) -> Dict[str, np.ndarray]:
    """Compute the p-bit spectrum of `data`:
      counts: int64[2ᵖ] — sliding-window symbol counts.
      coeffs: int64[2ᵖ] — WHT of counts (Fourier-like coefficients).
    """
    bits = bits_msb_first(data)
    counts = sliding_window_counts(bits, p)
    coeffs = walsh_hadamard(counts)
    return {"counts": counts, "coeffs": coeffs}


def multi_prime_profile(
    data: bytes, primes: Iterable[int] = (2, 3, 5, 7),
) -> Dict[int, Dict[str, np.ndarray]]:
    """Compute the multi-prime spectral atlas {p: spectrum(p)}."""
    return {p: prime_spectrum(data, p) for p in primes}


# --- Self-check -----------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. WHT length check.
    try:
        walsh_hadamard(np.array([1, 2, 3], dtype=np.int64))
        if verbose:
            print("FAIL: WHT accepted non-power-of-2 length")
        ok = False
    except ValueError:
        pass

    # 2. WHT involution: WHT(WHT(v)) = N · v.
    rng = np.random.default_rng(7)
    for N in (1, 2, 4, 8, 16, 32, 128):
        v = rng.integers(-100, 100, size=N, dtype=np.int64)
        t1 = walsh_hadamard(v)
        t2 = walsh_hadamard(t1)
        if not np.array_equal(t2, v * N):
            if verbose:
                print(f"FAIL: WHT involution at N={N}")
            ok = False

    # 3. WHT(δ_0) = all-ones.
    for N in (4, 8, 32):
        d = np.zeros(N, dtype=np.int64)
        d[0] = 1
        t = walsh_hadamard(d)
        if not np.all(t == 1):
            if verbose:
                print(f"FAIL: WHT(δ_0) ≠ ones at N={N}")
            ok = False

    # 4. WHT(ones) = N · δ_0.
    for N in (4, 8, 32):
        ones = np.ones(N, dtype=np.int64)
        t = walsh_hadamard(ones)
        expected = np.zeros(N, dtype=np.int64)
        expected[0] = N
        if not np.array_equal(t, expected):
            if verbose:
                print(f"FAIL: WHT(ones) ≠ N · δ_0 at N={N}")
            ok = False

    # 5. bits_msb_first round-trip.
    data = bytes([0xAB, 0x12])
    bits = bits_msb_first(data)
    expected_bits = [1, 0, 1, 0, 1, 0, 1, 1,
                     0, 0, 0, 1, 0, 0, 1, 0]
    if list(bits) != expected_bits:
        if verbose:
            print(f"FAIL: bits_msb_first = {list(bits)}")
        ok = False

    # 6. Sliding count: known small case. data = "10101011 00010010"
    #    p=2: windows = 10, 01, 10, 01, 10, 01, 11, 10, 00, 00, 00, 10,
    #                   01, 00, 01, 10, ... 15 windows total.
    counts = sliding_window_counts(bits, 2)
    if int(counts.sum()) != len(bits) - 1:
        if verbose:
            print(f"FAIL: sliding count sum {counts.sum()} ≠ {len(bits)-1}")
        ok = False

    # 7. Sliding count: p=8 on aligned bytes recovers byte frequencies
    #    at the byte-aligned subset.
    data = bytes(range(64))
    bits = bits_msb_first(data)
    counts8 = sliding_window_counts(bits, 8)
    # Total windows = 64*8 - 7 = 505.
    if int(counts8.sum()) != len(bits) - 7:
        if verbose:
            print(f"FAIL: p=8 sliding sum {counts8.sum()}")
        ok = False

    # 8. multi_prime_profile shape.
    data = bytes(range(128))
    profile = multi_prime_profile(data, primes=(2, 3, 5, 7))
    for p in (2, 3, 5, 7):
        spectrum = profile[p]
        if spectrum["counts"].shape[0] != (1 << p):
            if verbose:
                print(f"FAIL: spectrum p={p} shape {spectrum['counts'].shape}")
            ok = False

    if verbose:
        print(f"walsh_hadamard self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
