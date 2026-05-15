"""
v4_klein_four_coverage.py — apply the V₄/S₃ structure to find which
architectural axis-combinations we haven't explored.

With 4 axes (D, C, S, W = data, compute, state, scratch), the natural
symmetry group is S₄ of order 24. S₄ has V₄ (Klein four-group) as its
unique nontrivial normal subgroup; the quotient S₄/V₄ ≅ S₃ acts on the
3 natural pairings of 4 items.

The 3 pairings of {D, C, S, W}:
  α: {D, C} + {S, W}  — operational pair vs workspace pair
  β: {D, S} + {C, W}  — persistent pair vs active pair
  γ: {D, W} + {C, S}  — storage pair vs process pair

V₄ has 4 elements:
  e         — identity
  (DC)(SW)  — swap within α's pairs (preserves α)
  (DS)(CW)  — swap within β's pairs (preserves β)
  (DW)(CS)  — swap within γ's pairs (preserves γ)

Each non-identity V₄ element preserves exactly one pairing. V₄-orbits
on moves group together moves that are equivalent under the natural
pair-swap symmetries.
"""

from collections import defaultdict
from itertools import combinations

AXES = ['D', 'C', 'S', 'W']

# The three V₄ non-identity elements as axis swaps
V4_NONTRIVIAL = {
    'α-swap (DC)(SW)': {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β-swap (DS)(CW)': {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ-swap (DW)(CS)': {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}

# The three pairings
PAIRINGS = {
    'α': [{'D', 'C'}, {'S', 'W'}],
    'β': [{'D', 'S'}, {'C', 'W'}],
    'γ': [{'D', 'W'}, {'C', 'S'}],
}


# ============================================================
# Operational moves from the audit (held axis → enabled axes)
# ============================================================

OPERATIONAL_MOVES = [
    # (name, held_axis, frozenset of enabled axes)
    ('M5',  'D', frozenset({'C', 'S'})),
    ('M9',  'D', frozenset({'C', 'S'})),
    ('M11', 'D', frozenset({'C'})),
    ('M13', 'D', frozenset({'S'})),
    ('M14', 'D', frozenset({'S'})),
    ('M16', 'C', frozenset({'D'})),
    ('M17', 'C', frozenset({'D'})),
    ('M_SPPF_R2N',                'D', frozenset({'C'})),
    ('M_SPPF_one_hot',            'D', frozenset({'C'})),
    ('M_SPPF_witness_application','S', frozenset({'C', 'D'})),
    ('M_SPPF_BWT',                'D', frozenset({'C'})),
    ('M_SPPF_integer_path',       'D', frozenset({'C'})),
    ('M_SPPF_morton_heap',        'D', frozenset({'C'})),
    ('M_SPPF_fat_node_k4',        'D', frozenset({'C'})),
    ('M_SPPF_GF2k',               'C', frozenset({'D'})),
    ('M_SPPF_subtree_fingerprints','D', frozenset({'C'})),
]


# ============================================================
# Apply V₄ swaps to moves
# ============================================================

def apply_swap(move_tuple, swap):
    """Apply a V₄ swap to a (held, enabled) tuple."""
    _, held, enabled = move_tuple
    new_held = swap.get(held, held)
    new_enabled = frozenset(swap.get(a, a) for a in enabled)
    return (new_held, new_enabled)


def v4_orbit_of(held, enabled):
    """Return all 4 V₄-equivalent (held, enabled) pairs for a move."""
    orbit = {(held, frozenset(enabled))}
    for swap in V4_NONTRIVIAL.values():
        new_held = swap.get(held, held)
        new_enabled = frozenset(swap.get(a, a) for a in enabled)
        orbit.add((new_held, new_enabled))
    return frozenset(orbit)


# ============================================================
# Build the full enumeration of possible (held, enabled) signatures
# ============================================================

def all_move_signatures():
    """Enumerate all possible (held, enabled) where held ∉ enabled."""
    signatures = []
    for held in AXES:
        for k in [1, 2, 3]:  # 1 to 3 enabled axes
            other = [a for a in AXES if a != held]
            for combo in combinations(other, k):
                signatures.append((held, frozenset(combo)))
    return signatures


# ============================================================
# Classify each operational move by V₄-orbit and pairing
# ============================================================

def classify_move_by_pairing(held, enabled):
    """Find the pairing under which the move's structure is cleanest.

    Heuristic: the pairing is 'compatible' if the held axis is alone in
    its pair (workspace position) and the enabled axes are together in
    the other pair (operational position). Failing that, the pairing
    where held and at least one enabled are in the same pair.
    """
    compatibility = {}
    for name, pairs in PAIRINGS.items():
        # Find the pair containing held
        held_pair = next(p for p in pairs if held in p)
        other_pair = next(p for p in pairs if held not in p)

        # How many enabled are in the held's pair vs other pair?
        enabled_in_held_pair = len(enabled & held_pair)
        enabled_in_other_pair = len(enabled & other_pair)

        compatibility[name] = (enabled_in_other_pair, enabled_in_held_pair)

    # Best pairing: most enabled in OTHER pair (held isolated in workspace)
    best = max(compatibility.items(), key=lambda x: (x[1][0], -x[1][1]))
    return best[0], compatibility


# ============================================================
# Coverage analysis
# ============================================================

def main():
    print("=" * 76)
    print("  V₄ orbit coverage analysis of the M-history")
    print("=" * 76)
    print()

    # Compute V₄ orbits of all operational moves
    orbits = defaultdict(list)
    for name, held, enabled in OPERATIONAL_MOVES:
        orbit_key = v4_orbit_of(held, enabled)
        orbits[orbit_key].append((name, held, enabled))

    print(f"  Number of V₄-orbits with representatives: {len(orbits)}")
    print(f"  Total operational moves: {len(OPERATIONAL_MOVES)}")
    print()

    print("=" * 76)
    print("  V₄-orbit population (4 directions per orbit)")
    print("=" * 76)
    print()

    for orbit_key, moves_in_orbit in sorted(orbits.items(),
                                            key=lambda x: -len(x[1])):
        # Show the 4 V₄-equivalent directions
        directions = sorted(orbit_key)
        print(f"  V₄-orbit: {{{', '.join(f'{h}→{set(e)}' for h, e in directions)}}}")
        print(f"  Orbit size: {len(orbit_key)} directions, {len(moves_in_orbit)} moves populated")

        # Count populations per direction
        pop_by_direction = defaultdict(list)
        for name, held, enabled in moves_in_orbit:
            pop_by_direction[(held, frozenset(enabled))].append(name)

        for direction in directions:
            count = len(pop_by_direction.get(direction, []))
            held, enabled = direction
            marker = '✓' if count > 0 else '·'
            names = ', '.join(pop_by_direction.get(direction, [])) or '(empty)'
            print(f"    [{marker}] {held}→{set(enabled)}: {count} move(s)  {names}")
        print()

    # Coverage by axis-as-carrier
    print("=" * 76)
    print("  Axis-as-scratch-carrier coverage")
    print("=" * 76)
    print()

    by_carrier = defaultdict(list)
    for name, held, enabled in OPERATIONAL_MOVES:
        by_carrier[held].append(name)

    print(f"  {'axis':>5}  {'count':>6}  {'examples':<60}")
    print(f"  {'-'*5}  {'-'*6}  {'-'*60}")
    for axis in AXES:
        count = len(by_carrier.get(axis, []))
        examples = ', '.join(by_carrier.get(axis, [])[:3])
        if count > 3:
            examples += f", ... (+{count-3} more)"
        if count == 0:
            examples = '(NONE — unexplored!)'
        print(f"  {axis:>5}  {count:>6}  {examples:<60}")
    print()

    # Coverage by pairing
    print("=" * 76)
    print("  Pairing compatibility coverage")
    print("=" * 76)
    print()

    by_pairing = defaultdict(list)
    for name, held, enabled in OPERATIONAL_MOVES:
        best_pairing, _ = classify_move_by_pairing(held, enabled)
        by_pairing[best_pairing].append(name)

    print(f"  {'pairing':>8}  {'pairs':>20}  {'count':>6}  {'fraction':>10}")
    print(f"  {'-'*8}  {'-'*20}  {'-'*6}  {'-'*10}")
    total = len(OPERATIONAL_MOVES)
    for p_name, pairs in PAIRINGS.items():
        count = len(by_pairing.get(p_name, []))
        pair_str = f"{set(pairs[0])} + {set(pairs[1])}"
        print(f"  {p_name:>8}  {pair_str:>20}  {count:>6}  {100*count/total:>8.0f}%")
    print()

    # Full coverage matrix
    print("=" * 76)
    print("  Complete coverage matrix: all possible move-signatures")
    print("=" * 76)
    print()

    # Group by V₄-orbit and tabulate
    all_orbits_full = defaultdict(set)
    for held in AXES:
        for k in [1, 2, 3]:
            for combo in combinations([a for a in AXES if a != held], k):
                orbit = v4_orbit_of(held, frozenset(combo))
                all_orbits_full[orbit].add((held, frozenset(combo)))

    populated_dirs = set()
    for name, held, enabled in OPERATIONAL_MOVES:
        populated_dirs.add((held, frozenset(enabled)))

    print(f"  Total V₄-orbits in the full signature space: {len(all_orbits_full)}")
    print(f"  Total possible (held, enabled) signatures: {sum(len(o) for o in all_orbits_full.values())}")
    print(f"  Populated signatures: {len(populated_dirs)}")
    print(f"  Empty signatures: {sum(len(o) for o in all_orbits_full.values()) - len(populated_dirs)}")
    print()

    # Show empty V₄-orbits (entirely under-explored equivalence classes)
    print("=" * 76)
    print("  V₄-orbits with NO representative populated (entirely unexplored)")
    print("=" * 76)
    print()

    empty_orbits = []
    for orbit, directions in all_orbits_full.items():
        if not directions & populated_dirs:
            empty_orbits.append(directions)

    for directions in empty_orbits:
        # Show one representative direction per orbit
        sample = sorted(directions)[0]
        held, enabled = sample
        print(f"  Hold on {held}, enable {set(enabled)}  (and 3 V₄-equivalent directions)")
    print()
    print(f"  Total fully-empty V₄-orbits: {len(empty_orbits)}")
    print()

    # Partially populated V₄-orbits (under-represented within orbit)
    print("=" * 76)
    print("  Partially-populated V₄-orbits (asymmetric exploration)")
    print("=" * 76)
    print()

    partial_orbits = []
    for orbit, directions in all_orbits_full.items():
        populated_in_orbit = directions & populated_dirs
        unpopulated_in_orbit = directions - populated_dirs
        if populated_in_orbit and unpopulated_in_orbit:
            partial_orbits.append((populated_in_orbit, unpopulated_in_orbit))

    for populated, unpopulated in partial_orbits:
        pop_sample = sorted(populated)[0]
        print(f"  Populated: {pop_sample[0]}→{set(pop_sample[1])} (and possibly {len(populated)-1} V₄-equivalent)")
        for direction in sorted(unpopulated):
            held, enabled = direction
            print(f"    Missing V₄-twin: {held}→{set(enabled)}")
        print()


if __name__ == "__main__":
    main()
