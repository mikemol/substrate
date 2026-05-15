"""
directed_witnessed_pairs.py — the 24-operation directed framework.

A directed witnessed operation is a triple (source, sink, witness) where:
  - source, sink ∈ {D, C, S, W}, distinct (the data-flow direction X→Y)
  - witness ∈ {D, C, S, W} \\ {source, sink} from the OPPOSITE PAIR
    under the V_4 pairing that puts {source, sink} together

Count:
  4 (source) × 3 (sink) × 2 (witness from opposite pair) = 24

This equals |S_4|. S_4 acts transitively on the 24 ops (one orbit).
A_4 (even permutations) gives 2 orbits of 12 (chirality classes).
V_4 (Klein 4-group) gives 6 orbits of 4: each pairing × each chirality.

This is the tetrahedral flag manifold:
  - 4 vertices (axes)
  - 12 directed edges (4×3)
  - 24 (directed-edge, opposite-vertex) pairs = oriented flags
  - 2 chirality classes (mirror images of the tetrahedron)
  - 6 V_4-orbits = 3 pairings × 2 orientations
"""

from itertools import permutations
from collections import defaultdict

AXES = ['D', 'C', 'S', 'W']

PAIRINGS = {
    'α': ({'D', 'C'}, {'S', 'W'}),
    'β': ({'D', 'S'}, {'C', 'W'}),
    'γ': ({'D', 'W'}, {'C', 'S'}),
}

V4_SWAPS = {
    'e': {a: a for a in AXES},
    'α': {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},
    'β': {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},
    'γ': {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},
}


def opposite_pair_for(source, sink):
    """Given two axes, find the V_4-opposite pair (which contains the witnesses)."""
    s_set = frozenset({source, sink})
    for pairing, (p1, p2) in PAIRINGS.items():
        if frozenset(p1) == s_set:
            return frozenset(p2), pairing
        if frozenset(p2) == s_set:
            return frozenset(p1), pairing
    raise ValueError(f"No pairing contains {s_set}")


def enumerate_directed_witnessed_ops():
    """Generate all 24 directed witnessed operations."""
    ops = []
    for source in AXES:
        for sink in AXES:
            if source == sink:
                continue
            opp_pair, pairing = opposite_pair_for(source, sink)
            for witness in sorted(opp_pair):
                ops.append({
                    'source': source,
                    'sink': sink,
                    'witness': witness,
                    'pair': frozenset({source, sink}),
                    'pairing': pairing,
                    'opposite_pair': opp_pair,
                    'name': f"{source}→{sink} w/ {witness}",
                })
    return ops


def apply_v4_swap(op, swap_name):
    """Apply a V_4 swap to a directed witnessed operation."""
    swap = V4_SWAPS[swap_name]
    return (swap[op['source']], swap[op['sink']], swap[op['witness']])


def v4_orbit_of(op):
    """Return the V_4-orbit of a directed witnessed op as a set of triples."""
    return frozenset(apply_v4_swap(op, swap) for swap in V4_SWAPS)


# ============================================================
# Chirality (A_4 vs S_4 \ A_4)
# ============================================================

def chirality(source, sink, witness):
    """Compute the chirality of a directed witnessed op.

    The 4th axis is determined: the one not in {source, sink, witness}.
    The triple (source, sink, witness, fourth) is a permutation of (D,C,S,W).
    Parity of that permutation determines chirality.
    """
    fourth = (set(AXES) - {source, sink, witness}).pop()
    perm = [source, sink, witness, fourth]
    # Count inversions relative to canonical order (D, C, S, W)
    pos = {'D': 0, 'C': 1, 'S': 2, 'W': 3}
    inversions = 0
    for i in range(4):
        for j in range(i + 1, 4):
            if pos[perm[i]] > pos[perm[j]]:
                inversions += 1
    return 'even' if inversions % 2 == 0 else 'odd'


# ============================================================
# Generate the structure
# ============================================================

