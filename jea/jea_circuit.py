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

PERSPECTIVE MAP (Φ1, corrected Φ1′): series_schur/parallel/nodal_solve are ONE conductance-evaluation
seen from different COORDINATES, NOT different capabilities. nodal_solve (Gaussian elimination over the
Laplacian) is the SUBTRACTIVE coordinate -- it needs a subtraction-having carrier (the Laplacian's
negative off-diagonals + elimination subtract). But the subtraction is an ARTIFACT of that coordinate,
NOT of the governing law: by the Matrix-Tree theorem the effective conductance is a RATIO of two POSITIVE
sums-of-products of edge conductances -- the spanning-tree polynomial over the spanning-2-forest
polynomial -- entirely SUBTRACTION-FREE. nodal_solve_subfree (below) computes exactly that, so the
subtraction-FREE graded-ℚ wedge (jea's charter carrier) DOES solve ANY graph, irreducible ones (a shared
resource, a Wheatstone bridge) included. The float realization is the log/division/exp route: take logs
at intern so products become sums and the final ratio becomes a subtraction-of-logs = DIVISION, exp on
readout -- the exp⊣log retraction (substrate's, a step-inverse bisimulation; for EXACT ℚ no log is needed,
the ratio is exact). So the carrier's subtraction-capability selects which COORDINATE you run (subtractive
Gaussian vs subtraction-free Matrix-Tree), NOT which graphs you can solve.

(CORRECTION: an earlier rung of this module froze "sub-free carrier ⟹ cannot solve irreducible graphs"
and raised TypeError to enforce it -- a collapsed scalar COORDINATE mistaken for the GEOMETRY. The
governing law is coordinate-free; subtraction was only the Gaussian chart. The premature wall is removed.)

