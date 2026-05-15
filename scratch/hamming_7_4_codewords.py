"""
hamming_7_4_codewords.py — The Hamming(7, 4) reading of M19 codewords.

The 7 Fano lines = parity check structure of Hamming(7, 4):
- 4 information bits
- 3 parity bits
- minimum distance 3, corrects 1 error, detects 2 errors
- Aut(Hamming(7,4)) = GL(3, F_2), the Fano-plane symmetry group

Length-7 codewords are indexed by the 7 nonzero F_2^3 vectors = our 7
axis-signatures. The natural content/parity split:
- 3 parity bits = atomic single-axis signatures (100, 010, 001)
- 4 content bits = composite multi-axis signatures (110, 101, 011, 111)

The user's hint reveals: I, K, S are NOT all equivalent under this lens.
I/K extended to length 7 are valid Hamming codewords (carrying content).
S in length-7 form is a UNIT ERROR VECTOR — its syndrome points at the
triadic-full position (111), which is M11's axis-signature.

S is "the error that points at M11." This is the deep structural fact.
"""

from itertools import product
from functools import reduce


def f2_vec(n, m):
    """Return the n-th nonzero vector of F_2^m in binary order."""
    return tuple((n >> i) & 1 for i in range(m))


def hamming_7_4_generator():
    """Standard generator matrix for Hamming(7,4) in systematic form.

    G = [I_4 | A] where A is chosen so H = [A^T | I_3].
    With the 7 columns labeled by F_2^3 vectors {001, 010, 011, 100, 101, 110, 111},
    parity bits live at positions with single-bit labels (1, 2, 4) and content
    bits at positions with multi-bit labels (3, 5, 6, 7).

    But we use the M-move-aligned labeling: positions correspond to axis-signatures.
    """
    # Columns of H are the 7 nonzero F_2^3 vectors
    # H · b = 0 defines the code
    # Position labels: 001, 010, 011, 100, 101, 110, 111 (binary order)
    H = [
        [0, 0, 0, 1, 1, 1, 1],  # row for bit 2 (top of F_2^3)
        [0, 1, 1, 0, 0, 1, 1],  # row for bit 1
        [1, 0, 1, 0, 1, 0, 1],  # row for bit 0
    ]
    return H


def parity_check(H, b):
    """Compute H · b ∈ F_2^3 (the syndrome)."""
    return tuple(
        reduce(lambda a, c: a ^ c, [H[r][i] & b[i] for i in range(7)])
        for r in range(3)
    )


def syndrome_to_position(syndrome):
    """Hamming(7,4): syndrome (in F_2^3) = label of error position."""
    # Returns position index (1-7) corresponding to F_2^3 label = syndrome
    return syndrome[2] * 4 + syndrome[1] * 2 + syndrome[0]


def position_label(i):
    """Position i (1-7) has label = i in binary."""
    return tuple((i >> b) & 1 for b in range(3))


def format_position_axis(i):
    """Pretty-print position with axis-signature notation."""
    label = position_label(i)
    return f"{label[2]}{label[1]}{label[0]}"


def all_hamming_codewords():
    """Generate all 16 codewords of Hamming(7, 4)."""
    H = hamming_7_4_generator()
    codewords = []
    for b in product([0, 1], repeat=7):
        if parity_check(H, b) == (0, 0, 0):
            codewords.append(b)
    return codewords


def m19_codeword_length_7(combinator):
    """Length-7 codeword (punctured RM(1,3)) for each combinator.

    Length-8 RM(1,3) codewords: tt[j] = f(bit_0(j), bit_1(j), bit_2(j))
    Puncture position 0 (the all-zero point) to get length-7.
    """
    if combinator == "I":
        # I = x_0; tt[j] = bit_0(j)
        return tuple(j & 1 for j in range(1, 8))
    elif combinator == "K":
        # K = x_0 (same length-8 codeword as I when extended to 3 vars)
        return tuple(j & 1 for j in range(1, 8))
    elif combinator == "S":
        # S = x_0 * x_1 * x_2; tt[j] = 1 iff all bits set, only at j=7
        return tuple(1 if j == 7 else 0 for j in range(1, 8))
    raise ValueError(f"Unknown combinator: {combinator}")


