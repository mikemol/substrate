#!/usr/bin/env python3
"""jea_apex_deliver.py — err=2 -> byte-limb DELIVER: wire the apex's escalation flag to the EXISTING jea_limb carrier.

The apex (jea_apex) combines on the u128 carrier and PREDICT-PLACES: when a combine's bit-length would exceed
u128 it sets err=2 (escalation needed) and writes a placeholder. That flag was un-wired -- beyond u128 the result
was incomplete. This is the final escalation tier: err=2 -> recompute exactly on the byte-limb carrier (jea_limb),
the escalate-don't-truncate guarantee. The carrier escalates u64 -> u128 -> byte-limb; byte-limb IS jea_limb
(gpu_add / dp4a-convolution gpu_mul). The DELIVER reuses it -- not a reinvented carrier.

The no-in-kernel-gcd insight (from the carrier work): ℚ stays exact WITHOUT per-step reduction -- accumulate
num/den exactly via byte-limb and REDUCE ONCE AT READOUT. So the proven byte-limb add/mul suffice for the deliver;
no byte-limb gcd is needed. (Simplest correct deliver: when ANY node escalates, recompute the whole DAG exactly on
byte-limb -- escalation propagates to ancestors anyway. A subtree-only deliver is a future optimization.)

Witnesses (each [W]):
1. ESCALATION FIRES: a DAG whose intermediates exceed u128 makes the apex set err=2 (u128 alone is insufficient
   -- placeholder root, not the true value).
2. DELIVER EXACT: the byte-limb deliver (jea_limb, reduce-at-readout) recomputes the TRUE rational exactly, at a
   magnitude beyond u128 -- escalate-don't-truncate delivered, not flagged-and-dropped.
3. EXISTING CARRIER: the deliver is jea_limb's add/mul (the established byte-limb tier), invoked by err=2 -- no
   reinvention; the apex u128 path is unchanged for DAGs that fit (err=0).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_apex import _apex, FIELDS
from jea_generator_dag import build_dag
from jea_limb_gpu import to_limbs, from_limbs, gpu_add, gpu_mul

NSM = cp.cuda.Device().attributes["MultiProcessorCount"]; BLOCKS, THREADS = 8*NSM, 128


def predict_per_node(g):
    """Live O(N) solve over the DAG: unreduced num/den bit-length UPPER BOUNDS per node, by the SAME formula the
    apex predict-places with (mul: bln_L+bln_R; add: max(bln_L+bld_R, bln_R+bld_L)+1; den: bld_L+bld_R). Leaves-
    first. pred(i)=max(nb,db) is monotone toward the root, so {pred>128} is the UP-CLOSED escalation crown and
    {pred<=128} is DOWN-CLOSED and >= the apex's ACTUAL (reduced) lengths -> every such node the apex computed
    correctly. Returns (nb, db)."""
    N = g["N"]; op = g["op"]; lch = g["lch"]; rch = g["rch"]; vN = g["vN"]; vD = g["vD"]
    nb = [0]*N; db = [0]*N
    for i in range(N):
        if op[i] == -1:
            nb[i] = max(1, int(vN[i]).bit_length()); db[i] = max(1, int(vD[i]).bit_length())
        else:
            a, b = lch[i], rch[i]
            if op[i] == 1:
                nb[i] = nb[a] + nb[b]; db[i] = db[a] + db[b]
            else:
                nb[i] = max(nb[a] + db[b], nb[b] + db[a]) + 1; db[i] = db[a] + db[b]
    return nb, db


def run_apex_u128(g, return_nodes=False):
    """Run the apex on the u128 carrier (full lanes, spin=0). Return (root Fraction-or-None, err); with
    return_nodes also (vN_u128, vD_u128) = per-node reduced u128 values (correct for non-escalated nodes)."""
    N = g["N"]; root = g["root"]
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]
    vN=[int(x) for x in g["vN"]]; vD=[int(x) for x in g["vD"]]
    d=lambda a,t: cp.asarray(a,t)
    dop=d(op,cp.int32); dn=cp.zeros(N,cp.int32); dl=d(list(g["lch"]),cp.int32); dr=d(list(g["rch"]),cp.int32)
    vnl=d([v & (2**64-1) for v in vN],cp.uint64); vnh=d([v>>64 for v in vN],cp.uint64)
    vdl=d([v & (2**64-1) for v in vD],cp.uint64); vdh=d([v>>64 for v in vD],cp.uint64)
    bln=d([v.bit_length() for v in vN],cp.int32); bld=d([v.bit_length() for v in vD],cp.int32)
    st=d([1 if op[i]==2 else 0 for i in range(N)],cp.int32); pe=cp.full(1,sum(1 for i in range(N) if op[i]!=2),cp.int32)
    qt=cp.full(1,N,cp.int32); er=cp.zeros(1,cp.int32); pk=cp.zeros(2*FIELDS,cp.int32); pk[0]=BLOCKS*THREADS; ac=cp.zeros(1,cp.int32)
    gt=cp.zeros(4,cp.int32); gtn=cp.zeros(1,cp.int32)
    _apex((BLOCKS,),(THREADS,),(dop,dn,dl,dr,vnl,vnh,vdl,vdh,bln,bld,st,qt,pe,er,np.int32(N),np.int64(N),
                                pk,ac,np.int32(FIELDS),gt,gtn,np.int32(4),np.int32(0)))
    cp.cuda.Stream.null.synchronize()
    VNL=vnl.get(); VNH=vnh.get(); VDL=vdl.get(); VDH=vdh.get()
    rn=(int(VNH[root])<<64)|int(VNL[root]); rd=(int(VDH[root])<<64)|int(VDL[root])
    val=(Fraction(rn,rd) if rd else None); err=int(er.get()[0])
    if return_nodes:
        vN_u128=[(int(VNH[i])<<64)|int(VNL[i]) for i in range(N)]
        vD_u128=[(int(VDH[i])<<64)|int(VDL[i]) for i in range(N)]
        return val, err, vN_u128, vD_u128
    return val, err


def deliver_bytelimb(g):
    """err=2 DELIVER: exact ℚ-fold on the byte-limb carrier (jea_limb add/mul), reduce at readout. ANY magnitude."""
    N=g["N"]; op=g["op"]; lch=g["lch"]; rch=g["rch"]; vN=g["vN"]; vD=g["vD"]
    num=[None]*N; den=[None]*N
    L_=lambda v: cp.asarray(to_limbs(int(v)))
    for i in range(N):
        if op[i]==-1: num[i]=L_(vN[i]); den[i]=L_(vD[i])
        else:
            a,b=lch[i],rch[i]; nl,dl,nr,dr=num[a],den[a],num[b],den[b]
            if op[i]==1: num[i]=gpu_mul(nl,nr)[0]; den[i]=gpu_mul(dl,dr)[0]
            else: num[i]=gpu_add(gpu_mul(nl,dr)[0], gpu_mul(nr,dl)[0]); den[i]=gpu_mul(dl,dr)[0]
    r=g["root"]
    return Fraction(from_limbs(num[r]), from_limbs(den[r]))      # REDUCE at readout


def deliver_subtree(g, vN_u128, vD_u128):
    """Δ-Ω-deliver-opt: byte-limb ONLY the escalation CROWN (the up-closed set pred>128), LIFTING the apex's
    correct u128 values for the crown's non-crown children. Solves over the subtree carrying the overflow, not
    the whole DAG. Returns (Fraction, limb_muls) -- limb_muls = byte-limb gpu_mul count (the cost that shrinks)."""
    N=g["N"]; op=g["op"]; lch=g["lch"]; rch=g["rch"]; vN=g["vN"]; vD=g["vD"]; root=g["root"]
    nb,db=predict_per_node(g)
    crown=lambda i: max(nb[i],db[i])>128                         # up-closed; apex placeholdered exactly a subset
    num=[None]*N; den=[None]*N; muls=[0]
    def lift(i):                                                 # value of node i in limbs (memoized)
        if num[i] is None:                                       # not crown-computed -> EXACT source: leaf literal
            nv,dv=(int(vN[i]),int(vD[i])) if op[i]==-1 else (int(vN_u128[i]),int(vD_u128[i]))  # or apex's reduced u128
            num[i]=cp.asarray(to_limbs(nv)); den[i]=cp.asarray(to_limbs(dv))
        return num[i],den[i]
    for i in range(N):                                           # topological (leaves-first); compute ONLY the crown
        if op[i]==-1 or not crown(i): continue
        a,b=lch[i],rch[i]; nl,dl=lift(a); nr,dr=lift(b)          # children: crown-computed or lifted from u128/literal
        if op[i]==1: num[i]=gpu_mul(nl,nr)[0]; den[i]=gpu_mul(dl,dr)[0]; muls[0]+=2
        else: num[i]=gpu_add(gpu_mul(nl,dr)[0], gpu_mul(nr,dl)[0]); den[i]=gpu_mul(dl,dr)[0]; muls[0]+=3
    nrt,drt=lift(root)                                           # root in crown when err=2; else lifted
    return Fraction(from_limbs(nrt), from_limbs(drt)), muls[0]


if __name__ == "__main__":
    print("err=2 -> byte-limb DELIVER: the apex's escalation flag wired to the EXISTING jea_limb carrier\n")
    # find a DAG whose intermediates exceed u128 (so the apex sets err=2)
    g=None; apex_err=0
    for (n,depth) in [(256,8),(256,12),(256,16),(512,12),(512,16)]:
        cand=build_dag(n,depth); v,e,vN_u,vD_u=run_apex_u128(cand,return_nodes=True)
        if e==2: g, apex_val, apex_err, vN_u128, vD_u128 = cand, v, e, vN_u, vD_u; chosen=(n,depth); break
    if g is None:
        print("  (no u128-overflowing DAG found in the probe set; widen it)"); sys.exit(1)

    truth=g["truth"]; tb=max(truth.numerator.bit_length(), truth.denominator.bit_length())
    ncomb=sum(1 for i in range(g["N"]) if g["op"][i]!=-1)
    nb,db=predict_per_node(g); ncrown=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and max(nb[i],db[i])>128)
    print(f"  DAG build_dag{chosen}: {g['N']} nodes ({ncomb} combines), true rational ~{tb} bits (EXCEEDS u128={tb>128})")
    print(f"  apex (u128 only): err={apex_err} (=2 escalation needed); root={apex_val} (placeholder/incomplete, != truth)")

    full = deliver_bytelimb(g)                                  # COARSE: recompute the WHOLE DAG on byte-limb
    sub, sub_muls = deliver_subtree(g, vN_u128, vD_u128)        # SUBTREE: byte-limb only the escalation crown
    full_muls = sum((2 if g["op"][i]==1 else 3) for i in range(g["N"]) if g["op"][i]!=-1)
    print(f"  full-DAG  deliver: root={str(full)[:50]}...  == truth: {full==truth}  (byte-limb muls ~{full_muls}, all {ncomb} combines)")
    print(f"  SUBTREE   deliver: root={str(sub)[:50]}...  == truth: {sub==truth}   (byte-limb muls {sub_muls}, only {ncrown} crown combines)")

    w1 = (apex_err==2) and (apex_val != truth)                  # u128 insufficient, flagged
    w2 = (full == truth) and (sub == truth) and (tb > 128)      # BOTH exact beyond u128 (subtree == full == truth)
    w3 = (sub_muls < full_muls) and (ncrown < ncomb)            # subtree solves the CROWN only -- strictly less work
    print(f"\nW1 ESCALATION FIRES (u128 insufficient -> apex err=2, root != truth): {w1}")
    print(f"W2 BOTH EXACT beyond u128 (subtree == full == truth, {tb}>128 bits -- the subtree loses nothing): {w2}")
    print(f"W3 SUBTREE < FULL (byte-limb work {sub_muls} vs {full_muls} muls; only {ncrown}/{ncomb} combines redone -- the")
    print(f"   crown carrying the overflow, valid nodes LIFTED from the apex's u128 result): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ω-deliver-opt: escalation no longer recomputes the WHOLE DAG (a coarse")
    print(f"  coordinate). The escalation CROWN (up-closed pred>128) is the geometry carrying the overflow; only it")
    print(f"  runs on byte-limb, the apex's correct u128 values for the crown's valid children are LIFTED. Exact and")
    print(f"  strictly less work, degenerating to the full DAG only when EVERYTHING overflows. Solve over the subtree.")