el-atlas/tools/kirchhoff_nedge.solve is the float instance of the SUBTRACTIVE coordinate; series_schur/
parallel are the closed-form projection for series-parallel-reducible graphs. The Π4 --shape scan
correctly MAPPED the correspondence (G_AND ~ series_schur). No cross-project import: jea carries its OWN
solves, validatable against el-atlas's the way jea_onegraph self-hosts it -- a homing choice.
"""
from fractions import Fraction
from itertools import combinations


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
    """The SUBTRACTIVE coordinate of the governing law -- Kirchhoff nodal analysis by Gaussian elimination
    over the Laplacian: effective conductance src->sink, carrier-parametric. Needs a subtraction-having
    carrier (the Laplacian's negative off-diagonals + elimination subtract). This is ONE coordinate;
    nodal_solve_subfree (below) is the subtraction-FREE coordinate computing the SAME G_eff (Matrix-Tree
    ratio) -- so a sub-free carrier is NOT barred from irreducible graphs. series_schur/parallel are the
    closed form for reducible graphs. el-atlas/tools/kirchhoff_nedge.solve is this coordinate's float
    instance. edges: (u, v, G)."""
    if not hasattr(C, "sub") or not hasattr(C, "one"):
        raise TypeError("nodal_solve is the SUBTRACTIVE coordinate (Gaussian elimination needs .sub); a "
                        "subtraction-free carrier runs the SAME law via nodal_solve_subfree (the "
                        "Matrix-Tree ratio) -- it is NOT barred from any graph, this is just a coordinate")
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


def nodal_solve_subfree(C, n, edges, src, sink):
    """The SUBTRACTION-FREE coordinate of the SAME governing law -- so the graded-ℚ wedge (jea's charter
    carrier, sub-free) solves ANY graph, irreducible ones (shared resource, Wheatstone bridge) included.
    The subtraction in nodal_solve (Laplacian negatives + Gaussian elimination) is an ALGORITHM coordinate,
    NOT intrinsic to the law: by the Matrix-Tree theorem the effective conductance is a RATIO of two
    POSITIVE sums-of-products of edge conductances --
        T    = Σ over spanning TREES      ∏ edge-conductance   (the whole graph)
        F_st = Σ over spanning 2-FORESTS  ∏ edge-conductance   (src, sink in DIFFERENT trees)
    and G_eff = T / F_st. Only add (the Σ), mul (the ∏) and ONE final div (the ratio) touch the carrier --
    no .sub. Needs only a multiplicative identity (.one), which a sub-free semiring has. (Float realization
    of the user's route: take logs at intern so each ∏ becomes a Σ and the final ratio becomes a
    subtraction-of-logs = DIVISION, exp on readout -- the exp⊣log retraction; for exact ℚ no log is needed.)
    An acyclic size-k edge set on n nodes is always an (n-k)-forest, so summing ∏g over acyclic size-(n-1)
    subsets = the spanning-tree polynomial, and over src/sink-separating acyclic size-(n-2) subsets = F_st.
    Enumeration is the exact subtraction-free WITNESS (combinatorial, fine for the device's small Kron
    blocks); an efficient monotone evaluator is a separate concern, not claimed here. edges: (u, v, G)."""
    one = getattr(C, "one", None)
    if one is None:
        raise TypeError("nodal_solve_subfree needs a multiplicative identity (.one); it does NOT need "
                        ".sub -- that is the whole point (the subtraction-free coordinate of the law)")
    z = C.zero

    def _root(parent, x):
        while parent[x] != x:
            x = parent[x]
        return x

    def _forest_poly(k, separate):
        total = z
        for combo in combinations(edges, k):
            parent = list(range(n)); acyclic = True
            for (u, v, _g) in combo:
                ru, rv = _root(parent, u), _root(parent, v)
                if ru == rv:                                 # a cycle -> not a forest
                    acyclic = False; break
                parent[ru] = rv
            if not acyclic:
                continue
            if separate and _root(parent, src) == _root(parent, sink):
                continue                                     # src,sink must land in different trees
            prod = one
            for (_u, _v, g) in combo:
                prod = C.mul(prod, g)
            total = C.add(total, prod)
        return total

    T = _forest_poly(n - 1, separate=False)                  # spanning trees       (Matrix-Tree numerator)
    F_st = _forest_poly(n - 2, separate=True)                # spanning 2-forests    (separating denominator)
    return C.div(T, F_st)                                    # G_eff = T / F_st -- positive/positive, no sub


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
    class SubFreeCarrier(Carrier):                # graded-ℚ-like: NO .sub (only .one -> the unit, not subtraction)
        zero = Fraction(0)
        one = Fraction(1)                         # multiplicative identity -- a sub-free semiring has it; NOT subtraction
        def add(self, a, b): return a + b
        def mul(self, a, b): return a * b
        def div(self, a, b): return a / b if b != 0 else self.zero
    F, FL, SF = FRACTION, FloatCarrier(), SubFreeCarrier()

    series = [(0, 1, Fraction(2)), (1, 2, Fraction(3))]                      # A-x-B (series-parallel-reducible)
    twopar = [(0, 1, Fraction(2)), (0, 1, Fraction(3))]                      # two parallel edges
    wheat  = [(0, 1, Fraction(1)), (0, 2, Fraction(1)), (1, 3, Fraction(1)),  # balanced Wheatstone bridge --
              (2, 3, Fraction(1)), (1, 2, Fraction(1))]                       #   IRREDUCIBLE (not series-parallel)

    w1 = series_schur(F, Fraction(2), Fraction(3)) == Fraction(6, 5)          # 2·3/(2+3)
    w2 = current_divider(F, Fraction(2), [Fraction(3), Fraction(5)]) == Fraction(1, 5)  # 2/(2+3+5)
    w3 = parallel(F, Fraction(2), Fraction(3)) == Fraction(5)
    w4 = fstar(F, Fraction(3), Fraction(2)) == Fraction(2, 5)                 # gg/(gc+gg)=2/5
    w5 = abs(float(series_schur(F, Fraction(2), Fraction(3))) - series_schur(FL, 2.0, 3.0)) < 1e-12
    w6 = series_schur(F, Fraction(1), Fraction(0)) == Fraction(0)             # /0 policy -> zero
    # SUBTRACTIVE coordinate (Gaussian): the closed form EMERGES from the nodal solve, exactly.
    w7 = nodal_solve(F, 3, series, 0, 2) == series_schur(F, Fraction(2), Fraction(3))
    w8 = nodal_solve(F, 2, twopar, 0, 1) == parallel(F, Fraction(2), Fraction(3))
    w9 = nodal_solve(F, 4, wheat, 0, 3) == Fraction(1)                        # irreducible -> resolves to 1
    # COORDINATE distinction is real: nodal_solve (Gaussian) genuinely needs .sub --
    try:
        nodal_solve(SF, 2, twopar, 0, 1); w10 = False
    except TypeError:
        w10 = True
    # ...but the GRAPH/capability wall is DISSOLVED: the sub-free carrier solves the SAME graphs via the
    # subtraction-free Matrix-Tree coordinate -- IRREDUCIBLE Wheatstone included, exactly.
    w11 = nodal_solve_subfree(SF, 4, wheat, 0, 3) == Fraction(1)             # sub-free SOLVES the irreducible graph
    w12 = nodal_solve_subfree(F, 3, series, 0, 2) == series_schur(F, Fraction(2), Fraction(3))   # == 6/5
    w13 = nodal_solve_subfree(F, 4, wheat, 0, 3) == nodal_solve(F, 4, wheat, 0, 3)   # both coordinates AGREE
    w14 = nodal_solve_subfree(SF, 2, twopar, 0, 1) == parallel(F, Fraction(2), Fraction(3))      # parallel, sub-free
    ws = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14]
    ok = all(ws)
    print(f"jea_circuit (Π2 carrier-parametric solve + Φ1′ Matrix-Tree subtraction-free coordinate): w1..w14 = {ws}")
    print(f"  {'PASS' if ok else 'FAIL'} — ONE conductance-eval, TWO coordinates of the SAME governing law:")
    print(f"  nodal_solve = SUBTRACTIVE (Gaussian, needs .sub; kirchhoff_nedge.solve is its float instance),")
    print(f"  nodal_solve_subfree = SUBTRACTION-FREE (Matrix-Tree ratio T/F_st; the graded-ℚ wedge runs it).")
    print(f"  The carrier's subtraction-capability selects the COORDINATE, NOT which graphs are solvable —")
    print(f"  the sub-free wedge solves the IRREDUCIBLE Wheatstone too (w11/w13). The earlier wall was false.")
