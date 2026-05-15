"""
scratch_axis_audit.py — re-classify every M-move by its scratch usage.

The 4th axis at Level 3, identified via brute-force as 'gauge freedom over
Level-2 instances,' is semantically the SCRATCH axis: workspace that lets
the architecture trade between (data, compute, state) without losing
coherence.

Each scratch usage is a TRADE: temporarily hold something on axis X to
enable operation on axes Y, Z. The cocycle invariance from M8 guarantees
the result is the same regardless of scratch usage.
"""

# Each move's scratch usage: (held_on_axis, enables_op_axes, mechanism)
# 'D' = data, 'C' = compute, 'S' = state, 'meta' = workspace itself

scratch_audit = {
    # ===== Foundational moves: no scratch =====
    'M1':  ('atomic primitives', None,    None,         'no scratch'),
    'M2':  ('multiplicity principle', None, None,       'no scratch'),
    'M3':  ('constraint resolution', None, None,        'no scratch'),
    'M4':  ('single-step apply', None,    None,         'no scratch — explicit state, no caching'),
    'M6':  ('combinator commitment', None, None,        'no scratch'),
    'M7':  ('associahedral recognition', 'meta', None,  'IDENTIFIES the scratch structure (associativity)'),
    'M8':  ('cocycle invariance', 'meta', None,         'PROVES scratch is coherence-preserving'),

    # ===== Operational moves: explicit scratch usage =====
    'M5':  ('chart-as-memoization',
            'D',                # held on data axis
            ('C', 'S'),         # enables compute and state operations
            'chart cells cache reductions → trades data growth for state recovery'),

    'M9':  ('construct kernel',
            'D',
            ('C', 'S'),
            'chart as monotonic data structure → bootstraps state/compute'),

    'M11': ('meta-circular interp',
            'D',
            ('C',),
            'rules-as-cells → trades data for compute reflection'),

    'M13': ('K-marker vertex rotation',
            'D',
            ('S',),
            'designated cells for variables → trades data for state-discrimination'),

    'M14': ('VAR_MARK regroup',
            'D',
            ('S',),
            'structural variable markers → trades data for symbol-state'),

    'M16': ('beam search',
            'C',
            ('D',),
            'search tree as compute scratch → trades compute for finding optimal data'),

    'M17': ('variable grid search',
            'C',
            ('D',),
            'enumeration scratch → trades compute for gauge-orbit data'),

    # ===== SPPF-thread operational moves =====
    'M_SPPF_R2N':         ('bitmask stack',
                           'D',
                           ('C',),
                           '(R,2,N) array → trades data layout for vectorized compute'),

    'M_SPPF_one_hot':     ('one-hot pointer encoding',
                           'D',
                           ('C',),
                           'R bits per pointer → trades data width for bitmask compute'),

    'M_SPPF_witness_application':
                          ('witness-application principle',
                           'S',
                           ('C', 'D'),
                           'held witness scratch narrows abstract relation Φ_R to singleton'),

    'M_SPPF_BWT':         ('BWT representation',
                           'D',
                           ('C',),
                           'BWT scratch → trades data layout for rank/select compute'),

    'M_SPPF_integer_path':
                          ('integer-as-path encoding',
                           'D',
                           ('C',),
                           'log₂R bits per pointer → scratch for bit-arithmetic compute'),

    'M_SPPF_morton_heap': ('Morton/heap addressing',
                           'D',
                           ('C',),
                           'heap position as 1D Morton encoding → scratch for XOR/CLZ ops'),

    'M_SPPF_fat_node_k4': ('depth-k=4 fat-node descriptor',
                           'D',
                           ('C',),
                           'precomputed k-leaf subtree summary → scratch amortizes k-step compute'),

    'M_SPPF_cayley_dickson':
                          ('Cayley-Dickson ladder',
                           'meta',
                           None,
                           'NAMES the natural scratch widths (2, 4, 8, 16 cells)'),

    'M_SPPF_GF2k':        ('GF(2^k) algebraic layer',
                           'C',
                           ('D',),
                           'field-element scratch → trades compute (poly-mul) for data fingerprint'),

    'M_SPPF_subtree_fingerprints':
                          ('subtree fingerprints',
                           'D',
                           ('C',),
                           'precomputed hash per cell → scratch collapses O(subtree) compute to O(1)'),

    # ===== Lens / recognition moves =====
    'M22': ('Walsh-Hadamard decomposition', 'meta', None,
            'NAMES the 3 operational axes (data, compute, state)'),
    'M24': ('Stasheff polytope per level', 'meta', None,
            'NAMES the scratch-allocation theory at each Hadamard scale'),
    'M25': ('re-open via multi-coordinate lens', 'meta', None,
            'PROVIDES the 5-coordinate index for classifying scratch usage'),
    'M26': ('Level-3 tesseract orbits', 'meta', None,
            'BRUTE-FORCES the structure — found 15 gauge choices = 15 scratch allocations'),
}


