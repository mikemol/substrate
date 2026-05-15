"""
hadamard_basis.py — M39: the architecture as symmetry-governed Hadamard basis mixing.

The witness axis in the unified codeword (M38) is not just an axis label —
it indexes a Walsh–Hadamard character of F_2^n, where n is the architecture's level.

At level n:
    domain          = F_2^n  (2^n points)
    basis           = 2^n WHT characters χ_k(x) = (-1)^{k·x}, indexed by k ∈ F_2^n
    operations      = symmetry-governed mixings of basis elements
    codeword width  = 1 (chirality) + n (pairing) + n (witness) = 2n + 1

This is the precise framing: computation in this architecture is the structured
mixing of WHT basis functions, with the parity-coded symmetries (V_4 / Z_3 / Z_2)
controlling how mixings compose.
"""

from itertools import product
from typing import Callable
from chart_chained import ChartChained
from unified_address import encode_op, AXIS_TO_LABEL, V4_XOR_MASK
from meta_protocol import AXES


# ============================================================
# Walsh–Hadamard characters at arbitrary level
# ============================================================

def wht_inner_product(k_bits, x_bits, n):
    """The F_2 inner product k · x = ⊕_i k_i x_i."""
    return bin(k_bits & x_bits).count('1') % 2


def character(k_bits, n):
    """Return the WHT character χ_k : F_2^n → {±1}, χ_k(x) = (-1)^{k·x}."""
    def chi(x_bits):
        return -1 if wht_inner_product(k_bits, x_bits, n) else +1
    chi.__name__ = f"χ_{k_bits:0{n}b}"
    return chi


def all_characters(n):
    """Return the full set of 2^n WHT characters at level n."""
    return {k: character(k, n) for k in range(2**n)}


def character_as_vector(k_bits, n):
    """Express χ_k as its vector of evaluations χ_k(0), χ_k(1), ..., χ_k(2^n-1)."""
    return tuple(character(k_bits, n)(x) for x in range(2**n))


# ============================================================
# Verify the basis properties: orthogonality and completeness
# ============================================================

def inner_product_of_chars(k1, k2, n):
    """Σ_x χ_{k1}(x) · χ_{k2}(x) — should equal 2^n if k1==k2, else 0."""
    return sum(character(k1, n)(x) * character(k2, n)(x) for x in range(2**n))


def verify_orthogonality(n):
    """The 2^n characters are mutually orthogonal under the F_2^n inner product."""
    for k1 in range(2**n):
        for k2 in range(2**n):
            ip = inner_product_of_chars(k1, k2, n)
            expected = 2**n if k1 == k2 else 0
            if ip != expected:
                return False, (k1, k2, ip, expected)
    return True, None


def verify_completeness(n):
    """The 2^n characters span the function space F_2^n → R."""
    # Any function f : F_2^n → R can be expanded as f = Σ_k <f, χ_k> χ_k / 2^n
    # We verify by showing the change-of-basis matrix is invertible (= the Hadamard matrix).
    H = [[character(k, n)(x) for x in range(2**n)] for k in range(2**n)]
    # H is 2^n × 2^n. Hadamard matrix property: H · H^T = 2^n · I
    N = 2**n
    for i in range(N):
        for j in range(N):
            dot = sum(H[i][k] * H[j][k] for k in range(N))
            expected = N if i == j else 0
            if dot != expected:
                return False, (i, j, dot, expected)
    return True, None


# ============================================================
# The architecture's correspondence: witness axis → WHT character
# ============================================================

def axis_to_character_index(axis: str) -> int:
    """Each axis label is a 2-bit index into the level-2 character basis.

    D = 00 → χ_00 (the constant character, "DC component")
    C = 01 → χ_01
    S = 10 → χ_10
    W = 11 → χ_11
    """
    return AXIS_TO_LABEL[axis]


def witness_character(op):
    """Return the WHT character that an operation's witness axis indexes."""
    return character(axis_to_character_index(op.witness), n=2)


# ============================================================
# Demonstrate at level 2
# ============================================================

