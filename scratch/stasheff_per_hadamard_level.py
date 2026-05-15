"""
stasheff_per_hadamard_level.py — At each Hadamard level, a different
Stasheff polytope encodes the composition choices for that level.

The Walsh-Hadamard at level m has m butterfly stages. The ways to
*compose* these m stages = bracketings of m items = vertices of the
Stasheff polytope K_m. The dimension of K_m is m-2.

Going from Hadamard level m to m+1 adds ONE DIMENSION to the Stasheff
polytope. That new dimension is a new axis of design choice — a new
tradeoff you can make in how computation is organized.

The user's hint:
    "You can pivot an axis off to a different consideration with each
     step up. This is how you compose things like parallel vs series
     computation, how you trade between compute time at different orders
     of composition, how you handle synchronization between parallel
     asymmetric compute or representation."

Each axis of the Stasheff polytope IS one of these considerations:
    Axis 1 (first available at K_3): parallel vs serial
    Axis 2 (added at K_4):           depth/breadth balance
    Axis 3 (added at K_5):           chunking pattern
    Axis 4 (added at K_6):           synchronization granularity
    ...
"""

from itertools import product, combinations


# ============================================================
# Catalan numbers and Stasheff polytope dimension
# ============================================================

def catalan(n):
    """Catalan number C_n. The number of bracketings of n+1 elements."""
    if n == 0:
        return 1
    result = 1
    for i in range(n):
        result = result * 2 * (2 * i + 1) // (i + 2)
    return result


def stasheff_dim(m):
    """Stasheff polytope K_m has dimension m-2 and C_{m-1} vertices."""
    return m - 2


def stasheff_vertices(m):
    """Number of vertices in K_m = C_{m-1}."""
    return catalan(m - 1)


# ============================================================
# Generating bracketings (vertices of K_m)
# ============================================================

def bracketings(items):
    """Generate all binary bracketings of a sequence of items.

    Each bracketing is a binary tree expressed as nested tuples.
    For items = [a, b, c], yields: (a, (b, c)), ((a, b), c).
    """
    if len(items) == 1:
        yield items[0]
        return
    for i in range(1, len(items)):
        left_items = items[:i]
        right_items = items[i:]
        for left in bracketings(left_items):
            for right in bracketings(right_items):
                yield (left, right)


def bracketing_str(b):
    """Pretty-print a bracketing."""
    if isinstance(b, tuple):
        return f"({bracketing_str(b[0])} {bracketing_str(b[1])})"
    return str(b)


def bracketing_depth(b):
    """Max depth of the bracketing tree (depth of nesting)."""
    if isinstance(b, tuple):
        return 1 + max(bracketing_depth(b[0]), bracketing_depth(b[1]))
    return 0


def bracketing_balance(b):
    """Balance ratio: |right - left| / (right + left) across all internal nodes."""
    if not isinstance(b, tuple):
        return 0.0, 0
    total_imbalance = 0.0
    total_nodes = 0

    def count(t):
        if not isinstance(t, tuple):
            return 1
        return count(t[0]) + count(t[1])

    def walk(t):
        nonlocal total_imbalance, total_nodes
        if isinstance(t, tuple):
            lcount = count(t[0])
            rcount = count(t[1])
            imbalance = abs(lcount - rcount) / (lcount + rcount)
            total_imbalance += imbalance
            total_nodes += 1
            walk(t[0])
            walk(t[1])

    walk(b)
    return total_imbalance, total_nodes


def parallel_depth(b):
    """If all subtrees evaluate in parallel, what's the critical path depth?

    This is the depth of the tree if siblings evaluate in parallel.
    """
    if not isinstance(b, tuple):
        return 0
    return 1 + max(parallel_depth(b[0]), parallel_depth(b[1]))


def serial_depth(b):
    """Serial cost = number of internal nodes = n - 1."""
    if not isinstance(b, tuple):
        return 0
    return 1 + serial_depth(b[0]) + serial_depth(b[1])


# ============================================================
# Hardware design interpretation
# ============================================================

