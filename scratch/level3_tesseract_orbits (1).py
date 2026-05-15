"""
level3_tesseract_orbits.py — enumerate orbits of GL(4, F_2) ≅ A_8 acting
on the 2^15 = 32768 subsets of the 15 points of PG(3, F_2).

At Level 2 (Fano), GL(3, F_2) acts on 2^7 = 128 subsets of 7 points,
giving 10 orbits. The orbits correspond to:
  - empty / full (1 each)
  - singletons / complement-of-singleton (1 each)
  - pairs / complement-of-pair (1 each)
  - collinear vs noncollinear triples + complements (2 + 2)

At Level 3, we expect richer orbit structure because PG(3, F_2) has more
incidence types (lines, planes, dual structures).

The 16 Walsh-Hadamard readings at Level 3 are indexed by 4-bit signatures.
The orbit structure should reveal whether there are 3 axes (as at Level 2,
named data/compute/state) or genuinely 4 axes at Level 3.
"""

import numpy as np
from collections import defaultdict, deque

# ============================================================
# F_2^4 setup
# ============================================================

N = 4                     # dimension
NUM_PTS = 2**N - 1        # 15 nonzero F_2^4 vectors
NUM_SUBSETS = 2**NUM_PTS  # 32768 subsets

# ============================================================
# Generators for GL(4, F_2) (3 matrices generate the full group)
# ============================================================

def gen_transposition():
    """(1, 2) transposition: swap rows 0 and 1."""
    M = np.eye(N, dtype=np.uint8)
    M[[0, 1]] = M[[1, 0]].copy()
    return M

def gen_cycle():
    """N-cycle: e_0 -> e_1 -> ... -> e_{N-1} -> e_0."""
    M = np.zeros((N, N), dtype=np.uint8)
    for i in range(N):
        M[(i + 1) % N, i] = 1
    return M

def gen_shear():
    """Elementary shear: I + E_{0,1} (row 0 gets row 1 added)."""
    M = np.eye(N, dtype=np.uint8)
    M[0, 1] = 1
    return M

GENERATORS = [gen_transposition(), gen_cycle(), gen_shear()]


def matrix_to_point_perm(M):
    """Compute the permutation on points 0..14 induced by M."""
    perm = np.zeros(NUM_PTS, dtype=np.int32)
    for i in range(NUM_PTS):
        idx = i + 1  # nonzero vector index
        v = np.array([(idx >> j) & 1 for j in range(N)], dtype=np.uint8)
        Mv = (M @ v) % 2
        new_idx = sum(int(Mv[j]) << j for j in range(N))
        perm[i] = new_idx - 1
    return perm


PERMS = [matrix_to_point_perm(g) for g in GENERATORS]


def apply_perm_to_subset(s, perm):
    """Apply permutation to a subset represented as int."""
    new_s = 0
    for j in range(NUM_PTS):
        if s & (1 << j):
            new_s |= (1 << int(perm[j]))
    return new_s


# ============================================================
# Orbit enumeration via BFS
# ============================================================

def compute_orbits():
    visited = np.zeros(NUM_SUBSETS, dtype=bool)
    orbits = []

    for start in range(NUM_SUBSETS):
        if visited[start]:
            continue
        orbit = []
        queue = deque([start])
        visited[start] = True
        while queue:
            x = queue.popleft()
            orbit.append(x)
            for perm in PERMS:
                y = apply_perm_to_subset(x, perm)
                if not visited[y]:
                    visited[y] = True
                    queue.append(y)
        orbits.append(orbit)

    return orbits


# ============================================================
# Walsh-Hadamard at Level 3 (16 readings)
# ============================================================

def wht_reading(subset, sig):
    """Walsh-Hadamard reading of subset at signature sig.

    Reading at signature s = sum_{i in subset} (-1)^{s · binary(i+1)}.
    """
    total = 0
    for j in range(NUM_PTS):
        if subset & (1 << j):
            idx = j + 1  # nonzero F_2^4 vector
            dot = bin(sig & idx).count('1') % 2
            total += -1 if dot else 1
    return total


