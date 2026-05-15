"""
chirality_as_parity_clean.py — chirality is sign(π) where π is the S_4
permutation [source, sink, witness, fourth].

The connection to Hamming/parity codes:
  - S_4 has a natural Z_2 quotient: S_4 / A_4 = {even, odd}
  - This Z_2 IS the parity bit of any Hamming-style encoding of S_4
  - Direction reversal (inverse) is a transposition (s ↔ t)
  - A transposition is an odd permutation → it flips the sign
  - Therefore: inverse(op) has chirality flipped from op
"""

from itertools import permutations

AXES = ['D', 'C', 'S', 'W']
AXIS_INDEX = {a: i for i, a in enumerate(AXES)}

PAIRINGS = {
    'α': ({'D', 'C'}, {'S', 'W'}),
    'β': ({'D', 'S'}, {'C', 'W'}),
    'γ': ({'D', 'W'}, {'C', 'S'}),
}


def opposite_pair_for(source, sink):
    s_set = frozenset({source, sink})
    for name, (p1, p2) in PAIRINGS.items():
        if frozenset(p1) == s_set:
            return frozenset(p2), name
        if frozenset(p2) == s_set:
            return frozenset(p1), name


def sign(perm):
    """Sign of permutation as a list of indices. Returns 0 (even) or 1 (odd)."""
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2


def perm_of(source, sink, witness):
    """The full S_4 permutation determined by (source, sink, witness)."""
    fourth = (set(AXES) - {source, sink, witness}).pop()
    return [AXIS_INDEX[a] for a in [source, sink, witness, fourth]]


def chirality(source, sink, witness):
    return 'even' if sign(perm_of(source, sink, witness)) == 0 else 'odd'


def main():
    print("=" * 78)
    print("  Chirality = sign(π) where π ∈ S_4 is determined by (source, sink, witness)")
    print("=" * 78)
    print()
    print("  Each directed witnessed op (s, t, w) determines a permutation π = [s, t, w, x]")
    print("  where x is the unique 'fourth axis' not in {s, t, w}.")
    print()
    print("  The chirality bit IS sign(π) ∈ Z_2 = S_4 / A_4.")
    print()

    # Enumerate all 24 ops and verify
    ops = []
    for source in AXES:
        for sink in AXES:
            if source == sink:
                continue
            opp_pair, pairing = opposite_pair_for(source, sink)
            for witness in sorted(opp_pair):
                π = perm_of(source, sink, witness)
                ops.append({
                    'source': source, 'sink': sink, 'witness': witness,
                    'pairing': pairing,
                    'perm': π,
                    'sign': sign(π),
                    'chirality': chirality(source, sink, witness),
                })

    # Show all 24 with their permutations
    print(f"  {'op':<14} {'permutation π':<20} {'sign(π)':<8} {'chirality':<10}")
    print(f"  {'-'*14} {'-'*20} {'-'*8} {'-'*10}")
    for op in sorted(ops, key=lambda o: (o['pairing'], o['sign'], o['source'], o['sink'])):
        op_str = f"{op['source']}→{op['sink']} w/ {op['witness']}"
        perm_str = str(op['perm'])
        print(f"  {op_str:<14} {perm_str:<20} {op['sign']:<8} {op['chirality']:<10}")

    # =====================
    # Inverse pairs: verify that inverse flips sign
    # =====================
    print()
    print("=" * 78)
    print("  Inverse = swap(source, sink). Since swap is a transposition (odd perm),")
    print("  sign(inverse(op)) = sign(op) * sign(transposition) = sign(op) * (-1)")
    print("=" * 78)
    print()

    op_lookup = {(o['source'], o['sink'], o['witness']): o for o in ops}

    all_pass = True
    inverse_pairs_seen = set()
    print(f"  {'forward':<14} {'sign':<6} {'inverse':<14} {'sign':<6}  {'flipped?':<10}")
    print(f"  {'-'*14} {'-'*6} {'-'*14} {'-'*6} {'-'*10}")
    for op in ops:
        s, t, w = op['source'], op['sink'], op['witness']
        inv_key = (t, s, w)
        if inv_key in inverse_pairs_seen or (s, t, w) in inverse_pairs_seen:
            continue
        inverse_pairs_seen.add((s, t, w))
        inv = op_lookup[inv_key]
        flipped = (op['sign'] != inv['sign'])
        if not flipped:
            all_pass = False
        marker = '✓ chirality flipped' if flipped else '✗ NOT FLIPPED'
        print(f"  {s}→{t} w/ {w:<5} {op['sign']:<6} {t}→{s} w/ {w:<5} {inv['sign']:<6} {marker}")

    print()
    print(f"  Inverse pairs that flip chirality: {'ALL 12' if all_pass else 'NOT ALL'}")
    print(f"  Verdict: {'✓ inverse ≡ chirality flip ≡ parity bit flip' if all_pass else '✗ FAIL'}")

    # =====================
    # The chirality classes
    # =====================
    print()
    print("=" * 78)
    print("  The two chirality classes are the cosets of A_4 ⊂ S_4")
    print("=" * 78)
    print()
    even = [o for o in ops if o['sign'] == 0]
    odd = [o for o in ops if o['sign'] == 1]
    print(f"  Even chirality (in A_4): {len(even)} ops — the 'positive' tetrahedron orientation")
    print(f"  Odd chirality (in S_4 \\ A_4): {len(odd)} ops — the 'mirror' orientation")
    print()
    print(f"  A_4 is the rotation group of the tetrahedron (|A_4| = 12).")
    print(f"  S_4 \\ A_4 is its mirror image (also 12 elements).")
    print(f"  Together they form S_4 = full symmetry group of the tetrahedron.")
    print()

    # =====================
    # Connection to Hamming/RM at axis level
    # =====================
    print("=" * 78)
    print("  Connection to the Hamming/RM structure already present in the cotype")
    print("=" * 78)
    print("""
  At the AXIS level (cotype M22):
      The 4 axes (D, C, S, W) carry Walsh-Hadamard readings — projections
      onto the 16 characters of F_2^4. The WHT-basis row containing the
      all-ones vector (the "DC component") is the parity-zero check on any
      operation's incidence vector.

  At the OPERATIONS level (here, M34):
      The 24 directed witnessed ops correspond to S_4 permutations.
      The S_4 / A_4 quotient is the chirality bit. This is the EXACT
      analog of the WHT parity bit at the axis level — applied to the
      operation's permutation rather than to its axis-engagement vector.

  Both bits answer the same kind of question:
      "Is this object on the 'positive' side or the 'mirror' side of its
       natural Z_2 quotient?"

  At axis level: even-weight incidence vs odd-weight incidence
  At operations level: even permutation (A_4) vs odd permutation (S_4 \\ A_4)

  This is structural convergence — the same parity bit appears at two
  different scales of the architecture. It's not a coincidence; it's the
  hierarchical RM/Hamming structure carrying through.

  Direction reversal = (s, t) transposition = flip parity at this level.
  Just like Hamming code complement = XOR with parity-check generator.

  The store/load 'asymmetry' from M33 was always going to be there. It's
  the parity bit doing its job: distinguishing op from inverse(op).
""")


if __name__ == "__main__":
    main()
