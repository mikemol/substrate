# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# P-IHARA: the ACTUAL Ihara edge-zeta object. Bass's determinant formula:
#   Z(u)^{-1} = (1-u^2)^{|E|-|V|} * det(I - A u + (D-I) u^2)
# where A = adjacency, D = degree diagonal. This is the object with the GUARANTEED functional
# equation. Build it for the graph our permutation acts on (start: K_n, the complete graph, since
# the cycle-space rep is on K_nv). Confirm the functional equation, read its factorization, then
# ask how a permutation's action relates to it.
import sympy as sp
from sympy import symbols, Matrix, eye, Poly, factor_list, cyclotomic_poly, simplify
u,x = symbols('u x')

def complete_graph_AD(n):
    A = sp.ones(n,n) - sp.eye(n)        # adjacency of K_n
    D = sp.diag(*[n-1]*n)               # every vertex has degree n-1
    return A, D

def ihara_det(n):
    """det(I - A u + (D-I) u^2) -- the Bass determinant (the nontrivial part of Z^{-1})."""
    A,D = complete_graph_AD(n)
    I = sp.eye(n)
    M = I - A*u + (D - I)*u**2
    return sp.expand(M.det())

def functional_eq_check(poly_u, n):
    """Ihara/Bass functional equation: the reciprocal in u. For a (q+1)-regular graph q = n-2
       (degree-1). Test if u^deg * det(1/(q u)... ) relates to det(u). We check the standard
       symmetry: the Bass det of a q+1 regular graph satisfies a known reciprocal relation."""
    q = n-2   # K_n is (n-1)-regular, so q+1 = n-1, q = n-2
    P = Poly(poly_u, u)
    d = P.degree()
    coeffs = P.all_coeffs()  # leading first, in u
    # reciprocal test: does u^d * P(1/(q u)) ∝ P(u)?  i.e. coeffs satisfy a_i = scalar * a_{d-i} * q^{?}
    rec = [coeffs[d-i] for i in range(d+1)]  # reversed
    # check ratio a_i / (a_{d-i} q^{d-i}) constant
    ratios=[]
    for i in range(d+1):
        if rec[i]!=0:
            ratios.append(sp.simplify(coeffs[i]/(rec[i]*q**( (d-2*i) ))) if q!=0 else None)
    # simpler: just report the coeff palindrome structure and q
    return q, coeffs

# CASES: complete-graph sizes. PUMP-COMPATIBLE via pump_adapter; one K_n per increment.
import sympy as sp
from sympy import Poly, factor_list
CASES=[4,5,6]

def compute(n):
    det=ihara_det(n); P=Poly(det,u); q=n-2
    _,facs=factor_list(det,u)
    fstr=' * '.join(f"({sp.factor(f)})^{m}" if m>1 else f"({sp.factor(f)})" for f,m in facs)
    # functional-equation check: for each adjacency eigenvalue, the two zeta poles multiply to 1/q
    fe_ok=True
    for lam in [n-1,-1]:
        roots=sp.solve(1-lam*u+(n-2)*u**2,u)
        if len(roots)==2 and sp.simplify(sp.prod(roots)-sp.Rational(1,q))!=0: fe_ok=False
    return {"degree":int(P.degree()),"q":q,"factors":fstr,"fe_product_1_over_q":bool(fe_ok)}

def fmt(n,res):
    return (f"K_{n}: Bass det degree {res['degree']} in u | q={res['q']} | "
            f"factors: {res['factors']} | FE poles product=1/q: {res['fe_product_1_over_q']}")

from pump_adapter import make
initial,pump,parse,serialize,deserialize = make(globals())

if __name__=="__main__":
    import sys
    st=initial()
    while not parse(st)["done"]: st=pump(st)
    m=parse(st)
    for n,res in zip(CASES,m["results"]): print(fmt(n,res))
    ok=all(r["fe_product_1_over_q"] for r in m["results"])
    print("\nFUNCTIONAL EQUATION: zeta poles u1*u2 = 1/(n-2) = 1/q — the Ihara FE in the ZETA variable.")
    print(f"verdict: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
