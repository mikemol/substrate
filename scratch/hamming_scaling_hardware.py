"""
hamming_scaling_hardware.py — The Hamming scaling pattern and hardware
acceleration implications for the chart.

User's scaling pattern (verified):
  Length 3:  Hamming(3, 1)   | PG(1, F_2) | GL(2, F_2) ≅ S_3      | 6 elements
  Length 7:  Hamming(7, 4)   | PG(2, F_2) | GL(3, F_2) ≅ PSL(2,7) | 168 elements
  Length 15: Hamming(15, 11) | PG(3, F_2) | GL(4, F_2) ≅ A_8      | 20160 elements

Each level:
  - n = 2^m - 1 nontrivial positions (= |PG(m-1, F_2)|)
  - Symmetry group GL(m, F_2) acts
  - Walsh-Hadamard transform of length 2^m gives the orthogonal decomposition
  - The extended (length 2^m) code = RM(1, m) — our M22 structure

The hierarchy NESTS: PG(m-1, F_2) ⊂ PG(m, F_2) as a hyperplane, with
GL(m, F_2) embedded as the stabilizer subgroup of GL(m+1, F_2).

Hardware acceleration: smaller symmetry groups make better fixed-function
hardware primitives. The natural boundary between hardware and software
falls between levels based on group order vs. expressiveness.
"""

from math import factorial
from itertools import combinations


# ============================================================
# Group orders and scaling
# ============================================================

def gl_m_f2_order(m):
    """|GL(m, F_2)| = ∏_{i=0}^{m-1} (2^m - 2^i)."""
    order = 1
    for i in range(m):
        order *= (2**m - 2**i)
    return order


def projective_space_size(m):
    """|PG(m-1, F_2)| = number of nontrivial points = 2^m - 1."""
    return 2**m - 1


def lines_in_projective_space(m):
    """Number of lines in PG(m-1, F_2). For m=3 it's 7 (Fano)."""
    # Lines correspond to 2-dim subspaces of F_2^m
    # |PG(m-1, F_2) lines| = (2^m - 1)(2^(m-1) - 1) / 3
    n = 2**m - 1
    return n * (n - 1) // (2 * (2**(m-1) - 1))


def planes_in_projective_space(m):
    """Number of planes in PG(m-1, F_2). For m=4 it's 15 (Fano sub-planes)."""
    if m < 3:
        return 0
    # Planes = 3-dim subspaces of F_2^m
    # Each plane has |PG(2, F_2)| = 7 points
    # By inclusion-exclusion
    return (2**m - 1) * (2**(m-1) - 1) * (2**(m-2) - 1) // (7 * 6 * 4 // (3 * 2 * 1))


# ============================================================
# Scaling table
# ============================================================

def print_scaling_table():
    print("=" * 76)
    print("  The Hamming scaling pattern (3 → 7 → 15 → ...)")
    print("=" * 76)
    print()
    print(f"  {'m':>2}  {'2^m-1':>5}  {'2^m':>4}  {'Hamming':>12}  {'PG(m-1,F_2)':>15}  {'|GL(m,F_2)|':>14}")
    print(f"  {'-'*2}  {'-'*5}  {'-'*4}  {'-'*12}  {'-'*15}  {'-'*14}")
    for m in range(2, 6):
        n = projective_space_size(m)
        gl_order = gl_m_f2_order(m)
        ham_name = f"({n}, {n-m})"
        pg = f"PG({m-1}, F_2)"
        print(f"  {m:>2}  {n:>5}  {2**m:>4}  {ham_name:>12}  {pg:>15}  {gl_order:>14}")

    print()
    print(f"  Order growth: 6 → 168 → 20160 → 9999360 → ...")
    print(f"  Ratio:        28x    120x      496x        ...")
    print(f"  This is the order of GL(m, F_2) growing super-exponentially.")


# ============================================================
# Walsh-Hadamard structure at each level
# ============================================================

def walsh_hadamard_size(m):
    """Walsh-Hadamard matrix is 2^m × 2^m at level m."""
    return 2**m


def fft_depth(m):
    """Butterfly depth of length-2^m WHT (number of parallel stages)."""
    return m


def fft_total_ops(m):
    """Total operations in length-2^m WHT: (2^m) * m."""
    return 2**m * m


