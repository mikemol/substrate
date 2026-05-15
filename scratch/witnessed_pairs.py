"""
witnessed_pairs.py — reformulate the architecture's ternary cells as
(pair, witness) operations.

The 6 unordered pairs of {D, C, S, W} × 2 possible witnesses each = 12 operations.

This isn't a new structure — it's a re-labeling of the 12 ternary cells in the
(held, enabled) state space:
  held axis ↔ WITNESS
  enabled axes (cardinality 2) ↔ PAIR

But the (pair, witness) framing is more semantically meaningful:
  - PAIR = the two axes that interact
  - WITNESS = the third axis providing validation/context

Crucially, the witness must come from the OPPOSITE PAIR under one of the 3
V₄ pairings. The 6 pairs partition into 3 pairings:
  α: {DC, SW}   (operational pair + workspace pair)
  β: {DS, CW}   (persistent pair + active pair)
  γ: {DW, CS}   (storage pair + process pair)

The 2 witnesses for pair P are exactly the 2 axes of P's opposite pair.

That gives the tetrahedron structure: 4 vertices (axes), 6 edges (pairs),
3 opposite-edge pairs (pairings), 12 edge-witness combinations (= A₄ order).
"""

from itertools import combinations
from collections import defaultdict

AXES = ['D', 'C', 'S', 'W']

# The 3 V₄ pairings — each splits 4 axes into 2 opposite pairs
PAIRINGS = {
    'α': ({'D', 'C'}, {'S', 'W'}),
    'β': ({'D', 'S'}, {'C', 'W'}),
    'γ': ({'D', 'W'}, {'C', 'S'}),
}

