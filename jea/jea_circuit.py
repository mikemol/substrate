#!/usr/bin/env python3
"""jea_circuit.py — Π2: the carrier-parametric circuit-solve (Kron/Schur reduction), ONE definition
over a pluggable arithmetic CARRIER.

jea_onegraph (the live el-atlas-wired supervisor) and jea_picircuit (the metalanguage-as-circuit
instrument) each REIMPLEMENTED series_schur / current_divider / parallel -- the SAME algorithm,
differing only in the carrier (onegraph: the subtraction-free graded-ℚ wedge, exact, charter;
picircuit: plain Fraction). The jea_pysim `--shape` scan flagged exactly this: shared shell +
carrier holes (current_divider <-> current_divider, frac 0.62, holes @depths [1,1,2]). This module
fills that hole the project's way: the carrier is the typed parameter, the algorithm is written once.

The solve is pure {add, mul, div}. A Carrier supplies those; `div` IS the ℚ field quotient = recon's
quotient with remainder 0 (Δ-Ω-divstr: the live ÷ is the Wedge quotient). A subtraction-free carrier
implements `div` as multiply-by-reciprocal (recip = the wedge quotient of 1) -- so the SAME code is
exact-graded-ℚ on the device side and plain-Fraction on the corpus side; the carrier owns the /0 policy.

PERSPECTIVE MAP (Φ1): series_schur/parallel are the SUBTRACTION-FREE closed-form reduction; nodal_solve
(below) is the GOVERNING LAW -- Kirchhoff nodal analysis, general (handles irreducible graphs: a shared
resource, a Wheatstone bridge). They are the SAME conductance-evaluation from two PERSPECTIVES, and the
axis between them is the CARRIER's subtraction-capability: a subtraction-FREE carrier (the graded-ℚ
wedge, jea's charter) runs ONLY the closed form, on series-parallel-reducible graphs; a subtraction-
HAVING carrier (Fraction, float) runs the nodal solve, on ANY graph. el-atlas/tools/kirchhoff_nedge.solve
is the FLOAT instance of nodal_solve -- the Π4 --shape scan correctly MAPPED that correspondence
(G_AND ~ series_schur); the perspective-difference (closed-form vs nodal, "G_AND primitive" vs "nodal
primitive") is just the subtraction axis, mapped -- not a reason to keep them apart. (No cross-project
import: jea carries its OWN nodal_solve, validatable against el-atlas's the way jea_onegraph self-hosts
it -- a homing choice, not a separation. The series-parallel reduction is the sub-free PROJECTION of this
governing law -- the governing-law-before-special-case discipline, with both perspectives now in one module.)
"""
from fractions import Fraction


class Carrier:
    """A circuit-solve carrier: a field, supplying add/mul/div (+ a `zero`). Remainder is 0 (exact ÷).
    Duck-typed -- any object with add(a,b), mul(a,b), div(a,b) and a `zero` attribute works."""
    zero = None
    def add(self, a, b): raise NotImplementedError
    def mul(self, a, b): raise NotImplementedError
    def div(self, a, b): raise NotImplementedError


# ---- the solve: written ONCE, never naming a concrete carrier op ----------------------------
def parallel(C, a, b):
    """Parallel conductances add (KCL at the shared node)."""
    return C.add(a, b)


def series_schur(C, a, b):
    """Schur-eliminate the shared middle node of a 2-edge series path -> a·b/(a+b). THE Kron
    reduction step. Commutative + associative, so it FOLDS a series path by the same combine."""
    return C.div(C.mul(a, b), C.add(a, b))


def current_divider(C, d_self, others):
    """The share of current through d_self at a node it shares with `others`: d_self / (d_self + Σ
    others). The shares of all branches at a node sum to 1 by construction (the denominator IS the
    sum -- KCL). Folded as onegraph did (tot = d_self, then add each other), carrier-agnostic."""
    tot = d_self
    for o in others:
        tot = C.add(tot, o)
    return C.div(d_self, tot)


def fstar(C, gc, gg):
    """f* = gg/(gc+gg): two parallel conductances' current divider -- exactly current_divider(gg, [gc])."""
    return current_divider(C, gg, [gc])