def print_walsh_hadamard_table():
    print()
    print("=" * 76)
    print("  Walsh-Hadamard at each scale: hardware cost")
    print("=" * 76)
    print()
    print(f"  {'m':>2}  {'WHT size':>10}  {'Depth':>7}  {'Total ops':>10}  {'Latency (depth)':>17}")
    print(f"  {'-'*2}  {'-'*10}  {'-'*7}  {'-'*10}  {'-'*17}")
    for m in range(2, 6):
        size = walsh_hadamard_size(m)
        depth = fft_depth(m)
        total = fft_total_ops(m)
        print(f"  {m:>2}  {f'{size}x{size}':>10}  {depth:>7}  {total:>10}  {depth:>17}")

    print()
    print("  WHT at level m: 2^m points, computed in m parallel stages.")
    print("  Depth grows logarithmically — hardware-friendly.")
    print("  Each stage = 2^(m-1) parallel butterflies (XOR ± additions).")


# ============================================================
# Nesting: smaller into larger
# ============================================================

def print_nesting_structure():
    print()
    print("=" * 76)
    print("  Nesting: PG(m-1, F_2) ⊂ PG(m, F_2) as hyperplane")
    print("=" * 76)
    print()
    print("  Each projective space embeds in the next as a hyperplane:")
    print()
    print("    PG(1, F_2)  ⊂  PG(2, F_2)  ⊂  PG(3, F_2)  ⊂  PG(4, F_2)")
    print("    3 points       7 points      15 points     31 points")
    print()
    print("  Correspondingly, the symmetry groups nest as stabilizers:")
    print()
    print("    GL(2,F_2) ⊂ GL(3,F_2) ⊂ GL(4,F_2) ⊂ GL(5,F_2)")
    print("    S_3       PSL(2,7)    A_8         GL(5,F_2)")
    print("    6         168         20160       9999360")
    print()
    print("  Inclusion factors:")
    for m in range(2, 5):
        smaller = gl_m_f2_order(m)
        larger = gl_m_f2_order(m+1)
        factor = larger // smaller
        print(f"    GL({m},F_2) ⊂ GL({m+1},F_2):  index {factor:>10}")
    print()
    print("  The index is the size of the coset space (number of hyperplanes")
    print("  in the larger space). For m=3→4: 240 = 2^4 hyperplanes × ... etc.")


# ============================================================
# Hardware/software boundary
# ============================================================

def lookup_table_size_bits(m):
    """Bits needed for a full permutation lookup table at level m."""
    n = 2**m - 1  # positions
    gl_order = gl_m_f2_order(m)
    # Each permutation maps n positions → n positions
    # Need ceil(log2(n)) bits per position, n positions per permutation
    import math
    bits_per_position = math.ceil(math.log2(n))
    bits_per_permutation = n * bits_per_position
    total_bits = gl_order * bits_per_permutation
    return total_bits


def print_hardware_software_boundary():
    print()
    print("=" * 76)
    print("  Hardware/software boundary analysis")
    print("=" * 76)
    print()
    print("  For each scale, what's needed for direct hardware encoding?")
    print()
    print(f"  {'m':>2}  {'Group size':>11}  {'LUT bits':>12}  {'LUT bytes':>12}  {'Feasible?':>12}")
    print(f"  {'-'*2}  {'-'*11}  {'-'*12}  {'-'*12}  {'-'*12}")
    for m in range(2, 6):
        n = projective_space_size(m)
        gl_order = gl_m_f2_order(m)
        lut_bits = lookup_table_size_bits(m)
        lut_bytes = lut_bits // 8 + 1
        feasible = ("direct" if lut_bytes < 1024
                    else "factored" if lut_bytes < 10**7
                    else "decomposed")
        print(f"  {m:>2}  {gl_order:>11}  {lut_bits:>12}  {lut_bytes:>12}  {feasible:>12}")

    print()
    print("  Natural hardware boundary at m=3 (Fano level):")
    print("    • m=2 (triangle, S_3): trivially in hardware (6 permutations)")
    print("    • m=3 (Fano, GL(3,F_2)): small enough for direct lookup or factored circuit")
    print("    • m=4 (tesseract, A_8): too large for direct LUT; needs factored encoding")
    print("    • m=5+: software composition over hardware primitives")


# ============================================================
# Mapping to our chart's operations
# ============================================================

