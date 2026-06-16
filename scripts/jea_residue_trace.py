#!/usr/bin/env python3
"""jea_residue_trace.py — Δ-Σ-trace rung-(b): the apex HOLDS the gcd/EEA reduction residue, not discards it.

The apex's combine does `na/=gg; D/=gg` -- it ran Euclid for the gcd and (before this rung) THREW AWAY both gg
and the quotient sequence. Per [[feedback_never_discard_residue]] that residue is kept and REUSED:

 * gg (the gcd) is now EMITTED by the kernel (jea_apex: gglo/gghi per node). reduced * gg == unreduced, so the
   reduction is a LOSSLESS RETRACTION (split-idempotent apex): the residue gg inverts it.
 * the EEA QUOTIENT SEQUENCE is the continued fraction = the canonical CF/EEA shape. It is captured by composing
   jea_carrier_trace (gpu_cf -- the SAME Euclid, quotients KEPT) on the reduced output. The CF is SCALE-FREE
   (to_cf(k*p,k*q)==to_cf(p,q)), so it is the canonical VALUE-KEY -- equal value <=> equal CF -- and from_cf is
   the inverse fold (from_cf . to_cf == reduce, the retraction). jea_trace_window/jea_carrier_trace de-orphaned.

What the held residue BUYS (over rung-1's structural interning): VALUE-interning. Structural intern (jea_intern)
merges same-STRUCTURE nodes; the CF canonical key merges same-VALUE nodes that are structurally DISTINCT (e.g.
2/4 and 1/2; or (1/2)*(2/3) and (1/6)+(1/6), both = 1/3) -- a strictly stronger SPPF collapse, free once the
residue is held. One never-discard-residue trace: eval-SPPF (rung-1) + this gcd/EEA residue, same structure.

Witnesses (each [W]):
1. RESIDUE HELD (gg not discarded): for every combine, the kernel-emitted gg == gcd(unreduced), and
   reduced * gg == unreduced -- the reduction is a lossless retraction, gg is its inverse cofactor.
2. CF CANONICAL KEY (jea_carrier_trace composed): per node the captured CF round-trips (from_cf(CF)==reduced)
   and is scale-free (CF(2n,2d)==CF(n,d)) -- the EEA shape is the canonical value-key, materialized not discarded.
3. VALUE-INTERN > STRUCTURAL: a DAG with value-equal-but-structurally-distinct nodes interns to FEWER nodes by
   the CF value-key than by structure -- the held residue buys the stronger collapse; root exact either way.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
from math import gcd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_apex_deliver import run_apex_u128
import jea_carrier_trace as CT                              # U4 gpu_cf -- the EEA-shape capture (orphan composed)
from jea_trace_window import from_cf                        # trace -> value fold (round-trip = reduce)


def dag():
    """9-node ℚ DAG with value-equal-but-structurally-distinct nodes:
      leaves 0:1/2 1:2/3 2:1/6 3:1/6 4:2/4 5:1/2   (4=2/4 and 0,5=1/2 are value-equal, structurally distinct)
      6: mul(0,1)=1/3   7: add(2,3)=1/3            (6 and 7 value-equal 1/3, structurally distinct)
      8: add(6,7)=2/3   (root)"""
    vN=[1,2,1,1,2,1, 0,0,0]; vD=[2,3,6,6,4,2, 1,1,1]
    op=[-1,-1,-1,-1,-1,-1, 1,0,0]; lch=[-1,-1,-1,-1,-1,-1, 0,2,6]; rch=[-1,-1,-1,-1,-1,-1, 1,3,7]
    return dict(vN=vN, vD=vD, op=op, lch=lch, rch=rch, N=9, root=8)


if __name__ == "__main__":
    print("Δ-Σ-trace rung-(b): the apex HOLDS the gcd/EEA reduction residue (gg + CF shape), not discards it\n")
    g=dag(); truth=Fraction(2,3)
    val,err,nodes = run_apex_u128(g, return_nodes=True)
    vN,vD,gg = nodes["vN"], nodes["vD"], nodes["gg"]

    # W1: gg is the held residue -- reduced * gg == unreduced (lossless retraction), gg == gcd(unreduced).
    w1=True; rows=[]
    for i in range(g["N"]):
        if g["op"][i]==-1: continue
        a,b=g["lch"][i],g["rch"][i]; nl,dl,nr,dr=vN[a],vD[a],vN[b],vD[b]
        na = nl*nr if g["op"][i]==1 else nl*dr+nr*dl; D = dl*dr
        gh=gcd(na,D)
        ok = (gg[i]==gh) and (vN[i]*gg[i]==na) and (vD[i]*gg[i]==D)     # reduced*gg reconstructs unreduced
        w1 = w1 and ok
        rows.append((i, f"{na}/{D}", gg[i], f"{vN[i]}/{vD[i]}", ok))
    print("  gcd RESIDUE per combine (kernel-emitted; reduced*gg == unreduced):")
    for i,unred,ggi,red,ok in rows:
        print(f"    node{i}: unreduced {unred:>7} = reduced {red:<5} * gg={ggi}   lossless:{ok}")

    # W2: capture the CF/EEA shape per node (jea_carrier_trace.gpu_cf), the canonical scale-free value-key.
    cfs,_ = CT.gpu_cf(vN, vD)                                # P/Q = the apex's per-node (num,den)
    cfs2,_ = CT.gpu_cf([2*x for x in vN], [2*x for x in vD]) # scaled -> same CF (scale-free => canonical)
    roundtrips = all(from_cf(cfs[i])==(vN[i]//gcd(vN[i],vD[i]), vD[i]//gcd(vN[i],vD[i])) for i in range(g["N"]))
    scalefree  = all(cfs[i]==cfs2[i] for i in range(g["N"]))
    w2 = roundtrips and scalefree
    print(f"\n  CF/EEA shape captured per node (jea_carrier_trace, composed): round-trip==reduce:{roundtrips} "
          f"scale-free:{scalefree}")

    # W3: VALUE-intern (CF key) merges value-equal structurally-distinct nodes that STRUCTURAL intern keeps apart.
    canon_s={}; ids=[0]*g["N"]                               # structural hash-cons (op, canonical children)
    for i in range(g["N"]):
        key = ("lf",vN[i],vD[i]) if g["op"][i]==-1 else (g["op"][i], ids[g["lch"][i]], ids[g["rch"][i]])
        ids[i]=canon_s.setdefault(key, len(canon_s))
    n_struct=len(canon_s)
    n_value=len({tuple(cfs[i]) for i in range(g["N"])})      # value key = the CF (scale-free canonical)
    w3 = (n_value < n_struct) and (val==truth)
    print(f"\n  intern of the {g['N']}-node DAG: STRUCTURAL distinct = {n_struct}  vs  VALUE distinct (CF key) = {n_value}"
          f"   (value < structural: 2/4≡1/2, and (1/2*2/3)≡(1/6+1/6)=1/3 merged)")
    print(f"  apex root = {val}  == truth {truth}: {val==truth}; err={err}")

    print(f"\nW1 RESIDUE HELD (kernel emits gg; reduced*gg == unreduced -- lossless retraction, gg the inverse cofactor): {w1}")
    print(f"W2 CF CANONICAL KEY (jea_carrier_trace composed; CF round-trips to reduce + scale-free = canonical value-key): {w2}")
    print(f"W3 VALUE-INTERN > STRUCTURAL ({n_value}<{n_struct}; CF value-key merges value-equal structurally-distinct nodes;"
          f" root exact): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-trace rung-(b): the apex no longer discards the gcd/EEA residue. The")
    print(f"  kernel EMITS gg (reduced*gg==unreduced: reduction is a lossless retraction), and the EEA quotient")
    print(f"  sequence -- the canonical CF shape -- is materialized by composing jea_carrier_trace (de-orphaned),")
    print(f"  scale-free, round-tripping to reduce. Held, the residue BUYS value-interning: the CF value-key merges")
    print(f"  value-equal structurally-distinct nodes structural interning cannot. eval-SPPF + gcd/EEA residue = one")
    print(f"  never-discard-residue trace. NEXT: hold the supervisor decision WAL in the same SPPF (rung c).")
