"""
radzdg-witness-pilot.py — T2 discharge: {RAD, ZDG} witness-structure
separation. The pair is unseparated IN TRUTH across three spaces (the
Hurwitz <-> no-ZD co-movement is a theorem); the standing frontier asked
whether their WITNESS STRUCTURES differ. They do, by exhibit:

1. ZDG witness at dim 16: a zero-divisor pair (xy = 0, x,y != 0) — found
   by brute force over signed two-term basis combinations. Every ZD pair
   is automatically a norm-failure witness (N(xy) = 0 < N(x)N(y)).
2. RAD witness at dim 16 that is NOT a ZD: a pair with
   N(xy) != N(x)N(y) and xy != 0 — norm multiplicativity fails without
   zero division.
3. Sanity: at dim 8 (octonions) the norm IS multiplicative (Hurwitz).

VERDICT (strata-indexed): {RAD, ZDG} unseparated-in-truth-in-S,
SEPARATED AT THE WITNESS STRATUM — ZD witnesses are a STRICT subset of
norm-failure witnesses. The co-movement is real; the claims are not
witness-aliases.
"""
import random
rng = random.Random(5)

from cd_arith import conj, vadd, vsub, cdmul, norm as N   # Π9: shared CD doubling generator
def e(i,n=16):
    v=[0.0]*n; v[i]=1.0; return tuple(v)

zd=None
for i in range(1,16):
    for j in range(i+1,16):
        if zd: break
        for k in range(1,16):
            for l in range(k+1,16):
                for s in (1,-1):
                    x=vadd(e(i),tuple(s*t for t in e(j))); y=vadd(e(k),tuple(-t for t in e(l)))
                    if N(cdmul(x,y))<1e-18: zd=(i,j,s,k,l,-1); break
                if zd: break
            if zd: break
    if zd: break
i,j,s,k,l,t=zd
x=vadd(e(i),tuple(s*u for u in e(j))); y=vadd(e(k),tuple(t*u for u in e(l)))
print(f"1. ZD witness (dim 16): (e{i} {'+' if s>0 else '-'} e{j})(e{k} {'+' if t>0 else '-'} e{l}) = 0 exactly: {N(cdmul(x,y))==0.0}; N(x)N(y) = {N(x)*N(y):.0f} > 0 (so also a norm-failure witness)")

found=None
for _ in range(50):
    u=tuple(rng.gauss(0,1) for _ in range(16)); v=tuple(rng.gauss(0,1) for _ in range(16))
    p=cdmul(u,v); dev=abs(N(p)-N(u)*N(v))/(N(u)*N(v))
    if dev>1e-3 and N(p)>1e-6: found=(dev,N(p)); break
print(f"2. RAD witness that is NOT a ZD: N(xy)/N(x)N(y) deviates by {found[0]*100:.1f}% with N(xy) = {found[1]:.3f} != 0 — norm failure WITHOUT zero division")

ok8=all(abs(N(cdmul(u,v))-N(u)*N(v))<1e-9*N(u)*N(v) for u,v in
        (((tuple(rng.gauss(0,1) for _ in range(8))),(tuple(rng.gauss(0,1) for _ in range(8)))) for _ in range(200)))
print(f"3. octonion sanity (Hurwitz, 200 random pairs): norm multiplicative: {ok8}")
print("VERDICT: witness sets — ZD ⊊ norm-failure at dim 16. {RAD,ZDG}: unseparated-in-truth, SEPARATED-at-witness-stratum.")