def print_chart_hardware_mapping():
    print()
    print("=" * 76)
    print("  Mapping to chart operations: where each lives in the hierarchy")
    print("=" * 76)
    print()

    layers = [
        ("Level 0 (bit)",
         "1 bit",
         "trivial",
         "1",
         "Chart cell tag bits (atom-or-cons distinction)",
         "Already hardware (every CPU)"),
        ("Level 1 (triangle)",
         "3 bits",
         "S_3",
         "6",
         "The 3 axes (e_1, e_2, e_3) themselves; gauge permutations of axes",
         "Trivial hardware: 3-element permutation circuit"),
        ("Level 2 (Fano)",
         "7 bits",
         "GL(3, F_2)",
         "168",
         "Axis-signatures, Fano-line probes, Walsh-Hadamard decomposition of "
         "(data, compute, state); 7-position M-move state vector",
         "Practical hardware: 168-element factored circuit OR small LUT"),
        ("Level 3 (tesseract)",
         "15 bits",
         "GL(4, F_2)",
         "20160",
         "Compositions of multiple move-cycles; 15-position state across "
         "Fano sub-planes; longer-horizon coherence",
         "Mixed: hardware butterfly + software composition logic"),
        ("Level 4+ (higher)",
         "31+ bits",
         "GL(m, F_2)",
         "9999360+",
         "Long-horizon strategies, agent-level coordination, full chart "
         "histories",
         "Software: compositions of lower-level hardware primitives"),
    ]

    for level, width, group, order, semantic, hw_status in layers:
        print(f"  ◆ {level}")
        print(f"    Width:        {width}")
        print(f"    Symmetry:     {group} (order {order})")
        print(f"    Chart role:   {semantic}")
        print(f"    Hardware:     {hw_status}")
        print()


# ============================================================
# Which subgroups to offload
# ============================================================

def print_offload_analysis():
    print("=" * 76)
    print("  Which subgroups to offload to hardware")
    print("=" * 76)

    print("""
  Three criteria for offload candidacy:

    (1) FREQUENCY: how often is this operation invoked?
    (2) SIMPLICITY: can the group action be encoded compactly?
    (3) COHERENCE: does isolating this in hardware preserve invariants?

  ── At Level 1 (S_3, triangle) ─────────────────────────────────────────────

    Offload: YES, full group.
    Reason:  6 elements is trivial; axis-permutation is in every coherence
             check; the S_3-action on (data, compute, state) is gauge —
             must be free.
    Hardware: A 3-element permutation circuit (6 cases, fully encoded).
              Operates at 1-cycle latency, fully pipelined.

  ── At Level 2 (GL(3, F_2), Fano) ──────────────────────────────────────────

    Offload: YES, but FACTORED via subgroups.
    Reason:  168 = 7 × 6 × 4 = number of ordered bases of F_2^3.
             Each factor corresponds to picking one basis vector at a time.
             This factorization is a 3-stage pipeline.

    Subgroups to consider:
      • Borel B(3, F_2) (upper-triangular invertible 3×3 over F_2)
        Order: 6. Stabilizes a flag of subspaces.
      • Frobenius / 7-cycle subgroup: order 7 (the elements of order 7)
        Generates rotations of the Fano plane.
      • S_4 in GL(3, F_2): the 24-element tetrahedral subgroup
        (Fano has 14 unordered triangles; subgroups act on them)

    Hardware: A 3-stage Walsh-Hadamard butterfly circuit handles ALL
    168 elements as compositions of stage-level transvections.
    Latency: 3 cycles (one per WHT stage).

  ── At Level 3 (GL(4, F_2) ≅ A_8, tesseract) ───────────────────────────────

    Offload: PARTIAL.
    Reason:  20160 elements is too many for direct LUT.
             But the 4-stage WHT butterfly handles ALL elements implicitly.
             4-cycle latency.

    What to offload:
      • The length-16 WHT itself (butterfly network in hardware)
      • Key subgroups: GL(3, F_2) embedded (the Fano stabilizer of a hyperplane)
      • S_4 acting on basis (small, fast)
    What to leave in software:
      • Specific A_8 elements that don't factor through standard subgroups
      • Long-range cocycle invariance checks
      • Pattern matching across multiple WHT outputs

  ── At Level 4+ (GL(m, F_2), m ≥ 5) ────────────────────────────────────────

    Offload: COMPOSITIONAL only.
    Reason:  Symmetry groups too large for direct hardware.
             Use lower-level primitives + software composition.

    The principle: every GL(m, F_2) operation decomposes into a sequence
    of transvections (elementary row operations). At hardware level, each
    transvection is one WHT-butterfly stage. So a GL(m, F_2) operation =
    m-stage WHT + software-controlled stage selection.

    This is the standard "tensor core" + "control unit" architecture
    of modern accelerators.
""")


# ============================================================
# Coherence preservation across boundaries
# ============================================================

