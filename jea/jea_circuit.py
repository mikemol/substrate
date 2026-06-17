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


# ---- the simplest carrier: plain exact ℚ (Python Fraction); /0 -> zero (the picircuit policy) ----
class FractionCarrier(Carrier):
    zero = Fraction(0)
    def add(self, a, b): return a + b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b if b != 0 else self.zero


FRACTION = FractionCarrier()


if __name__ == "__main__":
    # WITNESS: the solve is carrier-agnostic -- the SAME code over ℚ (Fraction) and float agrees,
    # and matches the closed forms. (The graded-ℚ wedge carrier lives in jea_onegraph; the device
    # plane carrier in jea_onegraph.fstar_device -- both are further instances of THIS one solve.)
    class FloatCarrier(Carrier):
        zero = 0.0
        def add(self, a, b): return a + b
        def mul(self, a, b): return a * b
        def div(self, a, b): return a / b if b != 0 else 0.0
    F, FL = FRACTION, FloatCarrier()

    w1 = series_schur(F, Fraction(2), Fraction(3)) == Fraction(6, 5)          # 2·3/(2+3)
    w2 = current_divider(F, Fraction(2), [Fraction(3), Fraction(5)]) == Fraction(1, 5)  # 2/(2+3+5)
    w3 = parallel(F, Fraction(2), Fraction(3)) == Fraction(5)
    w4 = fstar(F, Fraction(3), Fraction(2)) == Fraction(2, 5)                 # gg/(gc+gg)=2/5
    # carrier-agnostic: ℚ and float agree (the algorithm doesn't know its carrier)
    w5 = abs(float(series_schur(F, Fraction(2), Fraction(3))) - series_schur(FL, 2.0, 3.0)) < 1e-12
    w6 = series_schur(F, Fraction(1), Fraction(0)) == Fraction(0)             # /0 policy -> zero
    ok = all([w1, w2, w3, w4, w5, w6])
    print(f"jea_circuit (Π2 carrier-parametric solve): w1..w6 = "
          f"{[w1, w2, w3, w4, w5, w6]}")
    print(f"  {'PASS' if ok else 'FAIL'} — ONE series_schur/current_divider/parallel over a pluggable")
    print(f"  carrier (Fraction here; graded-ℚ wedge in jea_onegraph; device planes in fstar_device).")
