"""
hyperplane-ride-pilot.py — S23: ride breaker structure instead of sampling.

A. THE INSTRUMENT'S OWN RIDE (dep-projection separator counting): every
   claim verdict factors through its declared knob support (_CLAIM_DEPS —
   audited clean, tools/dep-audit.py). Therefore the separator count for a
   pair {X,Y} is EXACTLY (count on the joint dep-projection) x (volume of
   the complementary cylinder). Verified against full 165,888-model
   enumeration for five pairs: identical counts, two to three orders of
   magnitude less work. Coverage = exhaustive on the breaker's own
   coordinates x certified volume elsewhere — the carried certificate
   (deps) makes enumeration compile into multiplication.

B. THE WITNESS VARIETY'S RIDE (ZD compiled by kernel, no search): a
   sedenion x is a (left) zero divisor iff det L_x = 0, where L_x is the
   16x16 left-multiplication matrix — the breaker hyperplane IS a
   determinant variety. Riding it: evaluate the polynomial certificate
   (det) on the structured locus instead of brute-multiplying pairs;
   where it vanishes, the annihilator is COMPILED as ker L_x. Recovers
   the S21 exhibit from linear algebra; random gaussian x has det != 0
   (the variety is measure-zero: sampling NEVER finds it; compilation
   always does). The brute search of S21 (44k products) becomes 210
   determinant evaluations on the signed-pair slice.
"""
import importlib.util, numpy as np
from itertools import product
spec = importlib.util.spec_from_file_location("h", "tools/el-atlas-depsort-v3.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)

print("A. dep-projection ride vs full enumeration (exact-count equality required):")
res_full = {i: {} for i in range(len(h.SPACE))}
for X, Y in [('NVE','NVL'), ('GCX','CDC'), ('GCX','SWP'), ('LOC','L26'), ('PUR','PRO')]:
    st_f = sk_f = 0
    for m in h.SPACE:
        a, b = h.CLAIMS[X](m), h.CLAIMS[Y](m)
        st_f += (a=='F' and b=='P') or (b=='F' and a=='P'); sk_f += ((a!='P') != (b!='P'))
    joint = sorted(set(h._CLAIM_DEPS[X]) | set(h._CLAIM_DEPS[Y]))
    mult = 1
    for k in h.KNOBS:
        if k not in joint: mult *= len(h.KNOBS[k])
    st_p = sk_p = 0
    cells = 0
    for vals in product(*(h.KNOBS[k] for k in joint)):
        m = dict(h.BASE); m.update(dict(zip(joint, vals))); cells += 1
        a, b = h.CLAIMS[X](m), h.CLAIMS[Y](m)
        st_p += (a=='F' and b=='P') or (b=='F' and a=='P'); sk_p += ((a!='P') != (b!='P'))
    ok = (st_p*mult == st_f) and (sk_p*mult == sk_f)
    print(f"  {{{X},{Y}}}: full {st_f} truth/{sk_f} kind == projected {st_p}x{mult}/{sk_p}x{mult}: {ok}   work: {cells} cells vs {len(h.SPACE)} models ({len(h.SPACE)//cells}x less)")

print("\nB. determinant-variety ride (sedenions):")
from cd_arith import conj, cdmul   # Π9: shared CD doubling generator
def L(x):
    return np.array([cdmul(x, tuple(1.0 if t==j else 0.0 for t in range(16))) for j in range(16)]).T
x_ex = tuple((1.0 if i==1 else 0.0)+(1.0 if i==10 else 0.0) for i in range(16))
Lx = L(x_ex)
u, s, vt = np.linalg.svd(Lx)
kdim = int(np.sum(s < 1e-9))
kvec = vt[-1]
y_rec = kvec / max(abs(kvec)) if kdim else None
print(f"  exhibit x = e1+e10: det L_x = {np.linalg.det(Lx):.3e}; ker dim = {kdim}; kernel vector support = {sorted(i for i,t in enumerate(y_rec) if abs(t)>1e-9) if kdim else None} (S21 exhibit was e4 - e15: support [4,15]) ; x*y_rec = 0: {bool(np.allclose([t for t in cdmul(x_ex, tuple(y_rec))], 0, atol=1e-9)) if kdim else None}")
rng = np.random.default_rng(9)
gen_ok = all(abs(np.linalg.det(L(tuple(rng.normal(size=16))))) > 1e-6 for _ in range(50))
print(f"  50 random gaussian x: det L_x != 0 every time: {gen_ok}  (the variety is measure-zero — sampling cannot land on it)")
hits = 0; checked = 0
for i in range(1,16):
    for j in range(i+1,16):
        for sgn in (1,-1):
            xx = tuple((1.0 if t==i else 0.0)+(sgn if t==j else 0.0) for t in range(16))
            checked += 1
            if abs(np.linalg.det(L(xx))) < 1e-9: hits += 1
print(f"  signed-pair slice: {checked} determinant evaluations -> {hits} ZD locus members (S21's brute search needed ~44,000 sedenion products to find ONE)")