def compute_all_wht_readings(subset):
    """Compute all 16 WHT readings for a subset."""
    return np.array([wht_reading(subset, s) for s in range(2**N)])


# ============================================================
# Run and analyze
# ============================================================

def main():
    print("=" * 76)
    print("  Level-3 tesseract: orbits of GL(4, F_2) ≅ A_8 on 2^15 subsets")
    print("=" * 76)
    print()
    print(f"Number of points: {NUM_PTS}")
    print(f"Number of subsets: {NUM_SUBSETS}")
    print(f"Number of generators: {len(PERMS)}")
    print()

    # Verify generators induce permutations
    for i, perm in enumerate(PERMS):
        unique_count = len(set(perm.tolist()))
        print(f"  Generator {i+1}: induces permutation, range [{perm.min()}, {perm.max()}], "
              f"unique={unique_count}")
    print()

    print("Computing orbits...")
    orbits = compute_orbits()
    print(f"Total orbits: {len(orbits)}")
    print()

    # Group orbits by subset size (Hamming weight)
    by_size = defaultdict(list)
    for orbit in orbits:
        rep = orbit[0]
        size = bin(rep).count('1')
        by_size[size].append(orbit)

    print("=" * 76)
    print("  Orbit structure by subset size")
    print("=" * 76)
    print()
    print(f"  {'size':>4}  {'# orbits':>9}  {'orbit sizes':>40}")
    print(f"  {'-'*4}  {'-'*9}  {'-'*40}")

    total_check = 0
    for size in sorted(by_size.keys()):
        orbits_of_size = by_size[size]
        orbit_sizes = sorted([len(o) for o in orbits_of_size])
        size_str = str(orbit_sizes)
        if len(size_str) > 40:
            size_str = size_str[:37] + "..."
        total_check += sum(orbit_sizes)
        print(f"  {size:>4}  {len(orbits_of_size):>9}  {size_str:>40}")

    print()
    print(f"  Total subsets in orbits: {total_check} (should be {NUM_SUBSETS})")
    print()

    # Show structure of small orbits
    print("=" * 76)
    print("  Representative subsets at each size with their structure")
    print("=" * 76)
    print()

    for size in sorted(by_size.keys()):
        if size > 8:
            continue  # complements of smaller sizes
        orbits_of_size = sorted(by_size[size], key=lambda o: len(o))
        for orbit in orbits_of_size:
            rep = orbit[0]
            pts = [i + 1 for i in range(NUM_PTS) if rep & (1 << i)]  # 1-indexed for readability
            orbit_size = len(orbit)
            print(f"  size={size}, orbit size={orbit_size:5d}, rep points={pts}")
            # WHT readings of representative
            readings = compute_all_wht_readings(rep)
            print(f"      WHT readings = {readings.tolist()}")
        print()

    # Comparison to Level 2
    print("=" * 76)
    print("  Comparison: Level 2 vs Level 3")
    print("=" * 76)
    print()
    print(f"  {'':>10}  {'Level 2':>10}  {'Level 3':>10}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*10}")
    print(f"  {'points':>10}  {'7':>10}  {NUM_PTS:>10}")
    print(f"  {'subsets':>10}  {'128':>10}  {NUM_SUBSETS:>10}")
    print(f"  {'|G|':>10}  {'168':>10}  {'20160':>10}")
    print(f"  {'orbits':>10}  {'10':>10}  {len(orbits):>10}")
    print()
    print(f"  Level 2 orbit-count ratio: 10 / 128 = {10/128:.4f}")
    print(f"  Level 3 orbit-count ratio: {len(orbits)} / {NUM_SUBSETS} = {len(orbits)/NUM_SUBSETS:.4f}")
    print()
    print(f"  Level 2 / Level 3 ratio of orbit counts: {len(orbits)/10:.2f}x")


if __name__ == "__main__":
    main()