def hardware_profile(b, m):
    """Compute hardware tradeoff metrics for a bracketing."""
    pd = parallel_depth(b)
    sd = serial_depth(b)
    imbalance, internal_nodes = bracketing_balance(b)

    return {
        "parallel_latency": pd,      # depth assuming parallel execution
        "serial_ops": sd,             # total ops regardless of order
        "avg_imbalance": imbalance / max(internal_nodes, 1),
        "parallelism": sd / max(pd, 1),  # serial/parallel ratio
    }


# ============================================================
# Main demonstration: Stasheff at each Hadamard level
# ============================================================

def print_hadamard_stasheff_scaling():
    print("=" * 76)
    print("  The Stasheff polytope at each Hadamard level")
    print("=" * 76)
    print()
    print(f"  Hadamard at level m has m butterfly stages.")
    print(f"  Composing m stages = bracketing m items = vertex of Stasheff K_m.")
    print(f"  K_m has dim m-2 and C_{{m-1}} vertices.")
    print()
    print(f"  {'level m':>8}  {'WHT depth':>10}  {'K_m dim':>9}  {'# vertices':>11}  {'new axis at this level':>25}")
    print(f"  {'-'*8}  {'-'*10}  {'-'*9}  {'-'*11}  {'-'*25}")

    axes_added = [
        "(structure only)",
        "(structure only)",
        "parallel vs serial",
        "depth/breadth balance",
        "chunking pattern",
        "synchronization granularity",
        "burst vs continuous",
    ]

    for m in range(1, 8):
        dim = stasheff_dim(m) if m >= 2 else "n/a"
        verts = stasheff_vertices(m) if m >= 2 else 1
        axis = axes_added[m - 1] if m - 1 < len(axes_added) else f"axis #{m-2}"
        if m == 1:
            new_axis = "(no compose choice)"
        elif m == 2:
            new_axis = "(no compose choice yet)"
        else:
            new_axis = axis
        print(f"  {m:>8}  {m:>10}  {str(dim):>9}  {verts:>11}  {new_axis:>25}")

    print()
    print("  Pattern: dimension grows by 1 at each level.")
    print("  Each level UNLOCKS a new pivot axis = a new tradeoff choice.")


def print_stasheff_at_levels():
    """Enumerate bracketings at K_3, K_4, K_5 and show their hardware profiles."""
    print()
    print("=" * 76)
    print("  Bracketings at each level with hardware tradeoff profiles")
    print("=" * 76)

    for m in [3, 4, 5]:
        print()
        print("─" * 76)
        print(f"  Hadamard level m={m}, Stasheff K_{m}, dim={stasheff_dim(m)}")
        print("─" * 76)

        items = [f"s{i+1}" for i in range(m)]
        all_brackets = list(bracketings(items))

        print(f"  Number of bracketings: {len(all_brackets)} (= C_{m-1} = {catalan(m-1)})")
        print()
        print(f"  {'bracketing':>30}  {'parallel depth':>15}  {'serial ops':>12}  {'parallelism':>13}")
        print(f"  {'-'*30}  {'-'*15}  {'-'*12}  {'-'*13}")

        for b in all_brackets:
            prof = hardware_profile(b, m)
            bstr = bracketing_str(b)
            print(f"  {bstr:>30}  {prof['parallel_latency']:>15}  {prof['serial_ops']:>12}  {prof['parallelism']:>13.2f}")

        # Identify extremes
        max_par = max(all_brackets, key=lambda b: hardware_profile(b, m)['parallelism'])
        min_par = min(all_brackets, key=lambda b: hardware_profile(b, m)['parallelism'])
        print()
        print(f"  Most parallel:  {bracketing_str(max_par)}")
        print(f"  Most serial:    {bracketing_str(min_par)}")
        print(f"  These are the EXTREMA of the Stasheff polytope.")


