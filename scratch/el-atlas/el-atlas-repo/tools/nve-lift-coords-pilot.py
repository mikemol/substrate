"""
nve-lift-coords-pilot.py — the last residue inside the vE answer: the
exact statement in LIFT COORDINATES (formal-quotient pairs).

Statement: vE's JOIN is fraction-add on pairs (it closes to conductance
addition: cl(P (+) Q) = cl(P) + cl(Q)); the SPLIT is a point of the
join's FIBER (the section freedom = the purchased axis); and the
high-impedance BRIDGE READING is a strictly monotone, hence injective —
hence COMPLETE — coordinate on the binary fiber, computed entirely on
quotient values (it factors through cl per case: shadow-level, as S8
check 4 found physically).

1. cl((p1,q1)(+)(p2,q2)) == cl(p1,q1) + cl(p2,q2): the lift of the join.
2. On the fiber over fixed joined G (splits (a, G-a), a in (0,G)): the
   bridge reading r(a) = a/G - ref is strictly increasing and injective
   over a fine grid — one reading + the join determines the binary split.
3. Per-case rescaling invariance: the reading depends on the cases only
   through their quotients (pairs (2a,2) and (a,1) give identical
   readings) — the bridge consumes shadows; the pair holds what it can't.
"""
fadd=lambda P,Q:(P[0]*Q[1]+Q[0]*P[1], P[1]*Q[1]); cl=lambda P:P[0]/P[1]
import random
rng=random.Random(3)
ok1=all(abs(cl(fadd(P,Q))-(cl(P)+cl(Q)))<1e-12 for P,Q in
        (((rng.uniform(.1,9),rng.uniform(.1,9)),(rng.uniform(.1,9),rng.uniform(.1,9))) for _ in range(2000)))
print(f"1. the join lifts: cl(P(+)Q) = cl(P)+cl(Q) (2000 trials): {ok1}")
G, ref = 10.0, 2.0/5.0
rs=[a/G - ref for a in [G*k/400 for k in range(1,400)]]
ok2=all(rs[i]<rs[i+1] for i in range(len(rs)-1)) and len(set(rs))==len(rs)
print(f"2. bridge reading strictly monotone + injective on the join fiber (399-point grid): {ok2} — one reading + the join = the complete binary split")
r=lambda Pa,Pb,ref: cl(Pa)/(cl(Pa)+cl(Pb)) - ref
ok3=abs(r((6.0,2.0),(14.0,2.0),ref) - r((3.0,1.0),(7.0,1.0),ref))<1e-12
print(f"3. per-case rescaling invariance (pairs (6,2),(14,2) vs (3,1),(7,1)): {ok3} — the reading factors through cl per case; shadow-level, as the physical pilot found")
