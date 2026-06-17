"""
nve-alias-delta-pilot.py — S9: validate the delta between the two vE
formulations that S8 recorded as a "supersession":
  F_pack  : packed-node semantics (disjunction = held n-ary pack with
            case weights; elimination = projection over the pack)
  F_bridge: split/join carrier expansion + (binary) Wheatstone bridge

Adjudication sought: alias (one referent, plural readings) vs genuinely
separated — and if separated, WHERE.

Checks (high-impedance bridge reading r(G_left_top, G_left_bot | ref)
       = G_lt/(G_lt+G_lb) - ref_t/(ref_t+ref_b)):

A. n=2 ALIAS WITNESS: against the balanced reference (1,1), the bridge
   reading of a case-pair equals HALF ITS L1-NORMALIZED INTERNAL BIAS:
   r(a,b|1,1) = (a-b)/(2(a+b)) exactly. The pack's internal bias read and
   the bridge read are the same number — storage-layer and
   measurement-layer readings of one referent. UNSEPARATED at n=2.
B. n=3 SEPARATION WITNESS (necessity): packs A=(1,2,3), B=(1,2.5,2.5)
   share mass (6) and share the partition-{1} bridge reading; they differ
   on partition-{2}. A SINGLE binary bridge reading under-determines a
   3-pack: F_bridge as stated (one bridge) is strictly poorer than
   F_pack at n>=3. SEPARATED at n>=3 — the delta is ARITY.
C. TOMOGRAPHY (sufficiency, advancing the open n-ary item): mass + (n-1)
   partition bridge readings reconstruct the n-pack exactly (linear
   inversion); verified for random 3-packs. So the n-ary reconciliation
   = a bridge LATTICE of n-1 independent readings + the mass channel:
   necessity from B, sufficiency from C => exactly n-1.
"""
import random
random.seed(17)

def r(top, bot, rt=1.0, rb=1.0):
    return top/(top+bot) - rt/(rt+rb)

okA = all(abs(r(a,b) - (a-b)/(2*(a+b))) < 1e-12
          for a,b in ((random.uniform(.1,10), random.uniform(.1,10)) for _ in range(2000)))
print(f"A. n=2 alias witness: bridge-vs-balanced-ref == half normalized pack bias (2000 samples): {okA}")

A, B = (1.0,2.0,3.0), (1.0,2.5,2.5)
mA, mB = sum(A), sum(B)
p1A, p1B = r(A[0], mA-A[0]), r(B[0], mB-B[0])
p2A, p2B = r(A[1], mA-A[1]), r(B[1], mB-B[1])
print(f"B. n=3 separation: masses {mA}=={mB}; partition-1 readings {p1A:.6f}=={p1B:.6f} (blind); partition-2 readings {p2A:.6f} vs {p2B:.6f} (sees): single binary bridge under-determines the pack: {abs(p1A-p1B)<1e-12 and abs(p2A-p2B)>1e-3}")

okC = True
for _ in range(2000):
    G = [random.uniform(.1,10) for _ in range(3)]
    M = sum(G)
    r1, r2 = r(G[0], M-G[0]), r(G[1], M-G[1])
    g1, g2 = M*(r1+0.5), M*(r2+0.5)
    okC &= max(abs(g1-G[0]), abs(g2-G[1]), abs((M-g1-g2)-G[2])) < 1e-9
print(f"C. tomography: mass + (n-1)=2 bridge readings reconstruct the 3-pack exactly (2000 samples): {okC}")
print("VERDICT: alias at n=2 (one referent, layer-readings); separated at n>=3 by arity; reconciliation = bridge lattice, exactly n-1 readings + mass.")
