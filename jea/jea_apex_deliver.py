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
    return_nodes also a `nodes` dict {vN, vD, escal, tier} -- per-node reduced u128 values (correct for non-crown
    nodes), the device-emitted escalation CROWN (escal[i]=1 iff node i overflowed or has a crown descendant), and
    the per-node CARRIER TIER the kernel placed each node on (0=u64, 1=u128, 2=byte-limb/crown)."""
    N = g["N"]; root = g["root"]
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]
    vN=[int(x) for x in g["vN"]]; vD=[int(x) for x in g["vD"]]
    d=lambda a,t: cp.asarray(a,t)
    dop=d(op,cp.int32); dn=cp.zeros(N,cp.int32); dl=d(list(g["lch"]),cp.int32); dr=d(list(g["rch"]),cp.int32)
    vnl=d([v & (2**64-1) for v in vN],cp.uint64); vnh=d([v>>64 for v in vN],cp.uint64)
    vdl=d([v & (2**64-1) for v in vD],cp.uint64); vdh=d([v>>64 for v in vD],cp.uint64)
    bln=d([v.bit_length() for v in vN],cp.int32); bld=d([v.bit_length() for v in vD],cp.int32)
    escal=cp.zeros(N,cp.int32); tier=cp.zeros(N,cp.int32)
    st=d([1 if op[i]==2 else 0 for i in range(N)],cp.int32); pe=cp.full(1,sum(1 for i in range(N) if op[i]!=2),cp.int32)
    qt=cp.full(1,N,cp.int32); er=cp.zeros(1,cp.int32); pk=cp.zeros(2*FIELDS,cp.int32); pk[0]=BLOCKS*THREADS; ac=cp.zeros(1,cp.int32)
    gt=cp.zeros(4,cp.int32); gtn=cp.zeros(1,cp.int32)
    tdum=cp.zeros(1,cp.float64); ddum=cp.zeros(8,cp.int32)       # decide_dev=0: no on-device supervisor (eval path)
    _apex((BLOCKS,),(THREADS,),(dop,dn,dl,dr,vnl,vnh,vdl,vdh,bln,bld,escal,tier,st,qt,pe,er,np.int32(N),np.int64(N),
                                pk,ac,np.int32(FIELDS),gt,gtn,np.int32(4),np.int32(0),
                                tdum,ddum,np.int32(14),np.int32(0),np.int32(BLOCKS*THREADS),np.int32(0)))
    cp.cuda.Stream.null.synchronize()
    VNL=vnl.get(); VNH=vnh.get(); VDL=vdl.get(); VDH=vdh.get()
    rn=(int(VNH[root])<<64)|int(VNL[root]); rd=(int(VDH[root])<<64)|int(VDL[root])
    val=(Fraction(rn,rd) if rd else None); err=int(er.get()[0])
    if return_nodes:
        nodes=dict(vN=[(int(VNH[i])<<64)|int(VNL[i]) for i in range(N)],
                   vD=[(int(VDH[i])<<64)|int(VDL[i]) for i in range(N)],
                   escal=[int(x) for x in escal.get()], tier=[int(x) for x in tier.get()])
        return val, err, nodes
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


def deliver_subtree(g, vN_u128, vD_u128, escal=None):
    """Δ-Ω-deliver-opt / Δ-Ψ: byte-limb ONLY the escalation CROWN, LIFTING the apex's correct u128 values for the
    crown's non-crown children. Solves over the subtree carrying the overflow, not the whole DAG. The crown is the
    DEVICE's residue (escal[], emitted on-device by the apex's mark-propagation) when given -- recompute-from-
    residue, tighter than re-predicting on the host; else falls back to the host predict (predict_per_node).
    Returns (Fraction, limb_muls) -- limb_muls = byte-limb gpu_mul count (the cost that shrinks)."""
    N=g["N"]; op=g["op"]; lch=g["lch"]; rch=g["rch"]; vN=g["vN"]; vD=g["vD"]; root=g["root"]
    if escal is not None:
        crown=lambda i: escal[i]==1                              # DEVICE-emitted crown (on-device mark propagation)
    else:
        nb,db=predict_per_node(g)
        crown=lambda i: max(nb[i],db[i])>128                     # host fallback: up-closed; apex placeholdered a subset
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
    print("Δ-Ψ: the escalation CROWN is the DEVICE's residue (on-device mark propagation), not host re-prediction\n")
    # find a DAG whose intermediates exceed u128 (so the apex sets err=2)
    g=None; apex_err=0
    for (n,depth) in [(256,8),(256,12),(256,16),(512,12),(512,16)]:
        cand=build_dag(n,depth); v,e,nd=run_apex_u128(cand,return_nodes=True)
        if e==2: g, apex_val, apex_err, nodes = cand, v, e, nd; chosen=(n,depth); break
    if g is None:
        print("  (no u128-overflowing DAG found in the probe set; widen it)"); sys.exit(1)
    vN_u128, vD_u128, escal, tier = nodes["vN"], nodes["vD"], nodes["escal"], nodes["tier"]

    truth=g["truth"]; tb=max(truth.numerator.bit_length(), truth.denominator.bit_length())
    ncomb=sum(1 for i in range(g["N"]) if g["op"][i]!=-1)
    nb,db=predict_per_node(g); host_crown=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and max(nb[i],db[i])>128)
    dev_crown=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and escal[i]==1)
    t0=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and tier[i]==0)   # per-node carrier placement (Δ-Φ-pernode):
    t1=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and tier[i]==1)   # how many combines the kernel placed on
    t2=sum(1 for i in range(g["N"]) if g["op"][i]!=-1 and tier[i]==2)   # u64 / u128 / byte-limb, EACH its narrowest
    print(f"  DAG build_dag{chosen}: {g['N']} nodes ({ncomb} combines), true rational ~{tb} bits (EXCEEDS u128={tb>128})")
    print(f"  apex (u128 only): err={apex_err} (=2); root={apex_val} (placeholder, != truth)")
    print(f"  PER-NODE carrier placement (on-device, Δ-Φ-pernode): u64={t0}  u128={t1}  byte-limb(crown)={t2}  of {ncomb} combines")
    print(f"  crown size: host re-predict (unreduced) = {host_crown}  vs  DEVICE residue (actual reduced) = {dev_crown}  (device <= host)")

    full = deliver_bytelimb(g)                                  # COARSE: recompute the WHOLE DAG on byte-limb
    sub_h, sub_h_muls = deliver_subtree(g, vN_u128, vD_u128)              # crown via HOST re-predict (fallback)
    sub_d, sub_d_muls = deliver_subtree(g, vN_u128, vD_u128, escal=escal) # crown via DEVICE residue (Δ-Ψ)
    full_muls = sum((2 if g["op"][i]==1 else 3) for i in range(g["N"]) if g["op"][i]!=-1)
    print(f"  full-DAG deliver: == truth {full==truth}  (byte-limb muls ~{full_muls}, all {ncomb} combines)")
    print(f"  host-crown delvr: == truth {sub_h==truth}  (muls {sub_h_muls}, {host_crown} crown combines)")
    print(f"  DEVICE-crown dlv: == truth {sub_d==truth}  (muls {sub_d_muls}, {dev_crown} crown combines)  <- recompute-from-residue")

    dev_subset = all((escal[i]==0) or (max(nb[i],db[i])>128) for i in range(g["N"]))  # device crown ⊆ host crown (provable)
    w1 = (apex_err==2) and (apex_val != truth)                  # u128 insufficient, flagged on-device
    w2 = (full == truth) and (sub_h == truth) and (sub_d == truth) and (tb > 128)     # all three exact
    w3 = dev_subset and (dev_crown <= host_crown) and (sub_d_muls <= sub_h_muls) and (dev_crown < ncomb)
    print(f"\nW1 ESCALATION FIRES on-device (apex err=2, root != truth): {w1}")
    print(f"W2 ALL EXACT beyond u128 (full == host-crown == DEVICE-crown == truth, {tb}>128 bits): {w2}")
    print(f"W3 DEVICE RESIDUE ⊆ host re-predict ({dev_crown}<={host_crown}), same-or-less byte-limb work ({sub_d_muls}<={sub_h_muls}),")
    print(f"   crown < all combines ({dev_crown}<{ncomb}) -- the crown is the device's OWN output, not re-derived on host: {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ψ: the escalation crown is computed ON-DEVICE (the apex propagates an")
    print(f"  escalation mark up the DAG: a node is crowned iff it overflows u128 OR a child is). The host deliver")
    print(f"  READS that residue (escal[]) instead of re-predicting -- recompute-from-residue, not copy-across-boundary.")
    print(f"  The device crown is TIGHTER (actual reduced lengths) ⊆ the host unreduced predict, so it byte-limbs no")
    print(f"  more nodes, and the host no longer duplicates the device's own escalation solve. (Δ-Φ-pernode DONE: the")
    print(f"  apex kernel already places EACH node on its narrowest carrier on-device via the emitted tier[] = 0/1/2.)")