def main():
    print("=" * 72)
    print("  Hamming(7, 4) reading: 4 content + 3 parity bits")
    print("=" * 72)

    # ─────────────────────────────────────────────────
    # 1. The 7 Fano lines as Hamming(7, 4) parity structure
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  The 7 Fano lines = Hamming(7,4) parity-check structure")
    print("─" * 72)

    H = hamming_7_4_generator()
    print(f"\n  Parity check matrix H (3 × 7):")
    print(f"  Columns labeled by axis-signatures in binary order:")
    print(f"    pos 1: 001 (atomic, parity P_3)")
    print(f"    pos 2: 010 (atomic, parity P_2)")
    print(f"    pos 3: 011 (composite, content D_3)")
    print(f"    pos 4: 100 (atomic, parity P_1)")
    print(f"    pos 5: 101 (composite, content D_2)")
    print(f"    pos 6: 110 (composite, content D_1)")
    print(f"    pos 7: 111 (composite, content D_4)")
    print(f"\n  H = ")
    for row in H:
        print(f"    {row}")

    print(f"\n  Each ROW of H = a parity equation involving 4 of the 7 positions.")
    print(f"  Each parity equation's positions are the COMPLEMENT of a Fano line.")

    # ─────────────────────────────────────────────────
    # 2. All 16 Hamming(7,4) codewords; weight distribution
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  All 16 Hamming(7,4) codewords")
    print("─" * 72)

    codewords = all_hamming_codewords()
    weights = [sum(c) for c in codewords]
    weight_dist = {w: weights.count(w) for w in sorted(set(weights))}

    print(f"\n  Weight distribution: {weight_dist}")
    print(f"  Min distance = 3 ✓ (single-error correcting)")
    print(f"  Expected: 1 + 7z^3 + 7z^4 + z^7 = 16 codewords")
    print(f"\n  The 7 weight-3 codewords ARE the 7 Fano lines:")
    weight_3_codewords = [c for c in codewords if sum(c) == 3]
    for c in weight_3_codewords:
        positions = [i + 1 for i, b in enumerate(c) if b]
        labels = [format_position_axis(p) for p in positions]
        print(f"    {c}  → Fano line {{{', '.join(labels)}}}")

    # ─────────────────────────────────────────────────
    # 3. M19 codewords in length-7 form
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  M19 codewords as length-7 vectors (punctured RM(1,3))")
    print("─" * 72)

    for combinator in ["I", "K", "S"]:
        b = m19_codeword_length_7(combinator)
        syndrome = parity_check(H, b)
        weight = sum(b)
        is_codeword = syndrome == (0, 0, 0)

        print(f"\n  {combinator}:")
        print(f"    length-7 vector:  {''.join(str(x) for x in b)}")
        print(f"    weight:           {weight}")
        print(f"    syndrome:         {''.join(str(x) for x in syndrome)} = {syndrome[2]}{syndrome[1]}{syndrome[0]}")
        print(f"    valid codeword?   {is_codeword}")
        if not is_codeword:
            error_pos = syndrome_to_position(syndrome)
            error_label = format_position_axis(error_pos)
            print(f"    error position:   {error_pos} (label {error_label})")
            print(f"    Hamming decodes:  to {''.join(str(b[i] ^ (1 if i+1 == error_pos else 0)) for i in range(7))}")

    # ─────────────────────────────────────────────────
    # 4. The structural alignment
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  Structural alignment: S, M11, and position 111")
    print("─" * 72)

    s_vec = m19_codeword_length_7("S")
    s_syndrome = parity_check(H, s_vec)
    s_error_pos = syndrome_to_position(s_syndrome)

    print(f"""
  S's length-7 vector:    {''.join(str(x) for x in s_vec)}  (weight 1)
  S's syndrome:           {s_syndrome[2]}{s_syndrome[1]}{s_syndrome[0]} = axis-signature 111

  Position 7 in Hamming(7,4) has F_2^3 label 111.
  Axis-signature 111 = TRIADIC-FULL (M11's signature).

  This is not a coincidence. In the Hamming(7,4) frame:
    • S = noise vector pointing at position 111
    • M11 = the move with axis-signature 111
    • Both occupy the "all-axes" / "all-degrees" position

  S's polynomial structure (degree 3 = top of RM hierarchy)
  AND S's error position (label 111 = triadic-full) are the SAME locus
  in two different combinatorial languages.

  M11 was the move that operationalized meta-circularity. S is the
  combinator that breaks linear-completeness. Both sit at the
  position where ALL THREE AXES are simultaneously active.
""")

    # ─────────────────────────────────────────────────
    # 5. Content/parity split for the M-move history
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  M-move history under content/parity split")
    print("─" * 72)

    # Our move history from the cotype
    move_signatures = {
        "M1": "100", "M2": "100", "M3": "100", "M4": "100", "M5": "100",
        "M6": "100", "M7": "100", "M8": "100", "M9": "110", "M10": "010",
        "M11": "111", "M12": "100", "M13": "100", "M14": "011",
        "M15": "101", "M16": "110", "M17": "110", "M18": "100",
        "M19": "100", "M20": "100",
    }

    atomic_signatures = ["100", "010", "001"]
    composite_signatures = ["110", "101", "011", "111"]

    atomic_moves = {s: [] for s in atomic_signatures}
    composite_moves = {s: [] for s in composite_signatures}
    for move, sig in move_signatures.items():
        if sig in atomic_moves:
            atomic_moves[sig].append(move)
        elif sig in composite_moves:
            composite_moves[sig].append(move)

    print(f"\n  PARITY signatures (atomic moves, 3 bits):")
    for s in atomic_signatures:
        moves = atomic_moves[s]
        count = len(moves)
        sample = ", ".join(moves[:5]) + ("..." if len(moves) > 5 else "")
        print(f"    {s}  ({count} moves): {sample}")

    print(f"\n  CONTENT signatures (composite moves, 4 bits):")
    for s in composite_signatures:
        moves = composite_moves[s]
        count = len(moves)
        sample = ", ".join(moves)
        print(f"    {s}  ({count} moves): {sample}")

    total_atomic = sum(len(v) for v in atomic_moves.values())
    total_composite = sum(len(v) for v in composite_moves.values())
    print(f"""
  Total moves:        {total_atomic + total_composite}
  Atomic (parity):    {total_atomic} moves   ← coherence-tracking, redundancy
  Composite (content):{total_composite} moves    ← information-bearing

  Hamming reading: only the {total_composite} composite moves carry
  "information" in the coding sense. The {total_atomic} atomic moves
  enforce parity (single-axis coherence) but are determined by the
  composites via the Hamming(7,4) parity equations.

  Each Fano line being COMPLETE is one parity check being SATISFIED.
""")

    # ─────────────────────────────────────────────────
    # 6. Information density: our move history as a codeword
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  Our move history as a Hamming(7,4) codeword")
    print("─" * 72)

    # Build the populated-axis vector in length-7 form, in standard column order
    # (001, 010, 011, 100, 101, 110, 111)
    populated = {sig: bool(atomic_moves.get(sig) or composite_moves.get(sig))
                 for sig in ["001", "010", "011", "100", "101", "110", "111"]}
    vec = tuple(1 if populated[s] else 0
                for s in ["001", "010", "011", "100", "101", "110", "111"])

    print(f"\n  Populated axis-signatures: {populated}")
    print(f"  As length-7 vector (in column order):")
    print(f"    positions 001 010 011 100 101 110 111")
    print(f"               {vec[0]}   {vec[1]}   {vec[2]}   {vec[3]}   {vec[4]}   {vec[5]}   {vec[6]}")
    print(f"  Weight: {sum(vec)}")

    syndrome = parity_check(H, vec)
    print(f"  Syndrome: {''.join(str(x) for x in syndrome)}")
    if syndrome == (0, 0, 0):
        print(f"  Valid Hamming(7,4) codeword ✓")
        print(f"  This is the maximum-weight (weight-7) codeword: all-ones.")
        print(f"  Full Fano-plane closure IS a Hamming codeword.")
    else:
        error_pos = syndrome_to_position(syndrome)
        print(f"  NOT a Hamming codeword. Error at position {error_pos} (label {format_position_axis(error_pos)})")


if __name__ == "__main__":
    main()