def print_pivot_axes():
    print()
    print("=" * 76)
    print("  What each pivot axis means operationally")
    print("=" * 76)

    print("""
  At Hadamard level m, the Stasheff polytope K_m has dimension m-2.
  Each new dimension (each step up the Hadamard hierarchy) adds ONE
  axis of design choice. Cumulatively:

  ── At level 3 (K_3, dim 1) — FIRST PIVOT ─────────────────────────────────

    Available axis: PARALLEL vs SERIAL
    Bracketings of 3 stages: ((ab)c) or (a(bc))
      ((ab)c) — process first two, then add third  (more serial)
      (a(bc)) — process last two, then add first   (more serial, mirror)

    Mixed pivots (interior of K_3):
      Can overlap stages: start stage 'a' while 'bc' completes.
      This is INSTRUCTION-LEVEL PARALLELISM.

    Hardware implication:
      Choose dataflow direction (decimation in time vs frequency).
      Affects buffering, pipelining, latency vs throughput.

  ── At level 4 (K_4 pentagon, dim 2) — SECOND PIVOT ────────────────────────

    Available axes: (1) PARALLEL/SERIAL  +  (2) DEPTH/BREADTH BALANCE
    Bracketings: ((ab)c)d, (ab)(cd), (a(bc))d, a((bc)d), a(b(cd))

    The pentagon has FIVE vertices arranged in a 2D cycle:
      ((ab)c)d → (a(bc))d → a((bc)d) → a(b(cd)) → (ab)(cd) → ((ab)c)d

    Each edge of the pentagon = one rebracketing = one associativity move.
    The 5 vertices represent 5 distinct compute strategies.

    Hardware implication:
      Where to split a 4-stage pipeline: balanced ((ab)(cd)) gives
      best parallelism (depth 2); skewed gives worst (depth 3).
      Mixed strategies allow staggered start with synchronized end.

  ── At level 5 (K_5, dim 3) — THIRD PIVOT ─────────────────────────────────

    Adds: CHUNKING PATTERN  (how to group sub-stages into blocks)
    14 vertices in 3D associahedron.

    Hardware implication:
      Block size for SIMD/SIMT execution. Larger blocks = higher
      throughput but more synchronization overhead. The polytope
      contains all viable chunking strategies.

  ── At level 6+ (K_m, dim m-2) — HIGHER PIVOTS ────────────────────────────

    Each new level adds: SYNCHRONIZATION GRANULARITY, BURST PATTERNS,
                         REPRESENTATION SHARING, ...

    The interior of the polytope = compromises between extremes.
    The face structure = which choices are 'compatible' (composable).
""")


def print_polytope_face_structure():
    """Show how faces of K_m correspond to compatible choice combinations."""
    print("=" * 76)
    print("  Face structure: which combinations are coherent")
    print("=" * 76)

    print("""
  A point in K_m = a specific compute strategy.
  A face of K_m = a SUBSET of strategies that share some structure.

  Specifically: a face corresponds to a partial bracketing — some sub-stages
  are committed to a specific grouping, others remain free.

  ── Faces of K_4 (pentagon) ────────────────────────────────────────────────

    Vertices (0-faces): 5 specific strategies
    Edges (1-faces):    5 pairs of strategies sharing a sub-bracketing
    The pentagon itself (2-face): all 5 strategies

    Each EDGE is a coherent "design path" — you can move along it without
    changing the committed sub-structure. Each VERTEX is a fully-committed
    strategy.

  ── Faces of K_5 (3D associahedron) ────────────────────────────────────────

    Vertices: 14 strategies
    Edges:    21 pairs
    2-faces:  9 (mix of pentagons and squares)
    3-face:   1 (the whole polytope)

    The 9 two-dimensional faces are where TWO axes of choice are simultaneously
    available. The 6 pentagonal faces handle 5-strategy clusters; the 3 square
    faces handle 4-strategy clusters with different topology.

  ── Operationally ─────────────────────────────────────────────────────────

    A face of dimension d = a hardware/software design with d remaining
    free axes. As we 'commit' design decisions (move from interior to
    boundary), we lower the dimension and constrain the remaining choices.

    The FULL POLYTOPE corresponds to "anything goes — choose at runtime."
    A VERTEX corresponds to "everything fixed — pure hardware."
    EDGES correspond to "one axis of runtime choice."

    Hardware design = choosing which face to specialize to.
""")


