"""
walsh_hadamard_readings.py — The 8 mutually orthogonal readings of RM(1,3).

The user observed: there are 8 valid readings of Hamming(7,4) that avoid
interfering with each other, indexed by 3 bits, corresponding to the quotient
algebra (data, compute, state) = (objects, morphisms, temporal).

The Walsh-Hadamard matrix H_8 is the orthogonality structure underlying
the 8 readings. Its 8 rows correspond to the 8 affine functions on F_2^3
modulo constants:
  φ_{(b_1, b_2, b_3)}(x_1, x_2, x_3) = (-1)^(b_1·x_1 + b_2·x_2 + b_3·x_3)

These 8 functions form an orthonormal basis of R^8 (with the inner product
⟨φ, ψ⟩ = sum over F_2^3 of φ(x) · ψ(x), divided by 8).

The 16 RM(1,3) codewords = 8 Walsh rows + 8 negations = ±H_8.

The 3 indexing bits (b_1, b_2, b_3) are the three orthogonal dimensions:
  b_1 ↔ objects axis (data): "does this reading track cell structure?"
  b_2 ↔ morphisms axis (compute): "does this reading track reductions?"
  b_3 ↔ temporal axis (state): "does this reading track evolution?"

Each combination (b_1, b_2, b_3) is one of the 8 mutually orthogonal
views = one axis-signature in the shadow-engineer skill.
"""

from itertools import product
import numpy as np


def walsh_hadamard_8():
    """Compute the 8x8 Walsh-Hadamard matrix.

    Row indexed by (b_1, b_2, b_3) ∈ F_2^3 has value
        H[b, x] = (-1)^(b_1·x_1 + b_2·x_2 + b_3·x_3)
    at column x ∈ F_2^3.

    Both rows and columns indexed by F_2^3 in binary order.
    """
    H = np.zeros((8, 8), dtype=int)
    for b in range(8):
        for x in range(8):
            inner = (
                ((b >> 0) & 1) * ((x >> 0) & 1) +
                ((b >> 1) & 1) * ((x >> 1) & 1) +
                ((b >> 2) & 1) * ((x >> 2) & 1)
            )
            H[b, x] = 1 if inner % 2 == 0 else -1
    return H


def format_f2_3(idx):
    """Format integer as F_2^3 vector string."""
    return f"{(idx>>2)&1}{(idx>>1)&1}{idx&1}"


