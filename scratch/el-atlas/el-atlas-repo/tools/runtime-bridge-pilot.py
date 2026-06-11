"""
runtime-bridge-pilot.py — review-prompted (R1): three checks behind the
"static map -> dynamic memory layer" question.

1. MERGE DOES NOT FACTOR THROUGH THE QUOTIENT. Replicated evidence state =
   the pair (p, n) with join-merge (elementwise max, single source). The
   diagonal quotient b = p - n is NOT a congruence for merge: exhaustive
   small-grid search for states with equal bias whose merges have unequal
   bias. (This is the PN-counter design fact: production CRDTs keep the
   pair BECAUSE the evaluated difference does not merge — the prohibition,
   deployed.)
2. PROJECTIVE CONVERGENCE UNDER CYCLIC SUPPORT. Pair power-iteration with
   positive weights: mass diverges monotonically (the ledger coordinate)
   while G = E+/E- converges (Perron) — the scalar G-calculus's
   least-fixed-point equilibrium is the projective shadow of carrier
   dynamics; the quotient was doing normalization work that the codec
   instead localizes to one channel.
3. SOURCE-INDEXING DISSOLVES THE DOUBLE-COUNT. Source-indexed carrier:
   within-source merge is idempotent (re-merging the same evidence does
   not double), cross-source read is additive (independent endorsements
   sum) — G_OR(G,G)=2G is the scalar shadow of erased provenance.
"""
import itertools

# 1 — quotient not a congruence for merge
cnt = 0; wit = None
G = range(0, 6)
for p1,n1,p2,n2,tp,tn in itertools.product(G, repeat=6):
    if p1-n1 != p2-n2: continue
    m1 = (max(p1,tp), max(n1,tn)); m2 = (max(p2,tp), max(n2,tn))
    if (m1[0]-m1[1]) != (m2[0]-m2[1]):
        cnt += 1
        if wit is None: wit = ((p1,n1),(p2,n2),(tp,tn),m1,m2)
print("1. equal-bias states with unequal-bias merges:", cnt, "witnesses; first:", wit)

# 2 — mass diverges, balance converges (projective/Perron)
A = [[1.0,0.5],[0.2,1.1]]   # Perron ratio nontrivial (~1.35), not the G=1 conflation point
x = [1.0,1.0]; hist = []
for _ in range(60):
    x = [A[0][0]*x[0]+A[0][1]*x[1], A[1][0]*x[0]+A[1][1]*x[1]]
    hist.append((x[0]+x[1], x[0]/x[1]))
mass_div = hist[-1][0] > 1e3*hist[0][0]
tail = [r for _,r in hist[-10:]]
g_conv = max(tail)-min(tail) < 1e-9
print(f"2. mass diverges: {mass_div} (mass_60 = {hist[-1][0]:.3e});  G = E+/E- converges: {g_conv} (G* = {hist[-1][1]:.9f})")

# 3 — source-indexed carrier: idempotent within, additive across
def merge(a,b):
    out = dict(a)
    for k,(p,n) in b.items():
        out[k] = (max(out[k][0],p), max(out[k][1],n)) if k in out else (p,n)
    return out
read = lambda s: (sum(p for p,_ in s.values()), sum(n for _,n in s.values()))
s = {'src1':(4.0,1.0)}
print("3. re-merge same source:", read(merge(s,s)), "(idempotent);  distinct source:", read(merge(s,{'src2':(4.0,1.0)})), "(additive)")
