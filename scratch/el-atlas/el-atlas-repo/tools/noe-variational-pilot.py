#!/usr/bin/env python3
"""OB-7 variational discharge (S46): mass and bias as MOMENT MAPS.
Chart R^2 (log chart), symplectic form omega = da ^ db.
Convention omega(X_H, .) = dH gives X_H = (dH/db, -dH/da).
All checks exact over integers/rationals; no floats, no sampling."""
from fractions import Fraction as Q

def X(H_a, H_b):  # Hamiltonian vector field components from gradient
    return (H_b, -H_a)

checks=[]
# H = mass = a+b: grad (1,1) -> X = (1,-1) = the SQUEEZE
checks.append(("X_mass is the squeeze (1,-1)", X(1,1)==(1,-1)))
# G = bias = a-b: grad (1,-1) -> X = (-1,-1) = the diagonal translation
checks.append(("X_bias is the diagonal flow (-1,-1)", X(1,-1)==(-1,-1)))
# conservation of each charge along its OWN flow, exact integration (linear flows)
def flow(p, v, t): return (p[0]+t*v[0], p[1]+t*v[1])
mass=lambda p: p[0]+p[1]; bias=lambda p: p[0]-p[1]
ok=True
for a in range(-3,4):
    for b in range(-3,4):
        for t in [Q(-5),Q(-1),Q(1,3),Q(2),Q(7)]:
            if mass(flow((a,b),(1,-1),t))!=mass((a,b)): ok=False
            if bias(flow((a,b),(-1,-1),t))!=bias((a,b)): ok=False
checks.append(("each charge conserved along its own Hamiltonian flow (exact grid x rational times)", ok))
# Poisson bracket {mass,bias} = Ha*Gb - Hb*Ga = (1)(-1)-(1)(1) = -2: conjugate up to scale
checks.append(("{mass,bias} = -2 (canonically conjugate up to scale)", 1*(-1)-1*1==-2))
# crossbar C(a,b)=(a+b,a-b): C*omega = det(J) omega with J=[[1,1],[1,-1]], det=-2
detJ = 1*(-1)-1*1
checks.append(("crossbar is canonical up to the same constant (C*omega = -2 omega)", detJ==-2))
# cross-conservation FAILS as it must (the charges are conjugate, not in involution):
checks.append(("bias NOT conserved along the squeeze (conjugacy, not involution)",
               bias(flow((0,0),(1,-1),Q(1)))!=bias((0,0))))
for name,res in checks:
    print(("PASS " if res else "FAIL ")+name)
assert all(r for _,r in checks)
print("ALL EXACT — OB-7 variational form: mass, bias are the moment maps; the crossbar is a canonical transformation.")