# V₄ swaps
V4_SWAPS = {
    'e': {a: a for a in AXES},
    'α': {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β': {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ': {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}


# ============================================================
# Build the 12 witnessed-pair operations
# ============================================================

def opposite_pair(pair, pairing):
    """Given a pair and the pairing it belongs to, return the opposite pair."""
    p1, p2 = pairing
    return p2 if pair == p1 else p1


def witnessed_pairs():
    """Enumerate all 12 (pair, witness) operations."""
    ops = []
    for pairing_name, (p1, p2) in PAIRINGS.items():
        for pair in [p1, p2]:
            opp = p2 if pair == p1 else p1
            for witness in sorted(opp):
                ops.append({
                    'pair': pair,
                    'witness': witness,
                    'pairing': pairing_name,
                    'opposite_pair': opp,
                    'name': f"{''.join(sorted(pair))}-witnessed-by-{witness}",
                    # Translate to (held, enabled) — held = witness, enabled = pair
                    'held': witness,
                    'enabled': frozenset(pair),
                })
    return ops


# ============================================================
# V₄ action on witnessed pairs
# ============================================================

def apply_swap_to_witnessed(op, swap_name):
    """Apply a V₄ swap to a (pair, witness) operation."""
    swap = V4_SWAPS[swap_name]
    new_pair = frozenset(swap[a] for a in op['pair'])
    new_witness = swap[op['witness']]
    return new_pair, new_witness


def v4_orbit_of(op):
    """Return the V₄-orbit of a witnessed-pair operation."""
    orbit = set()
    for swap in ['e', 'α', 'β', 'γ']:
        new_pair, new_witness = apply_swap_to_witnessed(op, swap)
        orbit.add((new_pair, new_witness))
    return orbit


# ============================================================
# Map existing chart operations into the witnessed-pair scheme
# ============================================================

# For each implemented op, identify (pair, witness) by inspecting its
# engagement profile from the matrix.
EXISTING_OPS_MAPPING = {
    # 3-axis (core) operations — these inhabit the 12 ternary cells
    'M11 interp / S5 apply': {
        'engaged_core': {'D', 'C', 'S'},
        'pair': frozenset({'D', 'C'}),
        'witness': 'S',
        'classification': 'DC-witnessed-by-S',
        'notes': 'data-compute reduction with state as advancement-witness',
    },
    'M_SPPF_witness_application': {
        'engaged_core': {'D', 'C', 'S'},
        'pair': frozenset({'D', 'C'}),
        'witness': 'S',
        'classification': 'DC-witnessed-by-S',
        'notes': 'data-compute relation narrowed by state-witness',
    },
    'M32 workspace_witness': {
        'engaged_core': {'D', 'C', 'W'},
        'pair': frozenset({'D', 'C'}),
        'witness': 'W',
        'classification': 'DC-witnessed-by-W',
        'notes': 'data-compute narrowed by workspace-witness',
    },
    'M5 chart memoization': {
        'engaged_core': {'D', 'C', 'S'},
        'pair': frozenset({'D', 'C'}),
        'witness': 'S',
        'classification': 'DC-witnessed-by-S',
        'notes': 'chart caches reductions; state-history validates cache',
    },
    'M_SPPF_BWT': {
        'engaged_core': {'D', 'C', 'S'},
        'pair': frozenset({'D', 'C'}),
        'witness': 'S',
        'classification': 'DC-witnessed-by-S',
        'notes': 'BWT of data structure, state confirms structural property',
    },
    'M32 workspace_driven_state': {
        'engaged_core': {'D', 'C', 'W'},  # actually engages all 4
        'pair': frozenset({'D', 'C'}),    # if we drop S as ambient
        'witness': 'W',
        'classification': 'DC-witnessed-by-W (closest, but engages all 4)',
        'notes': 'should be SW-witnessed-by-? but actually calls apply (DC)',
    },
}


# ============================================================
# Generate the matrix
# ============================================================

def main():
    print("=" * 78)
    print("  WITNESSED-PAIR REFORMULATION")
    print("=" * 78)
    print()
    print("  The 4-axis architecture's 12 ternary cells are precisely")
    print("  the 12 (pair, witness) operations of the tetrahedral structure:")
    print(f"    4 axes = vertices of the tetrahedron K_4")
    print(f"    6 pairs = edges of K_4")
    print(f"    3 pairings = opposite-edge classes (matchings of K_4)")
    print(f"    12 = edges × 2 vertices of opposite edge = |A_4|")
    print()

    ops = witnessed_pairs()

    # Group by pairing
    by_pairing = defaultdict(list)
    for op in ops:
        by_pairing[op['pairing']].append(op)

    print("=" * 78)
    print("  The 12 witnessed-pair operations, organized by pairing (V₄-orbit)")
    print("=" * 78)

    for pairing_name in ['α', 'β', 'γ']:
        p1, p2 = PAIRINGS[pairing_name]
        print(f"\n  Pairing {pairing_name}: {{{''.join(sorted(p1))}, {''.join(sorted(p2))}}}")
        print(f"  ─" * 38)
        for op in by_pairing[pairing_name]:
            pair_str = ''.join(sorted(op['pair']))
            opp_str = ''.join(sorted(op['opposite_pair']))
            held_enabled = f"({op['held']}, {{{','.join(sorted(op['enabled']))}}})"
            print(f"    {op['name']:<28}  pair={pair_str}  opp={opp_str}  signature={held_enabled}")

    print()
    print("  Each pairing contains 4 operations: 2 pairs × 2 witnesses.")
    print("  These 4 operations form a V₄-orbit under the group action.")
    print()

    # =====================
    # V₄ action verification
    # =====================
    print("=" * 78)
    print("  V₄ action on the witnessed-pair operations")
    print("=" * 78)

    # Show the V₄-orbit structure
    orbits = []
    seen = set()
    for op in ops:
        key = (frozenset(op['pair']), op['witness'])
        if key in seen:
            continue
        orbit = v4_orbit_of(op)
        for k in orbit:
            seen.add(k)
        orbits.append(orbit)

    print(f"\n  Number of V₄-orbits: {len(orbits)}")
    print(f"  Each orbit has {len(orbits[0])} elements (V₄ acts faithfully on each).")

    for i, orbit in enumerate(orbits, 1):
        print(f"\n  Orbit {i}:")
        for pair, witness in sorted(orbit, key=lambda x: (sorted(x[0]), x[1])):
            pair_str = ''.join(sorted(pair))
            print(f"    {pair_str}-witnessed-by-{witness}")

    print()
    print("  Observation: each V₄-orbit contains exactly the 4 (pair, witness)")
    print("  combinations belonging to ONE pairing. The pairings are the orbits.")

    # =====================
    # Existing chart ops — where do they land?
    # =====================
    print()
    print("=" * 78)
    print("  Existing operations mapped into the witnessed-pair framework")
    print("=" * 78)

    cell_population = defaultdict(list)
    for op_name, info in EXISTING_OPS_MAPPING.items():
        cell_population[info['classification']].append(op_name)

    print()
    print("  Cells populated by existing operations:\n")
    for cell, ops_in in sorted(cell_population.items()):
        print(f"    {cell}")
        for op_name in ops_in:
            print(f"      • {op_name}")

    print()
    print(f"  Cells touched by existing chart: {len(cell_population)} / 12")
    print(f"  Most operations cluster on DC-witnessed-by-S (apply / reduction with state witness).")
    print()

    # =====================
    # What the 12 mean operationally
    # =====================
    print("=" * 78)
    print("  Operational interpretation of the 12 witnessed-pair operations")
    print("=" * 78)

    INTERPRETATIONS = {
        'DC-witnessed-by-S': ('apply / reduce', 'data and compute interact (reduction); state advances as witness'),
        'DC-witnessed-by-W': ('memoize-on-workspace', 'data-compute reduction with workspace caching as witness'),
        'DS-witnessed-by-C': ('compute-validated state change', 'data-state evolution; compute confirms validity'),
        'DS-witnessed-by-W': ('workspace-receipt state change', 'data-state evolution; workspace logs receipt'),
        'DW-witnessed-by-C': ('compute-validated store', 'data goes to workspace iff compute confirms'),
        'DW-witnessed-by-S': ('logged store', 'data-to-workspace transfer with state log as witness'),
        'CS-witnessed-by-D': ('data-invariant compute step', 'compute advances state; data invariant witnesses'),
        'CS-witnessed-by-W': ('workspace-scratch compute', 'compute advances state; workspace holds intermediate'),
        'CW-witnessed-by-D': ('data-validated memo', 'compute-workspace coupling; data witnesses correctness'),
        'CW-witnessed-by-S': ('state-versioned memo', 'compute-workspace memo with state version stamp'),
        'SW-witnessed-by-D': ('data-asserted checkpoint', 'state-workspace snapshot; data invariant attached'),
        'SW-witnessed-by-C': ('compute-asserted checkpoint', 'state-workspace snapshot; compute proof attached'),
    }

    print()
    for op in ops:
        cell_str = op['name']
        if cell_str in INTERPRETATIONS:
            name, desc = INTERPRETATIONS[cell_str]
            print(f"  {cell_str}")
            print(f"    name: {name}")
            print(f"    role: {desc}")
            print()


if __name__ == "__main__":
    main()
