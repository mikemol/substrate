"""
ngl-lift-pilot.py — the N2 pilot grounding the lift theorem's [W] grade
(spec §5.7e identification 3; nedge-decomposition.md §6; cotype N2).

Verifies, over 2000 random formal-quotient pairs (seed 42), that the entire
Nedge G-Value Calculus is <fraction-addition, swap> on pairs (n, d) with
class n/d:
  1. G_OR  = class of fraction addition
  2. G_AND = class of swap-conjugated fraction addition
  3. G_NOT = class of the swap
  4. non-idempotence = the mass-growth shadow ((n,d)+(n,d) = (2nd, d^2) ~ 2n/d)
  5. G_res = residuation of harmonic AND = resistance DIFFERENCE
     (1/X = 1/G(Q) - 1/G(P)), adjointness exact at the sup
  6. G(Q|P) = L1-normalization of the pair (G(P), G(Q))
  7. DeMorgan exactness = the swap distributing
The harness claim NGL (el-atlas-depsort-v3.py, v3.4) re-encodes identities
1-6 at 200 trials inside the instrument; this file is the original
free-standing witness. Run output: tools/ngl-lift-pilot-out.txt.
"""
import random
random.seed(42)
G_OR  = lambda a,b: a+b
G_AND = lambda a,b: a*b/(a+b)
G_NOT = lambda a: 1/a

f_add  = lambda p,q: (p[0]*q[1]+q[0]*p[1], p[1]*q[1])
f_swap = lambda p: (p[1],p[0])
cls    = lambda p: p[0]/p[1]

ok_or=ok_and=ok_not=ok_ni=ok_res=ok_cond=True
for _ in range(2000):
    p=(random.uniform(.1,10), random.uniform(.1,10))
    q=(random.uniform(.1,10), random.uniform(.1,10))
    a,b=cls(p),cls(q)
    ok_or  &= abs(G_OR(a,b)  - cls(f_add(p,q))) < 1e-9
    ok_and &= abs(G_AND(a,b) - cls(f_swap(f_add(f_swap(p),f_swap(q))))) < 1e-9
    ok_not &= abs(G_NOT(a)   - cls(f_swap(p))) < 1e-9
    ok_ni  &= abs(cls(f_add(p,p)) - 2*a) < 1e-9 and abs(cls(f_swap(f_add(f_swap(p),f_swap(p)))) - a/2) < 1e-9
    if a > b:
        X = a*b/(a-b)
        ok_res &= abs(G_AND(a,X) - b) < 1e-9          # exactness at the sup
        ok_res &= G_AND(a, X*1.001) > b               # above it, exceeds
        ok_res &= abs(1/X - (1/b - 1/a)) < 1e-9       # resistance-difference form
    ok_cond &= abs(G_AND(a,b)/a - b/(a+b)) < 1e-9

dm = all(abs(G_NOT(G_AND(a,b)) - G_OR(G_NOT(a),G_NOT(b))) < 1e-9
         for a,b in [(random.uniform(.1,10),random.uniform(.1,10)) for _ in range(500)])
print(f"LIFT PILOT: OR=fraction-add {ok_or}; AND=swap-conj-add {ok_and}; NOT=swap {ok_not}")
print(f"            non-idempotence=mass-shadow {ok_ni}; res=resistance-difference {ok_res}; cond=L1-normalization {ok_cond}; DeMorgan-via-swap {dm}")