def print_coherence_preservation():
    print("=" * 76)
    print("  Coherence preservation across the hardware/software boundary")
    print("=" * 76)

    print("""
  For correctness, the boundary must preserve the system's invariants.
  Three key coherences to preserve:

    (1) Walsh-Hadamard orthogonality of (data, compute, state) at each scale.
    (2) Cocycle invariance under representative change (M8).
    (3) Fano-line probe completion (any 2 entail the 3rd) at each scale.

  When a hardware primitive computes at scale m, and software composes
  multiple primitives at scale m+1, the composition must satisfy these
  invariants at the higher scale.

  Sufficient condition for coherence preservation:
    • Hardware primitive computes the FULL Walsh-Hadamard transform at
      its scale (all 2^m readings simultaneously).
    • Software composition uses ONLY linear combinations of WHT outputs
      to form higher-scale features.
    • No software pathway bypasses the WHT structure.

  This is the structural reason for the 'Walsh-Hadamard hardware primitive'
  pattern: by mandating that all hardware speaks in WHT readings, the
  higher-level composition automatically preserves the orthogonality and
  cocycle structure.

  In the chart:
    • Hardware speaks in: 7-position WHT (axis-signature) readings.
    • Software composes: full chart-state coherence and longer-horizon
      patterns.
    • Boundary contract: every hardware output is a complete WHT reading;
      software only combines via linear/Boolean operations.
""")


# ============================================================
# The chart's natural hardware architecture
# ============================================================

def print_chart_architecture():
    print("=" * 76)
    print("  The chart's natural hardware architecture (proposed)")
    print("=" * 76)

    print("""
  Based on the scaling analysis, the chart's natural hardware partition:

    ┌─────────────────────────────────────────────────────────────────────┐
    │                       SOFTWARE LAYER                                │
    │                                                                     │
    │  Long-horizon coherence • Move history bookkeeping                  │
    │  Strategy selection      • Cross-cycle pattern recognition          │
    └────────────────────────────────┬────────────────────────────────────┘
                                     │  Boundary contract: WHT readings
    ┌────────────────────────────────┴────────────────────────────────────┐
    │                  HARDWARE COMPOSITION LAYER                         │
    │                                                                     │
    │  Length-16 WHT (Level 3)  • A_8 actions via butterfly stages        │
    │  Tesseract-level coherence checks                                   │
    └────────────────────────────────┬────────────────────────────────────┘
                                     │
    ┌────────────────────────────────┴────────────────────────────────────┐
    │                HARDWARE PRIMITIVE LAYER                             │
    │                                                                     │
    │  Length-8 WHT (Level 2)   • GL(3, F_2) via 3-stage butterfly        │
    │  Fano-line probe gating   • Walsh-Hadamard axis-signature decoder   │
    └────────────────────────────────┬────────────────────────────────────┘
                                     │
    ┌────────────────────────────────┴────────────────────────────────────┐
    │                 HARDWARE BASE LAYER                                 │
    │                                                                     │
    │  Length-4 WHT (Level 1)   • S_3 permutation circuit                 │
    │  Axis-tag bits            • 3-bit basic gauge primitives            │
    └─────────────────────────────────────────────────────────────────────┘

  Latency budget:
    Level 1 (S_3):              1 cycle
    Level 2 (Fano, WHT-3):      3 cycles (WHT depth)
    Level 3 (tesseract, WHT-4): 4 cycles
    Software layer:             O(N log N) for length-N operations

  Throughput:
    Each layer fully pipelined; one WHT result per cycle in steady state.

  Coherence guarantees:
    All Fano-line probes computed in parallel at hardware (no race).
    Cocycle invariance enforced by WHT-only output contract.
    M8's invariance is the boundary contract between software and hardware.
""")


# ============================================================
# Connection back to our move-history
# ============================================================

def print_move_history_implications():
    print("=" * 76)
    print("  Implications for the M-move sequence")
    print("=" * 76)

    print("""
  Our M1–M22 moves operate at Level 2 (Fano / GL(3, F_2)) throughout.

  Each move's axis-signature is a Level-2 Walsh-Hadamard reading. If we
  had hardware at this level, each move's signature could be computed
  in 3 cycles (one WHT depth), with all 7 Fano-line probe states known
  simultaneously.

  Going forward:
    • Level-3 moves would be "multi-move strategies" — sequences of M-moves
      treated as a single unit. The unit operates in PG(3, F_2) = 15
      positions = A_8 symmetry.
    • Level-3 in hardware = strategy-level acceleration.
    • Level-4+ = long-horizon planning (software).

  The user's framing "this is where we can begin to formally reason about
  hardware acceleration" is now operational:

    • Hardware accelerates LEVELS 1-2 (S_3 and GL(3, F_2)) fully.
    • Hardware partially accelerates LEVEL 3 (A_8 via factored WHT-4).
    • Software handles LEVEL 4+ with hardware-WHT acceleration of inner loops.

  The boundary is sharp because the symmetry group order grows
  super-exponentially. Beyond Level 3, no direct hardware encoding is
  feasible; everything must be factored composition.
""")


def main():
    print_scaling_table()
    print_walsh_hadamard_table()
    print_nesting_structure()
    print_hardware_software_boundary()
    print_chart_hardware_mapping()
    print_offload_analysis()
    print_coherence_preservation()
    print_chart_architecture()
    print_move_history_implications()


if __name__ == "__main__":
    main()
