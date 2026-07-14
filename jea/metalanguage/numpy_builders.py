#!/usr/bin/env python3
"""numpy_builders.py — ⟡H: the array-side of query_builders.py, built as the FOUR-GAUGE semiring `contract`.

The substrate already carries the relational engine: `Substrate.Algebra.Semiring.Instances` builds ONE
`Semiring` in four GAUGES — ℕ (counting, +/·), F₂ (GF(2): XOR/AND field, 1+1=0), Bool (routing: ∨/∧ semiring,
1+1=1), tropical (min/+) — and `Substrate.Algebra.Semiring.Contraction` runs ONE GraphBLAS inner product
`contract(a,b) = ⊕ᵢ aᵢ⊗bᵢ` that PLACES ITSELF via the gauge: Bool = reachability, ℕ = path-count, tropical =
shortest-cost, F₂ = parity (Contraction.agda:46-69). A relational operation is a `contract` at the right gauge;
the numpy realization is the semiring reduction (Bool = any/all, ℕ = sum, tropical = min, F₂ = XOR-parity),
packbits-able to the SWAR word for Bool/F₂.

THE GF(2) → boolean → predicate bridge, with the FIELD-VS-SEMIRING caveat (the whole point of the four-gauge
split): at F₂, ⊕ = XOR and ⊗ = AND (F2.agda:16); a grade-n F₂ object is a Vec F₂ n = a row-MASK; ⊗ = predicate
conjunction (WHERE p AND q), ⊕ = symmetric difference. BUT SQL WHERE/OR/reachability is the **Bool routing
gauge (∨/∧)**, NOT the F₂ field: F₂'s + is XOR, so 1∨1 would wrongly become 0. Reserve F₂ for XOR/parity/crypto.
OR = a⊕b⊕(a∧b) is a derived (three-term) F₂ expression, not primitive.

⟡H1 (this file, first): the four-gauge Semiring + `contract`, reproducing the Contraction.agda placements
byte-exact. ⟡H2/⟡H3 (next): the relational builders mirroring query_builders + the SQL↔numpy hexagon identity
(braiding coherence certified numerically via rig_coherence's blockSwap/factorSwap).
"""
import os, sys, argparse
import numpy as np
try:                                   # the jea host/device seam (jea_zsppf.py:24) — device is optional here
    import cupy as cp                  # noqa: F401
    HAVE_CUPY = True
except Exception:
    HAVE_CUPY = False
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_INF = float("inf")


class Semiring:
    """One `Semiring` (Semiring/Instances.agda), pluggable gauge. `mul` = ⊗ (elementwise); `add_reduce` = the
    ⊕-fold over an axis; `zero`/`one` = the additive/multiplicative units. `contract` reads it GraphBLAS-style."""
    __slots__ = ("name", "mul", "add_reduce", "zero", "one", "add")
    def __init__(self, name, mul, add_reduce, zero, one, add):
        self.name, self.mul, self.add_reduce = name, mul, add_reduce
        self.zero, self.one, self.add = zero, one, add


# ── the four gauges (Semiring/Instances.agda:9-12) ──────────────────────────────────────────────────
def _nat_reduce(x):    return np.add.reduce(x) if x.size else 0
def _bool_reduce(x):   return np.logical_or.reduce(x) if x.size else False
def _trop_reduce(x):   return np.minimum.reduce(x) if x.size else _INF        # min over an empty ⊕ = ∞ (the ⊕-unit)
def _f2_reduce(x):     return int(np.bitwise_xor.reduce(x.astype(np.uint8)) & 1) if x.size else 0