def print_chart_implications():
    print("=" * 76)
    print("  Chart implications: composition design space")
    print("=" * 76)

    print("""
  Our chart operates at multiple Hadamard levels. At each level, the
  Stasheff polytope tells us how to COMPOSE the corresponding operations:

  ── Level 1 (S_3, K_1 = point) ─────────────────────────────────────────────

    No compose-choice. The 3-axis structure is fixed.
    Operations: cons, left, right, eq, var, is_var.
    These primitives have NO BRACKETING CHOICE — they're atomic.

  ── Level 2 (Fano, K_2 = point still — wait, m=2 means 2 stages → K_2) ────

    Actually, at Hadamard level m=2 we have 2 butterfly stages.
    K_2 has 0 dimensions (a point) — still no real choice.
    But at level m=3 (Fano!), K_3 = interval, dim 1.

    Hadamard-3 (Fano level): K_3 = first PIVOT axis available.
    Choice: process all 3 axes (e_1, e_2, e_3) in parallel, or sequentially.

    Chart operation affected: apply, interp.
    These can be either:
      ((e_1 e_2) e_3) — sequential reduction (left-leaning)
      (e_1 (e_2 e_3)) — sequential reduction (right-leaning)
      e_1 ∥ e_2 ∥ e_3 — parallel (interior of K_3)

  ── Level 3 (tesseract, K_4 pentagon, dim 2) ──────────────────────────────

    TWO pivot axes: parallel/serial × depth/breadth.
    14-stage compositions of multiple move-cycles.

    Chart operation affected: strategic move sequences (multi-M-move plans).
    The pentagon's 5 vertices give 5 distinct strategy archetypes.

  ── Level 4+ (K_5 and higher) ─────────────────────────────────────────────

    THREE+ pivot axes. Higher-order strategies.
    Long-horizon agent coordination, plan composition.

    Each new level adds a new degree of design freedom.

  ── Composition coherence ─────────────────────────────────────────────────

    The KEY: at any level, choosing a vertex of K_m commits to a specific
    composition. Different vertices yield DIFFERENT compute profiles
    (latency, parallelism, sync requirements) but produce the SAME OUTPUT
    (this is cocycle invariance from M8).

    The Stasheff polytope is the SPACE OF COCYCLE-EQUIVALENT REPRESENTATIONS
    at each level. Each vertex is a representative; the polytope structure
    encodes which representatives are reachable from which.

    This is what makes coherent hardware acceleration possible: the
    polytope's homotopy gives us the freedom to choose different compute
    strategies (different vertices) for hardware/software purposes WITHOUT
    changing the operational semantics.
""")


def print_engineering_summary():
    print("=" * 76)
    print("  Engineering summary: the Stasheff axes and their uses")
    print("=" * 76)

    print("""
  At Hadamard level m, the m-2 dimensions of K_m correspond to:

  ┌──────────────┬──────────────────────────────────────────────────────────┐
  │ Dimension d  │ Pivot axis at this dimension                             │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 1 (K_3)  │ Parallel ↔ Serial                                        │
  │              │   Critical for SIMD width vs pipeline depth              │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 2 (K_4)  │ Depth/breadth balance                                    │
  │              │   Critical for cache vs register pressure                │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 3 (K_5)  │ Chunking pattern                                         │
  │              │   Critical for memory hierarchy traversal                │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 4 (K_6)  │ Synchronization granularity                              │
  │              │   Critical for async/sync, distributed compute           │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 5 (K_7)  │ Burst vs continuous                                      │
  │              │   Critical for power/throughput tradeoffs                │
  ├──────────────┼──────────────────────────────────────────────────────────┤
  │ d = 6 (K_8)  │ Representation sharing                                   │
  │              │   Critical for multi-tenancy, virtualization             │
  └──────────────┴──────────────────────────────────────────────────────────┘

  Each NEW Hadamard level = one new design axis becoming available.
  Hardware designers PICK A FACE of the appropriate K_m polytope —
  specializing some axes (boundary), leaving others free (interior).

  The shadow-engineer skill's 3-axis decomposition (data, compute, state)
  corresponds to PG(2, F_2) at Hadamard level 3. The Stasheff polytope
  governing compositions of these three axes is K_3 (an interval).

  This is why the architecture has exactly ONE pivot axis at this level:
  parallel-vs-serial composition of (data, compute, state) operations.
""")


def main():
    print_hadamard_stasheff_scaling()
    print_stasheff_at_levels()
    print_pivot_axes()
    print_polytope_face_structure()
    print_chart_implications()
    print_engineering_summary()


if __name__ == "__main__":
    main()
