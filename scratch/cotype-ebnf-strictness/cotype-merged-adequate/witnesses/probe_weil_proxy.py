# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-WEIL: do the cycle-space Frobenius eigenvalues satisfy a FUNCTIONAL EQUATION λ ↦ c/λ
# (Ihara s↔1−s / graph-Weil)? Test the non-cyclotomic factors: a polynomial f(x) is
# "functional-equation symmetric" iff its roots pair under λ ↦ c/λ, i.e. f is (up to scale)
# PALINDROMIC/anti-palindromic in a generalized sense: x^d f(c/x) ∝ f(x) for some c.
# We test: does there exist c with x^deg * f(c/x) == (scalar) * f(x)? If yes, roots pair λ,c/λ.
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, Rational, simplify, nsimplify
x,c=symbols('x c')

def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def factors(perm,nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    out=[]
    for f,m in fl:
        fp=Poly(f,x);k=None
        for kk in range(1,40):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic():k=kk;break
        out.append((fp.degree(), m, ("Φ%d"%k if k else "NC"), fp))
    return out

def functional_eq_c(fp):
    """Find c such that x^d f(c/x) = scalar * f(x). Returns c if a consistent constant exists, else None.
       Reciprocal-symmetric: coeffs a_0..a_d satisfy a_i * c^? = scalar * a_{d-i}."""
    coeffs=fp.all_coeffs()  # a_d, a_{d-1}, ..., a_0  (leading first)
    d=fp.degree()
    coeffs=coeffs[::-1]      # now a_0 .. a_d
    # x^d f(c/x) = sum a_i c^i x^{d-i}. Coeff of x^j is a_{d-j} c^{d-j}. Want = s * a_j.
    # so a_{d-j} c^{d-j} = s a_j for all j. Take j=d (x^0... careful): use ratio.
    # For palindromic-with-c: a_{d-j} c^{d-j} / a_j = const s for all j with a_j!=0.
    s_vals=[]
    cc=sp.symbols('cc', positive=False)
    # solve from two equations (j=0 and j=1 if available), then verify all
    # a_d c^d = s a_0 ; a_{d-1} c^{d-1} = s a_1
    # divide: (a_d/a_{d-1}) c = (a_0/a_1)  => c = (a_0/a_1)*(a_{d-1}/a_d)
    try:
        if d>=1 and coeffs[1]!=0 and coeffs[d]!=0:
            cval = (coeffs[0]/coeffs[1])*(coeffs[d-1]/coeffs[d])
            cval = sp.nsimplify(sp.simplify(cval))
            # verify ALL j
            # scalar s from j=0: a_d c^d = s a_0
            sscal = sp.simplify(coeffs[d]*cval**d/coeffs[0])
            ok=True
            for j in range(d+1):
                lhs=sp.simplify(coeffs[d-j]*cval**(d-j))
                rhs=sp.simplify(sscal*coeffs[j])
                if sp.simplify(lhs-rhs)!=0: ok=False;break
            return (cval if ok else None)
    except Exception as e:
        return None
    return None

nv=10
for name,cycles in [("(2,3)",[(0,1),(2,3,4)]),("(4,3)",None),("lone 5",[(5,6,7,8,9)]),
                    ("(2,3,5)",[(0,1),(2,3,4),(5,6,7,8,9)])]:
    if name=="(4,3)":
        nv2=7; perm=build([(0,1,2,3),(4,5,6)],nv2); facs=factors(perm,nv2)
    else:
        perm=build(cycles,nv); facs=factors(perm,nv)
    print(f"{name}:")
    for deg,m,tag,fp in facs:
        if tag=="NC" and deg>=2:
            cval=functional_eq_c(fp)
            if cval is not None:
                print(f"    NC deg-{deg}: FUNCTIONAL EQ holds, λ↦{cval}/λ  (roots pair! graph-Weil)")
            else:
                print(f"    NC deg-{deg}: no λ↦c/λ symmetry found")
    print()
