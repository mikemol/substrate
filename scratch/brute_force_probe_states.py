"""
brute_force_probe_states.py — enumerate the Fano-line probe states at each
Walsh-Hadamard level of the cotype.

M25 said "L_2 through L_7 stand at the new lens scale." This script makes
that mechanical: enumerate the 7 Fano lines × 5 WHT levels = 35 probe
states; classify each as complete, gap-named, standing, or empty.
"""

from itertools import combinations

# ============================================================
# Populated axis-signatures by WHT level
# Extracted from M25's re-classification table
# ============================================================

populated_by_level = {
    0: {
        '100': ['M1 founding (left/right/eq accessors)'],
    },
    1: {
        '100': ['M1 founding (cons)', 'M2 multiplicity', 'M4 single-step apply', 'M5 chart-as-memoization'],
        '010': ['M_SPPF_R2N', 'M_SPPF_one_hot', 'M_SPPF_integer_path', 'M_SPPF_morton_heap'],
        '011': ['(none directly at Level 1)'],
        '110': ['M9 construct kernel (part)'],
    },
    2: {
        '100': ['M12 lift tier-2', 'M13 vertex rotation', 'M18 Fano-RM', 'M19 SKI-as-RM',
                'M20 parity basins', 'M21 Hamming(7,4)', 'M22 Walsh-Hadamard',
                'M_SPPF_cayley_dickson', 'M_SPPF_GF2k'],
        '010': ['M10 verification regroup', 'M_SPPF_witness_application'],
        '110': ['M_SPPF_BWT', 'M_SPPF_fat_node_k4', 'M_SPPF_subtree_fingerprints'],
        '011': ['M14 VAR_MARK regroup'],
        '101': ['M15 closure audit'],
        '111': ['M11 meta-circular interp'],
    },
    3: {
        '110': ['M16 beam search', 'M17 variable grid', 'M23 Hamming scaling'],
    },
    4: {
        # speculative only — no concrete moves
    },
}

# ============================================================
# The 7 Fano lines (each is a triple of axis-signatures
# whose XOR is zero)
# ============================================================

FANO_LINES = [
    ('L1', frozenset({'100', '010', '110'}), 'positive-closure'),
    ('L2', frozenset({'100', '001', '101'}), 'GS-guard-coverage'),
    ('L3', frozenset({'010', '001', '011'}), 'SA-guard-coverage'),
    ('L4', frozenset({'100', '011', '111'}), 'GS-triadic-completion'),
    ('L5', frozenset({'010', '101', '111'}), 'SA-triadic-completion'),
    ('L6', frozenset({'001', '110', '111'}), 'guard-reconstitution'),
    ('L7', frozenset({'110', '101', '011'}), 'pure-composite-diagonal'),
]


def probe_state_at_level(level: int, line_sigs: frozenset) -> tuple:
    """Return (state, populated_on_line, missing_on_line)."""
    level_pop = set(populated_by_level.get(level, {}).keys())
    populated_on_line = line_sigs & level_pop
    missing = line_sigs - populated_on_line
    if len(populated_on_line) == 3:
        return ('complete', populated_on_line, missing)
    elif len(populated_on_line) == 2:
        return ('gap-named', populated_on_line, missing)
    elif len(populated_on_line) == 1:
        return ('standing', populated_on_line, missing)
    else:
        return ('empty', populated_on_line, missing)


# ============================================================
# Brute-force enumeration
# ============================================================

def print_per_level_probe_states():
    print("=" * 76)
    print("  Probe state at each Walsh-Hadamard level")
    print("=" * 76)
    print()

    for level in sorted(populated_by_level.keys()):
        populated = set(populated_by_level.get(level, {}).keys())
        print(f"Level {level}  populated axis-signatures: {sorted(populated)}")
        print(f"          number of populated: {len(populated)}/7")
        print()

        for name, line_sigs, line_name in FANO_LINES:
            state, populated_on_line, missing = probe_state_at_level(level, line_sigs)
            tag = {'complete': '✓', 'gap-named': '!', 'standing': '·', 'empty': ' '}[state]
            print(f"   [{tag}] {name} ({line_name})")
            if state == 'complete':
                print(f"         complete: {sorted(populated_on_line)}")
            elif state == 'gap-named':
                print(f"         populated: {sorted(populated_on_line)}")
                print(f"         missing:   {sorted(missing)}  <-- candidate next-work")
            elif state == 'standing':
                print(f"         single point populated: {sorted(populated_on_line)}")
                print(f"         needs: {sorted(missing)} (two more points)")
            elif state == 'empty':
                print(f"         empty at this level")
        print()
        print('-' * 76)
        print()


def print_summary():
    print("=" * 76)
    print("  Summary: complete / gap-named / standing / empty counts")
    print("=" * 76)
    print()
    print(f"  {'Level':>6}  {'complete':>10}  {'gap-named':>11}  {'standing':>10}  {'empty':>7}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*11}  {'-'*10}  {'-'*7}")

    for level in sorted(populated_by_level.keys()):
        counts = {'complete': 0, 'gap-named': 0, 'standing': 0, 'empty': 0}
        for name, line_sigs, line_name in FANO_LINES:
            state, _, _ = probe_state_at_level(level, line_sigs)
            counts[state] += 1
        print(f"  {level:>6}  {counts['complete']:>10}  {counts['gap-named']:>11}  "
              f"{counts['standing']:>10}  {counts['empty']:>7}")


def print_gap_named_targets():
    """The candidate next-work items: gap-named probes by level."""
    print()
    print("=" * 76)
    print("  Gap-named candidate next-work")
    print("=" * 76)
    print()

    for level in sorted(populated_by_level.keys()):
        gaps_at_level = []
        for name, line_sigs, line_name in FANO_LINES:
            state, populated_on_line, missing = probe_state_at_level(level, line_sigs)
            if state == 'gap-named':
                gaps_at_level.append((name, line_name, populated_on_line, missing))

        if gaps_at_level:
            print(f"  Level {level}:")
            for name, line_name, populated, missing in gaps_at_level:
                missing_sig = list(missing)[0]
                print(f"    {name} ({line_name}): needs axis-sig {missing_sig}")
                print(f"           given: {sorted(populated)}")


def print_signature_population_matrix():
    """Show which axis-signatures appear at which levels."""
    print()
    print("=" * 76)
    print("  Axis-signature × WHT-level population matrix")
    print("=" * 76)
    print()
    sigs = ['100', '010', '001', '110', '101', '011', '111']
    print(f"  {'sig':>5}", end="")
    for level in sorted(populated_by_level.keys()):
        print(f"  L{level:>2}", end="")
    print()
    print(f"  {'-'*5}", end="")
    for level in sorted(populated_by_level.keys()):
        print(f"  {'-'*3}", end="")
    print()

    for sig in sigs:
        print(f"  {sig:>5}", end="")
        for level in sorted(populated_by_level.keys()):
            count = len(populated_by_level.get(level, {}).get(sig, []))
            marker = '·' if count == 0 else ('!' if count == 1 else '+' if count <= 3 else '#')
            print(f"  {marker:>3}", end="")
        print()

    print()
    print("  Legend: · = empty, ! = 1 move, + = 2-3 moves, # = 4+ moves")
    print()


if __name__ == "__main__":
    print_signature_population_matrix()
    print_summary()
    print_gap_named_targets()
    print()
    print_per_level_probe_states()