def main():
    print("=" * 78)
    print("  DIRECTED WITNESSED-PAIR FRAMEWORK — 24 operations")
    print("=" * 78)
    print()
    print("  Count: 4 (source) × 3 (sink) × 2 (witness from opposite pair) = 24 = |S_4|")
    print()
    print("  Group action structure:")
    print("    S_4 (24 elements):  acts transitively — 1 orbit of size 24")
    print("    A_4 (12 elements):  2 orbits of 12 — the 2 CHIRALITY CLASSES")
    print("    V_4 (4 elements):   6 orbits of 4  — 3 pairings × 2 orientations")
    print()

    ops = enumerate_directed_witnessed_ops()

    # ============================================================
    # Compute orbits
    # ============================================================
    orbits = []
    seen = set()
    for op in ops:
        key = (op['source'], op['sink'], op['witness'])
        if key in seen:
            continue
        orbit = v4_orbit_of(op)
        seen.update(orbit)
        orbits.append({
            'pairing': op['pairing'],
            'chirality': chirality(op['source'], op['sink'], op['witness']),
            'members': sorted(orbit),
        })

    # ============================================================
    # Print orbits organized by pairing × chirality
    # ============================================================
    print("=" * 78)
    print("  The 6 V_4-orbits (3 pairings × 2 chiralities)")
    print("=" * 78)

    by_pairing_chirality = defaultdict(list)
    for o in orbits:
        by_pairing_chirality[(o['pairing'], o['chirality'])].append(o)

    for pairing_name in ['α', 'β', 'γ']:
        p1, p2 = PAIRINGS[pairing_name]
        p1_str = ''.join(sorted(p1))
        p2_str = ''.join(sorted(p2))
        print(f"\n  Pairing {pairing_name}: {{{p1_str}, {p2_str}}}")
        for chir in ['even', 'odd']:
            orbits_here = by_pairing_chirality[(pairing_name, chir)]
            for o in orbits_here:
                print(f"    ── V_4-orbit ({chir} chirality) ──")
                for source, sink, witness in o['members']:
                    print(f"        {source}→{sink} w/ {witness}")

    # ============================================================
    # Print the full 24 as a flat table
    # ============================================================
    print()
    print("=" * 78)
    print("  Full table of the 24 directed witnessed operations")
    print("=" * 78)
    print(f"\n  {'op':<14} {'pair':<5} {'pairing':<10} {'chirality':<10} {'(held,enabled)':<20}")
    print(f"  {'-'*14} {'-'*5} {'-'*10} {'-'*10} {'-'*20}")
    for op in sorted(ops, key=lambda o: (o['pairing'], chirality(o['source'], o['sink'], o['witness']),
                                          o['source'], o['sink'], o['witness'])):
        s, t, w = op['source'], op['sink'], op['witness']
        pair_str = ''.join(sorted(op['pair']))
        chir = chirality(s, t, w)
        held_enabled = f"({w}, {{{','.join(sorted(op['pair']))}}})"
        print(f"  {s}→{t} w/ {w:<6} {pair_str:<5} {op['pairing']:<10} {chir:<10} {held_enabled:<20}")

    # ============================================================
    # Semantic interpretations of one representative per orbit
    # ============================================================
    print()
    print("=" * 78)
    print("  Semantic interpretation — one representative per V_4-orbit")
    print("=" * 78)

    SEMANTICS = {
        # Pairing α (DC + SW)
        ('α', 'even'):  ('D→C w/ S', 'apply / reduce — data → compute, witnessed by state advance'),
        ('α', 'odd'):   ('D→C w/ W', 'memoized apply — data → compute, witnessed by workspace cache'),
        # Pairing β (DS + CW)
        ('β', 'even'):  ('D→S w/ C', 'compute-validated state change — data evolves with computed proof'),
        ('β', 'odd'):   ('D→S w/ W', 'workspace-receipted state change — data evolves, workspace logs'),
        # Pairing γ (DW + CS)
        ('γ', 'even'):  ('D→W w/ C', 'compute-validated store — data goes to workspace iff compute confirms'),
        ('γ', 'odd'):   ('D→W w/ S', 'logged store — data → workspace, state-log witnesses'),
    }

    print()
    print("  The 6 V_4-orbits — each orbit's 4 members all play the same role")
    print("  on different axis configurations. The representative is one member;")
    print("  the others are V_4-rotations of it.\n")
    for pairing in ['α', 'β', 'γ']:
        for chir in ['even', 'odd']:
            rep, desc = SEMANTICS[(pairing, chir)]
            print(f"  Pairing {pairing}, {chir} chirality:")
            print(f"    representative: {rep}")
            print(f"    role: {desc}")
            # Show the other 3 members of the orbit
            orbits_here = by_pairing_chirality[(pairing, chir)]
            for o in orbits_here:
                others = [f"{s}→{t} w/ {w}" for s, t, w in o['members'] if f"{s}→{t} w/ {w}" != rep]
                print(f"    V_4-rotations: {', '.join(others)}")
            print()

    # ============================================================
    # Map existing chart operations
    # ============================================================
    print("=" * 78)
    print("  Mapping existing chart operations to the directed framework")
    print("=" * 78)

    EXISTING_OPS = {
        'S5_apply (D-term → D-term via C, S advances)': {
            'reading_as_three_axis': ('D', 'C', 'S'),
            'orbit': ('α', 'even'),
            'notes': 'data passed through compute reduction; state witnesses. Apply is the canonical D→C w/ S.',
        },
        'M_SPPF_witness_application (S held, narrows C+D)': {
            'reading_as_three_axis': ('D', 'C', 'S'),
            'orbit': ('α', 'even'),
            'notes': 'Same orbit as apply: D→C with S witnessing. The "held" role is the witness role.',
        },
        'M32 workspace_witness (W held, narrows C+D)': {
            'reading_as_three_axis': ('D', 'C', 'W'),
            'orbit': ('α', 'odd'),
            'notes': 'D→C with W witnessing. Same orbit as memoized apply.',
        },
        'M32 store (D→W, logs S)': {
            'reading_as_three_axis': ('D', 'W', 'S'),
            'orbit': ('γ', 'odd'),
            'notes': 'Concrete directional D→W with state witness. Logged store.',
        },
        'M32 load (W→D)': {
            'reading_as_three_axis': ('W', 'D', '?'),
            'orbit': ('γ', '?'),
            'notes': 'INVERSE of store: W→D direction. Currently has no witness logging.',
        },
        'M11 interp (D rules, advances C and S)': {
            'reading_as_three_axis': ('D', 'S', 'C'),
            'orbit': ('β', 'even'),
            'notes': 'Re-classified: data drives state, compute witnesses. The state-evolving interp.',
        },
    }

    print()
    for op_name, info in EXISTING_OPS.items():
        s, t, w = info['reading_as_three_axis']
        pairing, chir = info['orbit']
        print(f"  • {op_name}")
        if '?' not in (s, t, w):
            print(f"    directed reading: {s}→{t} w/ {w}")
            print(f"    orbit: pairing {pairing}, {chir} chirality")
        else:
            print(f"    directed reading: {s}→{t} w/ {w} (ambiguous)")
        print(f"    notes: {info['notes']}")
        print()

    # ============================================================
    # Coverage in directed framework
    # ============================================================
    print("=" * 78)
    print("  Coverage of the 24 directed operations by current chart")
    print("=" * 78)

    populated_orbits = set()
    for op_name, info in EXISTING_OPS.items():
        s, t, w = info['reading_as_three_axis']
        if '?' not in (s, t, w):
            populated_orbits.add(info['orbit'])

    print()
    print(f"  Distinct (pairing, chirality) orbits populated: {len(populated_orbits)} / 6")
    print(f"  Operations in those orbits (counting individual cells): varies")
    print()
    for pairing in ['α', 'β', 'γ']:
        for chir in ['even', 'odd']:
            marker = '✓' if (pairing, chir) in populated_orbits else '·'
            example_rep = SEMANTICS[(pairing, chir)][0]
            print(f"    [{marker}] pairing {pairing}, {chir} chirality  (rep: {example_rep})")

    # ============================================================
    # Implications for meta-protocol
    # ============================================================
    print()
    print("=" * 78)
    print("  Implications for the meta-protocol")
    print("=" * 78)
    print("""
  In the directed framework, each operation declares:
      source  : Axis             # what gets consumed/transformed
      sink    : Axis             # what gets produced/written
      witness : Axis             # what validates (from opposite pair)

  Constraints checkable at the meta-level:
      - source ≠ sink ≠ witness ≠ source
      - witness ∈ opposite_pair_via_pairing(source, sink)

  V_4 rotation acts mechanically:
      v4_rotate(op, swap) = Operation(swap(source), swap(sink), swap(witness))

  Two operations are V_4-twins iff their (source, sink, witness) triples
  are V_4-related. Six V_4-orbits = the 6 fundamental architectural patterns.

  Each operation has a natural INVERSE:
      inverse(Operation(s, t, w)) = Operation(t, s, w)

  An invertible operation pair (op, inverse(op)) lives in the SAME pair
  but with reversed direction. Both have the same witness options.

  In the engagement matrix, this means:
      - op's profile has (s: I, t: M/C/O, w: R)  (source consumed, sink produced, witness read)
      - inverse(op)'s profile has (s: M/C/O, t: I, w: R)  (roles of s and t swap)

  Note that op and inverse(op) live in DIFFERENT V_4-orbits in general,
  because swapping (s, t) keeps the pair but may flip chirality.
""")


if __name__ == "__main__":
    main()