SR_NAT  = Semiring("ℕ",        np.multiply,     _nat_reduce,  0,    1, np.add)              # counting: +/·
SR_BOOL = Semiring("Bool",     np.logical_and,  _bool_reduce, False, True, np.logical_or)   # routing: ∨/∧  (reachability)
SR_TROP = Semiring("tropical", np.add,          _trop_reduce, _INF, 0, np.minimum)          # cost: min/+
SR_F2   = Semiring("F₂",       np.bitwise_and,  _f2_reduce,   0,    1, np.bitwise_xor)       # GF(2): XOR/AND (parity)
GAUGES  = {"nat": SR_NAT, "bool": SR_BOOL, "tropical": SR_TROP, "f2": SR_F2}


def contract(a, b, S):
    """The GraphBLAS inner product ⟨a,b⟩ = ⊕ᵢ (aᵢ ⊗ bᵢ), placed by the gauge S (Contraction.agda:46-49).
    a, b are equal-length 1-D arrays (or array-likes). Returns the scalar in S's carrier."""
    a = np.asarray(a); b = np.asarray(b)
    n = min(a.shape[0], b.shape[0])                    # contract stops at the shorter (Contraction.agda:47-48)
    if n == 0:
        return S.zero
    return S.add_reduce(S.mul(a[:n], b[:n]))


def matmul(A, B, S):
    """Semiring matrix product C[i,j] = ⊕ₖ A[i,k] ⊗ B[k,j], placed by the gauge S. The batched `contract`
    (a JOIN / one boolean-matrix reachability step). Dense O(n³) broadcast — fine for small/verify; the
    packbits SWAR form is ⟡H4."""
    A = np.asarray(A); B = np.asarray(B)
    prod = S.mul(A[:, :, None], B[None, :, :])         # (i,k,j)
    # reduce over k (axis=1) with the gauge's ⊕
    if S is SR_BOOL:   return np.logical_or.reduce(prod, axis=1)
    if S is SR_NAT:    return np.add.reduce(prod, axis=1)
    if S is SR_TROP:   return np.minimum.reduce(prod, axis=1)
    if S is SR_F2:     return np.bitwise_xor.reduce(prod.astype(np.uint8), axis=1) & 1
    raise ValueError(S.name)


# ════════════════ ⟡H-carrier — the carrier-interrelation core (DivStr/recon + EEA-fold + CRT) ═══════
# The deep layer BOTH SQL and numpy realize (witness-tower/CRT/EEA guidance). Every carrier is a DivStr =
# {z, recon(q,b,r)="q·b then r"} (Algebra/Wedge.agda:53-59); ⊗ = the q·b part, ⊕ = the +r part. Two carriers
# INTERRELATE via the EEA trace, folded to many targets (WitnessTower/EEAFoldTable.agda: gcd = common
# structure, Bézout = the recon inverses, CF-digits = the graded residue tower, coprime → CRT split — one
# trace, the fold TARGET picks the extraction). The residue r = the orientation = the CRT correction.

class DivStr:
    """A carrier's wedge interface (Algebra/Wedge.agda:53-59): `z` (terminal divisor) + `recon(q,b,r)` = q·b+r.
    ⊗ is the q·b part, ⊕ is the +r part. A wedge of `a` against `b` is (q, r) with `a == recon(q, b, r)`."""
    __slots__ = ("name", "z", "recon", "wedge")
    def __init__(self, name, z, recon, wedge):
        self.name, self.z, self.recon, self.wedge = name, z, recon, wedge

DIV_NAT = DivStr("ℕ", 0, lambda q, b, r: q * b + r, lambda a, b: divmod(a, b))   # ℕ-div (Algebra/Z/Wedge)
DIV_F2  = DivStr("F₂", 0, lambda q, b, r: (q & b) ^ r, None)                       # F₂-div (⊕=XOR, ⊗=AND)


def eea_steps(a, b):
    """The EEATrace (Nat/GCD/EEATrace.agda): the chain of one-step wedges (a,b)↦(q,r) down to gcd. Returns
    (gcd, [(a_i, b_i, q_i, r_i)] top-down). Each step: a_i = recon(q_i, b_i, r_i) = q_i·b_i + r_i."""
    steps = []
    while b != 0:
        q, r = divmod(a, b)
        assert a == DIV_NAT.recon(q, b, r), "the wedge identity a = recon q b r"
        steps.append((a, b, q, r)); a, b = b, r
    return a, steps                                        # a = gcd (the trace's target index g)

