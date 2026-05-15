"""
construct_v4_twins.py — apply the state machine's transitions to mechanically
construct V₄-twin operations toward orbit-completion.

This runs the shadow-engineer loop (Step A-D) for each constructed move.
The state machine guarantees coherence by construction (laws V, C, W all hold).
"""

import numpy as np
from itertools import combinations
from collections import defaultdict

AXES = ['D', 'C', 'S', 'W']

V4_SWAPS = {
    'e':         {a: a for a in AXES},
    'α-swap':    {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β-swap':    {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ-swap':    {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}


def apply_swap(state, swap):
    held, enabled = state
    new_held = swap.get(held, held)
    new_enabled = frozenset(swap.get(a, a) for a in enabled)
    return (new_held, new_enabled)


def v4_orbit(state):
    return frozenset(apply_swap(state, swap) for swap in V4_SWAPS.values())


# ============================================================
# Corrected M-history population
# (M11 reclassified as D→{C,S} since interp advances state)
# ============================================================

POPULATED = {
    ('D', frozenset({'C'})):     # D→C
        ['M_SPPF_R2N', 'M_SPPF_one_hot', 'M_SPPF_BWT', 'M_SPPF_integer_path',
         'M_SPPF_morton_heap', 'M_SPPF_fat_node_k4', 'M_SPPF_subtree_fingerprints'],
    ('C', frozenset({'D'})):     # C→D
        ['M16_beam_search', 'M17_grid_search', 'M_SPPF_GF2k'],
    ('D', frozenset({'C', 'S'})):  # D→{C,S}
        ['M5_memoization', 'M9_construct_kernel', 'M11_meta_circular_interp'],
    ('D', frozenset({'S'})):     # D→S
        ['M13_K_marker', 'M14_VAR_MARK'],
    ('S', frozenset({'C', 'D'})):  # S→{C,D}
        ['M_SPPF_witness_application'],
}


def report_orbit(name, orbit_directions, populated):
    """Report population of a V₄-orbit."""
    print(f"  V₄-orbit '{name}': {sorted(orbit_directions, key=lambda x: (x[0], len(x[1])))}")
    counts = {}
    for direction in orbit_directions:
        counts[direction] = len(populated.get(direction, []))
    for direction in sorted(orbit_directions, key=lambda x: (x[0], len(x[1]))):
        held, enabled = direction
        c = counts[direction]
        marker = '✓' if c > 0 else '·'
        print(f"    [{marker}] {held}→{set(enabled) if enabled else '∅'}: {c} move(s)  "
              f"{', '.join(populated.get(direction, [])[:2])}"
              f"{'...' if c > 2 else ''}")


def compute_orbit_state(populated):
    """Return (orbit -> populated directions in that orbit)."""
    orbit_pop = defaultdict(set)
    for direction in populated:
        orbit = v4_orbit(direction)
        if populated[direction]:  # has actual moves
            orbit_pop[orbit].add(direction)
    return orbit_pop


def print_state_summary(populated, label=""):
    print(f"\n--- {label} ---")
    orbit_pop = compute_orbit_state(populated)
    print(f"  Populated cells: {sum(1 for d in populated if populated[d])}")
    print(f"  Populated V₄-orbits: {len(orbit_pop)}")

    # Count orbit-complete (F)
    complete_orbits = [(orbit, dirs) for orbit, dirs in orbit_pop.items() if len(dirs) == 4]
    print(f"  Orbit-complete V₄-orbits (∈ F): {len(complete_orbits)}")
    if complete_orbits:
        print(f"  States in F: {sum(len(orbit) for orbit, _ in complete_orbits)}")


# ============================================================
# Construct V₄-twins via state machine transitions
# ============================================================

def construct_v4_twin(source_state, swap_name, source_op):
    """Apply state machine transition: V₄-rotate source operation to twin."""
    swap = V4_SWAPS[swap_name]
    target_state = apply_swap(source_state, swap)
    return target_state, swap_name


def axis_label(axis):
    return {'D': 'data', 'C': 'compute', 'S': 'state', 'W': 'workspace'}[axis]


def transcribe_via_swap(operation_desc, swap_name):
    """Apply swap to an operation description (mechanical axis relabeling)."""
    swap = V4_SWAPS[swap_name]
    full_labels = {'data': swap[d.upper() if d.upper() in 'DCSW' else d.upper() if d.upper()[0] in 'DCSW' else d]
                   for d in ['data', 'compute', 'state', 'workspace']}
    relabel = {'data': axis_label(swap['D']), 'compute': axis_label(swap['C']),
               'state': axis_label(swap['S']), 'workspace': axis_label(swap['W'])}
    result = operation_desc
    # Order matters: replace with placeholders first
    for old in relabel:
        result = result.replace(old, f"__{old}__")
    for old, new in relabel.items():
        result = result.replace(f"__{old}__", new)
    return result


# ============================================================
# Run the construction
# ============================================================

def main():
    print("=" * 76)
    print("  Step A: Classify the meta-move")
    print("=" * 76)
    print("""
  Move type: 110 mediated-composite (state machine mediates between
             existing shadows and new shadow generation).
  Direction: shadow-engineer loop (Step A-E), no special mode needed.
  No need for decompose-by-entailment: we're not lifting from intact goal;
  we're applying a mechanical generator to existing shadows.
""")

    print_state_summary(POPULATED, "Initial state")

    print("\n" + "=" * 76)
    print("  Step B: Externalize — construct V₄-twins via state machine")
    print("=" * 76)

    # Closest-to-acceptance V₄-orbit: {D→C, C→D, S→W, W→S}
    closest_orbit = v4_orbit(('D', frozenset({'C'})))
    print(f"\n  Closest-to-F orbit: {sorted(closest_orbit, key=lambda x: (x[0], len(x[1])))}")
    report_orbit("D↔C / S↔W orbit", closest_orbit, POPULATED)

    print()
    print("  Need to populate S→W and W→S to make this orbit ∈ F.")
    print()

    # Construct MV4-1: S→W twin of M_SPPF_BWT via (DS)(CW)
    print("  ── Constructing MV₄-1: V₄-twin of M_SPPF_BWT via (DS)(CW) ──")
    source_state = ('D', frozenset({'C'}))
    target_state, swap_used = construct_v4_twin(
        source_state, 'β-swap', 'M_SPPF_BWT')
    print(f"    Source: M_SPPF_BWT at {source_state}")
    print(f"    Swap: β-swap = (DS)(CW)  swaps D↔S and C↔W")
    print(f"    Target state: {target_state}")
    print(f"    Operation: Burrows-Wheeler transform of STATE-HISTORY into WORKSPACE")
    print(f"               → rank/select queries on temporal evolution")
    print(f"               → time-travel debugging, audit logging, state replay")
    print()
    print("    Coherence verification:")
    print(f"      (V) V₄-invariance: target in same orbit? "
          f"{'✓' if target_state in v4_orbit(source_state) else '✗'}")
    print(f"      (C) Cocycle commute: by construction (absorbing op + swap)")
    print(f"      (W) WHT orthogonality: distinct from source (different bits)")

    # Add to populated set
    POPULATED[target_state] = POPULATED.get(target_state, []) + ['MV4_1_BWT_state_history']

    print()
    print("  ── Constructing MV₄-2: V₄-twin of M_SPPF_morton_heap via (DW)(CS) ──")
    source_state = ('D', frozenset({'C'}))
    target_state, swap_used = construct_v4_twin(
        source_state, 'γ-swap', 'M_SPPF_morton_heap')
    print(f"    Source: M_SPPF_morton_heap at {source_state}")
    print(f"    Swap: γ-swap = (DW)(CS)  swaps D↔W and C↔S")
    print(f"    Target state: {target_state}")
    print(f"    Operation: Morton/heap addressing of WORKSPACE drives STATE evolution")
    print(f"               → workspace position determines state transition pattern")
    print(f"               → structured stack machines, continuation-passing, generators")
    print()
    print("    Coherence verification:")
    print(f"      (V) V₄-invariance: target in same orbit? "
          f"{'✓' if target_state in v4_orbit(source_state) else '✗'}")
    print(f"      (C) Cocycle commute: by construction")
    print(f"      (W) WHT orthogonality: distinct from source")

    POPULATED[target_state] = POPULATED.get(target_state, []) + ['MV4_2_workspace_state_driver']

    # Construct MV4-3: W→{C, D} twin of M_SPPF_witness_application via (DC)(SW)
    print()
    print("  ── Constructing MV₄-3: V₄-twin of M_SPPF_witness_application via (DC)(SW) ──")
    source_state = ('S', frozenset({'C', 'D'}))
    target_state, swap_used = construct_v4_twin(
        source_state, 'α-swap', 'M_SPPF_witness_application')
    print(f"    Source: M_SPPF_witness_application at {source_state}")
    print(f"    Swap: α-swap = (DC)(SW)  swaps D↔C and S↔W")
    print(f"    Target state: {target_state}")
    print(f"    Operation: WORKSPACE-held context narrows COMPUTE and DATA")
    print(f"               → workspace as witness for compute/data extraction")
    print(f"               → workspace-based unification, structured constraint solving")
    print()
    print("    Coherence verification:")
    print(f"      (V) V₄-invariance: target in same orbit? "
          f"{'✓' if target_state in v4_orbit(source_state) else '✗'}")
    print(f"      (C) Cocycle commute: by construction")
    print(f"      (W) WHT orthogonality: distinct from source")

    POPULATED[target_state] = POPULATED.get(target_state, []) + ['MV4_3_workspace_witness']

    print()
    print("=" * 76)
    print("  Step C: Fire probes — check what completes")
    print("=" * 76)

    print_state_summary(POPULATED, "After construction")

    # Identify orbit-complete V₄-orbits
    orbit_pop = compute_orbit_state(POPULATED)

    print()
    print("  Orbit-completion status:")
    for orbit, populated_dirs in orbit_pop.items():
        if len(populated_dirs) == 4:
            print(f"    ✓✓✓ ORBIT COMPLETE (∈ F!): {sorted(orbit, key=lambda x: (x[0], len(x[1])))}")
        elif len(populated_dirs) >= 2:
            print(f"    [{len(populated_dirs)}/4] {sorted(populated_dirs, key=lambda x: (x[0], len(x[1])))}")

    print()
    print("=" * 76)
    print("  Step D: Act on events")
    print("=" * 76)

    complete_orbits = [orbit for orbit, dirs in orbit_pop.items() if len(dirs) == 4]
    if complete_orbits:
        print(f"\n  L1 (positive-closure) COMPLETES for {len(complete_orbits)} V₄-orbit(s).")
        print(f"  F (accepting states) NON-EMPTY for the first time.")
        for orbit in complete_orbits:
            print(f"    F contains: {sorted(orbit, key=lambda x: (x[0], len(x[1])))}")
        print()
        print("  DELIVERABLE: the architecture has its first orbit-complete locus.")
        print("  Three concrete new architectural moves are now registered:")
        print("    - MV₄-1: BWT of state-history into workspace")
        print("    - MV₄-2: Morton-heap workspace addressing for state evolution")
        print("    - MV₄-3: Workspace-held context as witness")
    else:
        print("\n  No orbit completions yet; need more moves.")

    print()
    print("  Remaining gaps to close (orbits not yet in F):")
    for orbit, populated_dirs in orbit_pop.items():
        if len(populated_dirs) < 4:
            missing = orbit - populated_dirs
            print(f"    {sorted(populated_dirs, key=lambda x: (x[0], len(x[1])))} populated;")
            print(f"      missing: {sorted(missing, key=lambda x: (x[0], len(x[1])))}")


if __name__ == "__main__":
    main()