def nodal_solve(C, n, edges, src, sink):
    """The GOVERNING LAW -- Kirchhoff nodal analysis: effective conductance src->sink, carrier-parametric.
    series_schur/parallel are its SUBTRACTION-FREE reducible-graph projections; THIS handles any graph
    (irreducible included -- shared resource, Wheatstone bridge), and so it NEEDS subtraction (the
    Laplacian's negative off-diagonals + Gaussian elimination). A subtraction-FREE carrier (graded-ℚ,
    jea's charter) therefore cannot run it -- which IS the perspective the carrier's subtraction-capability
    selects. The float instance of this is el-atlas/tools/kirchhoff_nedge.solve. edges: (u, v, G)."""
    if not hasattr(C, "sub") or not hasattr(C, "one"):
        raise TypeError("nodal_solve needs a subtraction-capable carrier (with .sub and .one); the "
                        "subtraction-free graded-ℚ carrier has only the closed-form series_schur/parallel "
                        "(its graphs are series-parallel-reducible -- that's why the charter can stay sub-free)")
    z = C.zero
    L = [[z for _ in range(n)] for _ in range(n)]            # Laplacian over the carrier
    for u, v, g in edges:
        L[u][u] = C.add(L[u][u], g); L[v][v] = C.add(L[v][v], g)
        L[u][v] = C.sub(L[u][v], g); L[v][u] = C.sub(L[v][u], g)
    idx = [i for i in range(n) if i != sink]                 # ground `sink`; unit current at `src`
    pos = {node: r for r, node in enumerate(idx)}
    A = [[L[i][j] for j in idx] for i in idx]
    b = [z for _ in idx]; b[pos[src]] = C.one
    m = len(idx)
    for k in range(m):                                       # Gaussian elimination over the carrier
        piv = A[k][k]
        for i in range(k + 1, m):
            f = C.div(A[i][k], piv)
            for j in range(k, m):
                A[i][j] = C.sub(A[i][j], C.mul(f, A[k][j]))
            b[i] = C.sub(b[i], C.mul(f, b[k]))
    x = [z for _ in idx]
    for i in range(m - 1, -1, -1):
        s = b[i]
        for j in range(i + 1, m):
            s = C.sub(s, C.mul(A[i][j], x[j]))
        x[i] = C.div(s, A[i][i])
    return C.div(C.one, x[pos[src]])                         # G_eff = 1 / v[src]


# ---- the simplest carrier: plain exact ℚ (Python Fraction); /0 -> zero (the picircuit policy) ----
class FractionCarrier(Carrier):
    zero = Fraction(0)
    one = Fraction(1)                                        # subtraction-HAVING -> enables nodal_solve
    def add(self, a, b): return a + b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b if b != 0 else self.zero
    def sub(self, a, b): return a - b


FRACTION = FractionCarrier()


if __name__ == "__main__":
    # WITNESS: the solve is carrier-agnostic -- the SAME code over ℚ (Fraction) and float agrees,
    # and matches the closed forms. (The graded-ℚ wedge carrier lives in jea_onegraph; the device
    # plane carrier in jea_onegraph.fstar_device -- both are further instances of THIS one solve.)
    class FloatCarrier(Carrier):
        zero = 0.0
        one = 1.0
        def add(self, a, b): return a + b
        def mul(self, a, b): return a * b
        def div(self, a, b): return a / b if b != 0 else 0.0
        def sub(self, a, b): return a - b
    class SubFreeCarrier(Carrier):                # graded-ℚ-like: NO sub/one -> closed-form only
        zero = Fraction(0)
        def add(self, a, b): return a + b
        def mul(self, a, b): return a * b
        def div(self, a, b): return a / b if b != 0 else self.zero
    F, FL = FRACTION, FloatCarrier()

    w1 = series_schur(F, Fraction(2), Fraction(3)) == Fraction(6, 5)          # 2·3/(2+3)
    w2 = current_divider(F, Fraction(2), [Fraction(3), Fraction(5)]) == Fraction(1, 5)  # 2/(2+3+5)
    w3 = parallel(F, Fraction(2), Fraction(3)) == Fraction(5)
    w4 = fstar(F, Fraction(3), Fraction(2)) == Fraction(2, 5)                 # gg/(gc+gg)=2/5
    w5 = abs(float(series_schur(F, Fraction(2), Fraction(3))) - series_schur(FL, 2.0, 3.0)) < 1e-12
    w6 = series_schur(F, Fraction(1), Fraction(0)) == Fraction(0)             # /0 policy -> zero
    # PERSPECTIVE MAP: the closed form EMERGES from the nodal solve (the governing law), exactly.
    w7 = nodal_solve(F, 3, [(0, 1, Fraction(2)), (1, 2, Fraction(3))], 0, 2) == series_schur(F, Fraction(2), Fraction(3))  # series A-x-B
    w8 = nodal_solve(F, 2, [(0, 1, Fraction(2)), (0, 1, Fraction(3))], 0, 1) == parallel(F, Fraction(2), Fraction(3))      # 2 parallel edges
    w9 = nodal_solve(F, 4, [(0, 1, Fraction(1)), (0, 2, Fraction(1)), (1, 3, Fraction(1)),
                            (2, 3, Fraction(1)), (1, 2, Fraction(1))], 0, 3) == Fraction(1)   # balanced Wheatstone (IRREDUCIBLE) -> 1
    try:                                                                     # sub-free carrier CANNOT run nodal_solve
        nodal_solve(SubFreeCarrier(), 2, [(0, 1, Fraction(2))], 0, 1); w10 = False
    except TypeError:
        w10 = True
    ok = all([w1, w2, w3, w4, w5, w6, w7, w8, w9, w10])
    print(f"jea_circuit (Π2 carrier-parametric solve + Φ1 nodal governing-law): w1..w10 = "
          f"{[w1, w2, w3, w4, w5, w6, w7, w8, w9, w10]}")
    print(f"  {'PASS' if ok else 'FAIL'} — ONE conductance-eval over a pluggable carrier; series_schur/parallel")
    print(f"  = the SUB-FREE closed-form projection (graded-ℚ/Fraction), nodal_solve = the governing law")
    print(f"  (Fraction/float, sub-required; kirchhoff_nedge.solve is its float instance). The carrier's")
    print(f"  subtraction-capability is the perspective axis the --shape map found.")
