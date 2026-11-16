# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-ARITY (the real test): project the k-face rep analogously to the cycle space, then ask which
# prime the PROJECTED ramification supports. The cycle space = ker(∂1) on edges (1-cycles). The
# analogue on k-faces = ker(∂_k): the k-cycles, the k-th homology carrier. Build the permutation
# action ON ker(∂_k) and measure ramification. Edges(k=2 here means 1-faces=edges in our indexing):
#   - 1-faces = edges; ker ∂1 = cycle space (our original object).
#   - 2-faces = triangles; ker ∂2 = the 2-cycles. Act on it, measure which prime ramifies.
# INSTRUMENT: if 3 dominates on 2-faces where 2 dominated on 1-faces -> successor-arity climbs with
# face-dim (arity=successor-availability CONFIRMED). If 2 stays -> cell-dim != successor-arity.
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly, primerange, Rational
from itertools import combinations
x=symbols('x')

def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def vp(n,p):
    n=abs(int(n))
    if n==0: return None
    v=0
    while n%p==0: n//=p; v+=1
    return v

def boundary(nv, k):
    """∂_k : C_k -> C_{k-1}, k-faces to (k-1)-faces, with signs (simplicial boundary)."""
    kf=list(combinations(range(nv),k)); km=list(combinations(range(nv),k-1))
    kidx={f:i for i,f in enumerate(kf)}; kmidx={f:i for i,f in enumerate(km)}
    D=sp.zeros(len(km),len(kf))
    for j,f in enumerate(kf):
        for i in range(k):
            face=f[:i]+f[i+1:]   # drop i-th vertex
            D[kmidx[face], j] += (-1)**i
    return D, kf

def perm_on_faces(perm,nv,k):
    kf=list(combinations(range(nv),k)); fidx={f:i for i,f in enumerate(kf)}
    m=len(kf); P=sp.zeros(m,m)
    sign=[]
    for j,f in enumerate(kf):
        mapped=[perm[v] for v in f]
        sf=tuple(sorted(mapped))
        # simplicial sign of the permutation sorting `mapped`
        s=perm_sign(mapped)
        P[fidx[sf],j]=s
    return P, kf

def perm_sign(seq):
    s=1; a=list(seq)
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            if a[i]>a[j]: s=-s
    return s

def proj_rep_ker(perm,nv,k):
    """Action of the permutation on ker(∂_k) (the k-cycles)."""
    D,kf = boundary(nv,k)
    P,_ = perm_on_faces(perm,nv,k)
    # basis for ker(D)
    ker = D.nullspace()
    if not ker: return None
    K = sp.Matrix.hstack(*ker)   # columns = kernel basis
    # restrict P to ker: solve P*K = K * Trep  => Trep = (K^+ ) P K
    Kp = (K.T*K).inv()*K.T
    Trep = Kp * P * K
    return sp.simplify(Trep)

def ramif(T, primes=tuple(primerange(2,30))):
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    nc=[]; cyc=[]
    for f,m in fl:
        fp=Poly(f,x);kk=None
        for c in range(1,40):
            if Poly(cyclotomic_poly(c,x),x).monic()==fp.monic():kk=c;break
        if kk is None and fp.degree()>=2:
            ld=1
            for cc in fp.all_coeffs(): ld=sp.lcm(ld,sp.denom(sp.nsimplify(cc)))
            Pint=Poly(sp.expand(fp.as_expr()*ld),x)
            try:
                disc=Pint.discriminant(); nc.append((fp.degree(),{p:vp(disc,p) for p in primes if vp(disc,p)}))
            except: nc.append((fp.degree(),"err"))
        elif kk: cyc.append(kk)
    return cyc, nc

nv=6
perm=build([(0,1,2,3),(4,5)],nv)  # (4,2) order 4
print(f"(4,2) order-4 on nv={nv}:")
for k in [1,2,3]:
    T=proj_rep_ker(perm,nv,k)
    if T is None or T.shape[0]==0:
        print(f"  k={k}: ker(∂_{k}) trivial / empty"); continue
    cyc,nc=ramif(T)
    print(f"  ker(∂_{k}) dim {T.shape[0]}: cyclo {sorted(cyc)} | non-cyc ramification: {nc}")
print()
print("k=1: ker(∂1)=cycle space (original, 2 should dominate). k=2: 2-cycles (does 3 take over?).")