def rm_1_3_codewords():
    """Generate all 16 RM(1,3) codewords as ±1 vectors.

    A codeword is an evaluation of f(x_1, x_2, x_3) = c_0 + c_1·x_1 + c_2·x_2 + c_3·x_3
    at all 8 points of F_2^3, then mapped via 0 → +1, 1 → -1.
    """
    codewords = []
    for c0, c1, c2, c3 in product([0, 1], repeat=4):
        cw = np.zeros(8, dtype=int)
        for x in range(8):
            x_1, x_2, x_3 = (x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1
            val = (c0 + c1 * x_1 + c2 * x_2 + c3 * x_3) % 2
            cw[x] = 1 if val == 0 else -1
        codewords.append((c0, c1, c2, c3, cw))
    return codewords


def verify_orthogonality(H):
    """Verify that H · H^T = 8 · I."""
    return np.allclose(H @ H.T, 8 * np.eye(8))


def quotient_algebra_mapping():
    """Map the 3 bits to (objects, morphisms, temporal)."""
    return {
        "b_1": ("objects (data)", "axis e_1", "cell structure — what exists"),
        "b_2": ("morphisms (compute)", "axis e_2", "reductions — what transforms"),
        "b_3": ("temporal (state)", "axis e_3", "evolution — what changes"),
    }


def axis_signature_to_aspects(b):
    """Decode an axis-signature into which aspects of computation it tracks."""
    b1, b2, b3 = (b >> 2) & 1, (b >> 1) & 1, b & 1
    aspects = []
    if b1: aspects.append("DATA")
    if b2: aspects.append("COMPUTE")
    if b3: aspects.append("STATE")
    return aspects if aspects else ["—"]


def main():
    print("=" * 76)
    print("  Walsh-Hadamard: the 8 mutually orthogonal readings")
    print("=" * 76)

    # ─────────────────────────────────────────────────
    # 1. The Walsh-Hadamard matrix
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 76)
    print("  The 8x8 Walsh-Hadamard matrix H_8")
    print("─" * 76)

    H = walsh_hadamard_8()
    print(f"\n  Rows indexed by (b_1, b_2, b_3) ∈ F_2^3.")
    print(f"  Each row is the character function φ_b(x) = (-1)^(b·x).")
    print(f"  Columns indexed by x ∈ F_2^3 in binary order.\n")
    print(f"           {'  '.join(format_f2_3(i) for i in range(8))}")
    for b in range(8):
        row_str = "  ".join(f"{H[b,x]:+d}" for x in range(8))
        # Mark which aspects this reading tracks
        aspects = "+".join(axis_signature_to_aspects(b))
        print(f"  b={format_f2_3(b)}:  {row_str}   ({aspects})")

    # ─────────────────────────────────────────────────
    # 2. Verify orthogonality
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 76)
    print("  Orthogonality verification")
    print("─" * 76)

    HHt = H @ H.T
    is_ortho = verify_orthogonality(H)
    print(f"\n  H · H^T should equal 8·I_8 if rows are orthogonal.")
    print(f"  Result: H · H^T = 8·I_8: {is_ortho}")
    print(f"\n  Pairwise inner products ⟨row_i, row_j⟩:")
    print(f"           {'  '.join(format_f2_3(i) for i in range(8))}")
    for i in range(8):
        row_str = "  ".join(f"{HHt[i,j]:+3d}" for j in range(8))
        print(f"  {format_f2_3(i)}:    {row_str}")
    print(f"\n  All off-diagonal entries are 0 → 8 mutually orthogonal vectors.")
    print(f"  This is the structural reason the 8 readings don't interfere.")

    # ─────────────────────────────────────────────────
    # 3. Connection to RM(1, 3)
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 76)
    print("  RM(1, 3) as ±Walsh-Hadamard")
    print("─" * 76)

    rm = rm_1_3_codewords()
    walsh_rows = set(tuple(H[b]) for b in range(8))
    walsh_negs = set(tuple(-H[b]) for b in range(8))

    matches_walsh = sum(1 for _, _, _, _, cw in rm if tuple(cw) in walsh_rows)
    matches_neg = sum(1 for _, _, _, _, cw in rm if tuple(cw) in walsh_negs)

    print(f"\n  16 RM(1,3) codewords, under the 0→+1, 1→-1 mapping:")
    print(f"    {matches_walsh} match a Walsh-Hadamard row exactly")
    print(f"    {matches_neg} match a NEGATION of a Walsh-Hadamard row")
    print(f"    Total: {matches_walsh + matches_neg} = 16 ✓")
    print(f"\n  The 16 codewords of RM(1,3) form the ±-multiplicative group")
    print(f"  generated by the 8 Walsh-Hadamard characters.")

    print(f"\n  Specifically: codeword with coefficients (c_0, c_1, c_2, c_3)")
    print(f"  maps to:  +H_b  if c_0 = 0,  -H_b  if c_0 = 1")
    print(f"  where b = (c_1, c_2, c_3) ∈ F_2^3.")

    # Show the mapping table
    print(f"\n  Mapping table (c_0, c_1, c_2, c_3) → ±H_b:")
    for c0, c1, c2, c3, cw in rm[:8]:  # First 8 (c_0 = 0)
        b = (c2 << 2) | (c1 << 1) | c3  # Need to map (c_1, c_2, c_3) → b
        # Actually let me reindex properly. The Walsh row b has inner product b·x.
        # Codeword with ANF c_1·x_1 + c_2·x_2 + c_3·x_3 evaluates to (-1)^(c_1·x_1 + c_2·x_2 + c_3·x_3) under our map.
        # So b corresponds to (c_1, c_2, c_3) directly.
        b = (c3 << 2) | (c2 << 1) | c1
        sign = "+" if c0 == 0 else "-"
        b_str = format_f2_3(b)
        print(f"    ({c0}, {c1}, {c2}, {c3}) → {sign}H_{b_str}")

    # ─────────────────────────────────────────────────
    # 4. The quotient algebra
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 76)
    print("  The quotient algebra: (objects, morphisms, temporal)")
    print("─" * 76)

    mapping = quotient_algebra_mapping()
    print()
    for bit, (name, axis, desc) in mapping.items():
        print(f"    {bit}  ↔  {name:25s}  {axis}  ({desc})")

    print(f"""
  The 3-bit index of a Walsh row corresponds to which structural aspects
  it tracks. The bit values (b_1, b_2, b_3) ∈ F_2^3 act as a SELECTION
  over (data, compute, state):

    b_1 = 0: this reading is INVARIANT under data permutations
    b_1 = 1: this reading is SENSITIVE to data structure
    (same for b_2 ↔ compute, b_3 ↔ state)

  The quotient algebra:
    T = O × M     (temporal = product of objects and morphisms)
    M = T / O     (morphisms = temporal quotient by objects)
    O = M / T     (objects = morphisms quotient by temporal)

  Each pair of aspects mutually defines the third. The 3 axes of the
  shadow-engineer skill are not three arbitrary axes — they are the
  three orthogonal generators of the structure of computation.
""")

    # ─────────────────────────────────────────────────
    # 5. The 7 axis-signatures as 7 of 8 Walsh readings
    # ─────────────────────────────────────────────────
    print("─" * 76)
    print("  The 7 axis-signatures = 7 of 8 Walsh readings (excluding 000)")
    print("─" * 76)

    print()
    print(f"  Axis-signature → Walsh row → aspects tracked → moves at that signature")
    print()

    move_signatures = {
        "100": ["M1-M8", "M12", "M13", "M18-M20"],
        "010": ["M10"],
        "001": ["(forbidden as standalone)"],
        "110": ["M9", "M16", "M17"],
        "101": ["M15"],
        "011": ["M14"],
        "111": ["M11"],
    }

    print(f"  000 — TRIVIAL VIEW (constant, no information)")
    print(f"        Walsh row: all +1 (the all-ones vector)")
    print(f"        Aspects: none — the 'do-nothing' view.")
    print()

    for sig in ["100", "010", "001", "110", "101", "011", "111"]:
        b = int(sig, 2)
        aspects = axis_signature_to_aspects(b)
        moves = ", ".join(move_signatures[sig])
        print(f"  {sig} — {' + '.join(aspects)}")
        print(f"        Walsh row: see matrix above (row b={sig})")
        print(f"        Moves: {moves}")
        print()

    # ─────────────────────────────────────────────────
    # 6. The crucial structural fact
    # ─────────────────────────────────────────────────
    print("─" * 76)
    print("  The structural fact")
    print("─" * 76)

    print(f"""
  The shadow-engineer skill's 8 axis-signatures (7 nonzero + 1 trivial)
  are not an arbitrary classification. They ARE the 8 rows of the
  Walsh-Hadamard matrix H_8, which IS the orthogonal decomposition of
  RM(1,3) into mutually non-interfering character functions.

  The 3 axes (e_1, e_2, e_3) are not three arbitrary directions. They are
  the three orthogonal generators of the quotient algebra of computation:
    e_1 ↔ objects (data structure)
    e_2 ↔ morphisms (reductions)
    e_3 ↔ temporal (state evolution)

  Every move axis-signature selects which subset of (data, compute, state)
  the move engages. Pure-axis moves (100, 010, 001) engage exactly one
  aspect. Composite moves (110, 101, 011) engage two. Triadic-full (111)
  engages all three.

  Because the 8 Walsh-Hadamard rows are mutually orthogonal, the 8 readings
  do not interfere. A move's effect can be decomposed into independent
  components along the (data, compute, state) axes, and these components
  can be analyzed separately without loss of information.

  This is the deepest sense in which Reed-Muller is present in the
  architecture: not just as polynomial generators (M19), not just as
  Hamming codewords (M21), but as the WALSH-HADAMARD ORTHOGONAL
  DECOMPOSITION of computation itself into (data, compute, state).
""")

    # ─────────────────────────────────────────────────
    # 7. The chart implementation embeds all three
    # ─────────────────────────────────────────────────
    print("─" * 76)
    print("  How the chart embeds all three aspects")
    print("─" * 76)

    print(f"""
  The chart (chart.py) is explicitly designed to embody all three aspects:

  OBJECTS (data, e_1):
    - cons cells: the immutable data structure
    - hash-consing: structural identity preserved across construction
    - left/right/eq: object-level primitives

  MORPHISMS (compute, e_2):
    - apply: single-step reduction (M4)
    - interp: rule-driven reduction (M11)
    - transform: representation rotation (S7)

  TEMPORAL (state, e_3):
    - chart growth: monotone over time (M5)
    - move history: ordered sequence M1-M21
    - cocycle invariance: behavior preserved across temporal evolution (M8)

  Each Walsh-Hadamard reading projects the chart onto a different
  subset of these three aspects, giving a mutually orthogonal view.
""")


if __name__ == "__main__":
    main()