# the universal fold, THREE targets (eea_fold, Nat/GCD/Fold.agda — the target picks the extraction):
def fold_gcd(a, b):     return eea_steps(a, b)[0]          # the common structure
def fold_digits(a, b):  return [q for _, _, q, _ in eea_steps(a, b)[1]]   # CF / Lehmer digits (the residue tower)
def fold_bezout(a, b):
    """Bézout via the back-substitution fold (Z/Bezout.agda:53-59): base (s,t)=(1,0), step (s',t')↦(t', s'−t'·q),
    folded from the gcd base UP. Returns (s, t, g) with s·a + t·b = g."""
    g, steps = eea_steps(a, b)
    s, t = 1, 0
    for (_, _, q, _) in reversed(steps):
        s, t = t, s - t * q
    return s, t, g

def modinv(x, m):
    """x⁻¹ mod m via Bézout (s·x + t·m = 1 ⇒ s ≡ x⁻¹). The CRT inverse (CRT/FromTrace.agda)."""
    s, _, g = fold_bezout(x % m, m)
    assert g == 1, f"{x} not invertible mod {m} (gcd {g})"
    return s % m

def crt_idempotents(moduli):
    """The CRT correction basis eᵢ = Mᵢ·(Mᵢ⁻¹ mod mᵢ), Mᵢ = ∏_{j≠i} mⱼ (CRT/{Inverses,FromIdempotents}.agda):
    eᵢ ≡ 1 mod mᵢ, ≡ 0 mod mⱼ (j≠i). The idempotents ARE the codec legs; coprime ⇒ orthogonal (eᵢ·eⱼ ≡ 0)."""
    M = 1
    for m in moduli: M *= m
    return [(M // m) * modinv((M // m) % m, m) for m in moduli], M

def crt_combine(residues, moduli):
    """The Bézout-mediated CRT splitter (CRT.agda): combine(a₁,…) = Σ aᵢ·eᵢ — recompose a value from its
    residues across coprime moduli. Reconstruction = a sum of wedge recons (each aᵢ·eᵢ is recon(aᵢ, eᵢ, 0))."""
    es, _ = crt_idempotents(moduli)
    return sum(a * e for a, e in zip(residues, es))


def carrier_selftest():
    # reproduce EEAFoldTable.agda BYTE-EXACT on the trace of (3,2): ONE trace, four fold targets.
    assert fold_gcd(3, 2) == 1, "gcd(3,2) = 1 (the trace's target index — coprime)"
    assert fold_digits(3, 2) == [1, 2], "CF/Lehmer digits of 3/2 = [1,2] (the quotient sequence consed by the fold)"
    s, t, g = fold_bezout(3, 2)
    assert (s * 3 + t * 2 == g == 1) and (s, t) == (1, -1), f"Bézout: 1·3 + (−1)·2 = 1, got s={s},t={t},g={g}"
    # the residue r IS the wedge remainder (a = recon q b r): 3 = recon(1, 2, 1) = 1·2 + 1.
    assert DIV_NAT.recon(1, 2, 1) == 3, "a = recon q b r (the orientation residue r=1)"

    # CRT ℤ/15 ≅ ℤ/3 × ℤ/5 — reproduce CRT/Examples.agda byte-exact.
    es, M = crt_idempotents([3, 5])
    assert M == 15 and es == [10, 6], f"idempotents e₁=10 (≡1 mod3,≡0 mod5), e₂=6, got {es}"
    assert crt_combine([1, 2], [3, 5]) == 22, "combine(1,2) = 1·10 + 2·6 = 22 ≡ (1 mod 3, 2 mod 5)"
    assert 22 % 3 == 1 and 22 % 5 == 2, "the reconstruction hits both residues"
    # COPRIME ⇒ ORTHOGONAL: the cross-term e₁·e₂ ≡ 0 mod 15 (CenterIsStarCRT: ⊗ degenerates to ⊕, clean split).
    assert (es[0] * es[1]) % 15 == 0, "coprime ⇒ e₁·e₂ ≡ 0 (orthogonal, cross-term vanishes)"
    # SHARED FACTOR ⇒ a GRADED RESIDUE (CenterIsStarNumeral: ℤ/8, 2·2=4 nilpotent — carried, not rejected).
    assert (2 * 2) % 8 == 4 and (4 * 2) % 8 == 0, "shared prime-2: 2 nilpotent in ℤ/8 (a graded residue, the cost)"
    print("PASS ⟡H-carrier (DivStr/recon + EEA-fold + CRT):")
    print("  ONE EEA trace of (3,2), four fold targets (EEAFoldTable): gcd=1, CF-digits=[1,2], Bézout 1·3−1·2=1,")
    print("  residue r=1 = recon(1,2,1). CRT ℤ/15≅ℤ/3×ℤ/5: e=[10,6], combine(1,2)=22; coprime ⇒ e₁·e₂≡0")
    print("  (orthogonal, ⊗→⊕); shared prime ⇒ graded residue (2 nilpotent in ℤ/8) — the grade CARRIES it.")


# ════════════════════════════════ ⟡H1 selftest — the four placements, byte-exact ════════════════════
def selftest():
    # reproduce Contraction.agda:55-69 exactly (one tensor, four gauges — instances, not builds).
    assert contract([1, 2], [3, 4], SR_NAT) == 11, "ℕ count: 1·3 + 2·4 = 11"
    assert bool(contract([True, False], [True, True], SR_BOOL)) is True, "Bool route: (⊤∧⊤)∨(⊥∧⊤) = ⊤"
    assert contract([1, 2], [3, 4], SR_TROP) == 4, "tropical: min(1+3, 2+4) = 4"
    assert contract([1, 1], [1, 1], SR_F2) == 0, "F₂ parity: (𝟙∧𝟙)⊕(𝟙∧𝟙) = 𝟙⊕𝟙 = 𝟘"
    # the field-vs-semiring caveat, made executable: SAME 2-element inputs, DIFFERENT addition ⇒ different answer.
    #   Bool routes: 1∨1 = 1 (reachability accumulates);  F₂ parity: 1⊕1 = 0 (XOR cancels).
    assert bool(contract([True, True], [True, True], SR_BOOL)) is True, "Bool: two live channels ⇒ ⊤"
    assert contract([1, 1], [1, 1], SR_F2) == 0, "F₂: two ⇒ parity 0 — NOT the Bool answer (the trap the split prevents)"
    # a Bool reachability STEP as a matmul (frontier · adjacency): {0}·(0→1) reaches {0,1}? one step 0→1.
    adj = np.array([[False, True, False], [False, False, True], [False, False, False]])  # 0→1→2 chain
    front = np.array([[True, False, False]])                                             # frontier = {0}
    step = matmul(front, adj, SR_BOOL)                                                   # one hop
    assert step.tolist() == [[False, True, False]], "Bool matmul = one reachability hop 0→1"
    print("PASS ⟡H1 numpy four-gauge semiring `contract`:")
    print("  ONE contract, four gauges (Contraction.agda:55-69): ℕ=11, Bool=⊤, tropical=4, F₂=𝟘 — byte-exact.")
    print("  the field-vs-semiring caveat executable: Bool 1∨1=1 (reachability) ≠ F₂ 1⊕1=0 (parity);")
    print("  Bool matmul = one reachability hop. numpy" + (" + cupy" if HAVE_CUPY else " (host; cupy absent)") + ".")
    print()
    carrier_selftest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest(); return
    ap.print_help()


if __name__ == "__main__":
    main()