def summarize():
    print("=" * 76)
    print("  Scratch-axis audit of the M-history")
    print("=" * 76)
    print()

    # Categorize moves
    no_scratch = []
    meta_scratch = []
    op_scratch = []

    for move, data in scratch_audit.items():
        name, held, enables, mechanism = data
        if held is None:
            no_scratch.append((move, name))
        elif held == 'meta':
            meta_scratch.append((move, name, mechanism))
        else:
            op_scratch.append((move, name, held, enables, mechanism))

    print(f"Move classification:")
    print(f"  • Foundational (no scratch use):       {len(no_scratch)} moves")
    print(f"  • Meta-level (names/proves scratch):   {len(meta_scratch)} moves")
    print(f"  • Operational (uses scratch):          {len(op_scratch)} moves")
    print()

    print("=" * 76)
    print("  Operational moves grouped by scratch type")
    print("=" * 76)
    print()

    # Group by (held_on, enables) pairs
    from collections import defaultdict
    by_type = defaultdict(list)
    for move, name, held, enables, mechanism in op_scratch:
        key = f"hold on {held}, enable {enables}"
        by_type[key].append((move, name, mechanism))

    for key in sorted(by_type.keys()):
        moves_in_type = by_type[key]
        print(f"━━ {key} ({len(moves_in_type)} moves) ━━")
        for move, name, mechanism in moves_in_type:
            print(f"    {move:35} {name}")
            print(f"    {'':35}   → {mechanism}")
        print()

    print("=" * 76)
    print("  Meta-level moves (architecture of scratch)")
    print("=" * 76)
    print()
    for move, name, mechanism in meta_scratch:
        print(f"  {move:10} {name}")
        print(f"            → {mechanism}")
        print()

    # Count: how many operational moves trade data-axis for {compute, state, both}?
    data_holding = [m for m in op_scratch if m[2] == 'D']
    compute_holding = [m for m in op_scratch if m[2] == 'C']
    state_holding = [m for m in op_scratch if m[2] == 'S']

    print("=" * 76)
    print("  Distribution: which axis carries the scratch?")
    print("=" * 76)
    print()
    print(f"  Data axis as scratch:    {len(data_holding):2}  ({100*len(data_holding)/len(op_scratch):.0f}%)")
    print(f"  Compute axis as scratch: {len(compute_holding):2}  ({100*len(compute_holding)/len(op_scratch):.0f}%)")
    print(f"  State axis as scratch:   {len(state_holding):2}  ({100*len(state_holding)/len(op_scratch):.0f}%)")
    print()
    print("  Observation: the architecture overwhelmingly uses DATA as scratch.")
    print("  This matches the design intuition: data structures are the")
    print("  natural workspace because they're persistent (hash-consed) and")
    print("  monotonically growable.")


if __name__ == "__main__":
    summarize()