def demo():
    print("=" * 78)
    print("  hadamard_basis.py — M39: computation as Hadamard basis mixing")
    print("=" * 78)
    print()

    # ============================================================
    # Show the 4 characters at level 2
    # ============================================================
    print("Level 2 (F_2^2): 4 = 2^2 Walsh–Hadamard characters")
    print()
    print(f"  {'k (bits)':<10} {'k (label)':<10} {'name':<8} χ(00) χ(01) χ(10) χ(11)")
    print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for k in range(4):
        chi = character(k, n=2)
        label = next((axis for axis, l in AXIS_TO_LABEL.items() if l == k), '?')
        vals = [f"{chi(x):+d}" for x in range(4)]
        print(f"  {k:02b}         axis={label:<5}  χ_{k:02b}     {vals[0]}    {vals[1]}    {vals[2]}    {vals[3]}")

    # ============================================================
    # Verify the basis properties
    # ============================================================
    print()
    print("  Basis properties at level 2:")
    ortho, ortho_fail = verify_orthogonality(n=2)
    complete, complete_fail = verify_completeness(n=2)
    print(f"    [{'✓' if ortho else '✗'}] orthogonality:  ⟨χ_k, χ_k'⟩ = 4 δ_{{k,k'}}")
    print(f"    [{'✓' if complete else '✗'}] completeness:   H · H^T = 4 · I  (Hadamard matrix property)")

    # ============================================================
    # Show the witness-axis ↔ character correspondence
    # ============================================================
    print()
    print("=" * 78)
    print("  Each operation's witness axis indexes a WHT character")
    print("=" * 78)
    print()

    c = ChartChained()
    print(f"  {'op':<30} {'witness':<8} {'label':<6} {'character':<10}")
    print(f"  {'-'*30} {'-'*8} {'-'*6} {'-'*10}")
    for op in sorted(c.registry.all(), key=lambda o: (o.witness, o.name))[:8]:
        chi = witness_character(op)
        idx = axis_to_character_index(op.witness)
        print(f"  {op.name:<30} {op.witness:<8} {idx:02b}     {chi.__name__}")
    print(f"  ... ({len(c.registry)} total)")

    # ============================================================
    # The "DC component" / constant character
    # ============================================================
    print()
    print("=" * 78)
    print("  The 'DC component' (M22 nomenclature) is χ_00 — the constant character")
    print("=" * 78)
    print()
    dc_count = sum(1 for op in c.registry.all() if op.witness == 'D')
    print(f"  At level 2, axis D = label 00 ↔ χ_00 (constant +1 everywhere).")
    print(f"  Operations witnessed by D: {dc_count} (each indexes the DC character).")
    print()
    print("  The other characters (χ_01, χ_10, χ_11) are non-trivial parity probes.")
    print("  Each operation 'tags' its validation against one of the 4 basis characters.")

    # ============================================================
    # Higher-level scaling
    # ============================================================
    print()
    print("=" * 78)
    print("  Scaling: 2^n characters at level n")
    print("=" * 78)
    print()
    print(f"  {'level n':<10} {'axes':<6} {'characters 2^n':<18} {'codeword 2n+1':<14} {'comment'}")
    print(f"  {'-'*10} {'-'*6} {'-'*18} {'-'*14} {'-'*30}")
    print(f"  {'2 (now)':<10} {'4':<6} {'4':<18} {'5 bits':<14} F_2^2, current level")
    print(f"  {'3':<10} {'8':<6} {'8':<18} {'7 bits':<14} F_2^3, Hamming(7,4) layout")
    print(f"  {'4':<10} {'16':<6} {'16':<18} {'9 bits':<14} F_2^4, extended (Hamming-like)")
    print(f"  {'n':<10} {'2^n':<6} {'2^n':<18} {'2n+1 bits':<14} F_2^n, parity-coded basis")

    # Verify orthogonality at level 3 as a check
    print()
    ortho3, _ = verify_orthogonality(n=3)
    complete3, _ = verify_completeness(n=3)
    print(f"  Level 3 verification:")
    print(f"    [{'✓' if ortho3 else '✗'}] 8 characters orthogonal")
    print(f"    [{'✓' if complete3 else '✗'}] Hadamard matrix property holds at H_8")
    print()

    # ============================================================
    # The synthesis
    # ============================================================
    print("=" * 78)
    print("  Synthesis: what the architecture is doing")
    print("=" * 78)
    print("""
  Computation in this architecture is the STRUCTURED MIXING of Walsh–Hadamard
  basis characters over F_2^n. Each operation:

    • Indexes a basis character by its witness axis
      (which character validates this operation)
    • Carries a parity tag (chirality bit = sign of permutation)
    • Sits in a pairing structure (Z_3 generator routes among matchings)
    • Composes under controlled group symmetries (V_4, Z_2, Z_3)

  The codeword width 2n+1 = 1 (chirality) + n (pairing) + n (witness) gives
  exactly the dimensions needed to address the 2^n character basis × the
  parity / pairing structure that makes composition coherent.

  At level n, the architecture realizes:

    computation = symmetry-governed transformation of a Walsh–Hadamard basis

  This is the framing that makes the Cayley–Dickson ladder a structural scaling
  rather than an ad-hoc enlargement: each level extends F_2^n by one bit,
  doubles the basis from 2^n to 2^(n+1), and inherits the parity / symmetry
  structure of the prior level coherently.
""")


if __name__ == "__main__":
    demo()
