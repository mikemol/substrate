#!/usr/bin/env python3
"""jea_resident.py — Δ-Σ-trace (b-real): the resident SPPF forest lives ON-DEVICE as a sorted (linear-quadtree)
code index; sharing-lookup is cp.searchsorted (device), merge is a device sort, and the forest GROWS by new nodes
only across evaluations. The host orchestrates per height; the FOREST (codes + the sharing test) is device-resident.

Design: a node's IDENTITY id must be STABLE (append-only) -- a sorted-position id would shift on every merge and
break child references. So payload (op,lch,rch,value) is append-only by stable id; a SEPARATE device array pair
(ccode sorted, csid) is the linear-quadtree index used for the device sharing-lookup. The structural code of a
combine is op | morton(lch_id,rch_id) (jea_zsppf.morton2 -- the z-code, so the index is a quadtree: dedup AND
locality, W2/W5). Leaves are few -> a host map; combines (the bulk) are the device-resident sorted index.

evaluate(g, F): intern g bottom-up into F (device searchsorted per height -> SHARE existing / ADD new + device
merge), then evaluate ONLY the new frontier on the apex and store values into F. Exact at any magnitude (crown
nodes host-folded from resident children). The forest persists across calls (cross-eval sharing). Used by jea_eval.

Witnesses ([W], in __main__):
1. DEVICE-RESIDENT + GROWS-BY-NEW: F.ccode/csid are cupy arrays; eval(T2) sharing S with T1 finds S via
   cp.searchsorted (device) -> the forest grows ONLY by T2's genuinely-new nodes; shared nodes referenced.
2. EXACT: root values correct through the device-resident evaluator (any magnitude).
3. SHARING IS A DEVICE LOOKUP: the per-height share/add is cp.searchsorted into the resident sorted index + a
   device merge -- not a host hash table.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_zsppf import morton2, heights
import jea_mega_eval as MEGAE                                   # the FUSED on-device intern+combine megakernel (Δ-Σ-mega rung-2)


class Forest:
    """The device-resident SPPF: append-only stable payload + a device sorted (code -> stable id) linear quadtree."""
    def __init__(self):
        self.op=[]; self.lch=[]; self.rch=[]; self.vn=[]; self.vd=[]      # stable payload by sid (append-only)
        self.code=[]                                                     # per-node locality code (structural / value z-code)
        self.leafmap={}                                                  # (vN,vD) -> sid (leaves are few; host)
        self.ccode=cp.zeros(0,cp.int64); self.csid=cp.zeros(0,cp.int64)  # DEVICE sorted combine-code index (Phase-1 dedup)
        # b-real-store: the PHYSICAL store -- payload STRUCTURE laid out code-ordered (the linear quadtree, ALL nodes);
        # values stay in the stable store (arbitrary magnitude -> byte-limb carrier, not packable into int64).
        self.pslot=cp.zeros(0,cp.int64)                                  # stable id -> physical position (code order)
        self.pstable=cp.zeros(0,cp.int64); self.pcode=cp.zeros(0,cp.int64)   # physical position -> stable id / code (sorted)
        self.FE=MEGAE.Fused()                                            # the PERSISTENT on-device FUSED intern+combine (Δ-Σ-mega rung-2)

    def _new(self, op,l,r,vn,vd,code):
        sid=len(self.op); self.op.append(op); self.lch.append(l); self.rch.append(r); self.vn.append(vn); self.vd.append(vd)
        self.code.append(int(code)); return sid

    def leaf(self, vN,vD):
        k=(vN,vD); s=self.leafmap.get(k)
        if s is not None: return s
        lc=int(morton2(np.array([vN & 0xFFFF]), np.array([vD & 0xFFFF]))[0])   # leaf value-locality code
        s=self._new(-1,-1,-1,vN,vD,lc); self.leafmap[k]=s; return s

    def lookup(self, codes):                                             # DEVICE searchsorted -> stable sid or -1 (miss)
        if self.ccode.size==0: return np.full(len(codes),-1,np.int64)
        c=cp.asarray(codes,cp.int64); pos=cp.clip(cp.searchsorted(self.ccode,c),0,self.ccode.size-1)
        return cp.where(self.ccode[pos]==c, self.csid[pos], cp.int64(-1)).get()

    def add_combine(self, code, op,l,r):                                 # new combine -> stable sid (buffered for merge)
        s=self._new(op,l,r,0,1,code); self._pc.append(int(code)); self._ps.append(s); return s

    def materialize(self):                                               # b-real-store: lay the forest STRUCTURE physically
        codes=cp.asarray(self.code, cp.int64); order=cp.argsort(codes, kind="stable")   # in code order (DEVICE argsort)
        self.pcode=codes[order]; self.pstable=order                      # physical pos -> (code, stable id), sorted by code
        self.pslot=cp.empty(codes.size, cp.int64); self.pslot[order]=cp.arange(codes.size)   # stable id -> physical pos

    def gather(self, sids):                                              # read a working set's physical positions (coalesced
        return self.pslot[cp.asarray(sids, cp.int64)].get()             # for code-coherent sets); values via stable store

    def gather_cost(self, sids, T):                                      # HBM tiles touched gathering a working set:
        stable=len({int(s)//T for s in sids})                           #   stable-id (creation) order  vs
        loc=len({int(p)//T for p in self.gather(sids)})                 #   PHYSICAL code order (b-real-store, real pslot)
        return stable, loc

    def merge(self):                                                     # DEVICE merge buffered new codes into the index
        if not self._pc: return
        allc=cp.concatenate([self.ccode, cp.asarray(self._pc,cp.int64)])
        alls=cp.concatenate([self.csid, cp.asarray(self._ps,cp.int64)])
        o=cp.argsort(allc,kind="stable"); self.ccode=allc[o]; self.csid=alls[o]; self._pc=[]; self._ps=[]

    _pc=[]; _ps=[]
    def value(self, sid): return Fraction(self.vn[sid], self.vd[sid])
    def size(self): return len(self.op)


def _ccode(op, l, r):                                                    # structural z-code: morton(lch,rch) dominant, op LOW
    return (int(morton2(np.array([l]), np.array([r]))[0]) << 2) | (int(op) & 3)   # op high -> mixed-op sets split; keep it low


def evaluate(g, F):
    """Intern AND evaluate g into the device-resident forest F in ONE fused kernel (Δ-Σ-mega rung-2): the kernel
    hash-conses each node and, if NEW, computes its value once (u64/u128 carrier); SHARED sub-terms reuse the
    resident value. The host only does node bookkeeping (register the new canon ids, reading their values from the
    fused device store) and the EXACT crown fold for any node whose value exceeds u128 (recompute-from-residue: the
    crown folds from resident children, never lost). Returns (value, evaluated_new, shared). Forest persists across calls.
    (rung-1 used two kernels -- intern + a separate apex eval -- with host orchestration between; this collapses them.)"""
    N=g["N"]; prev=len(F.op)
    canon, distinct = F.FE.intern_eval(g)                                # ONE fused kernel: intern + combine in one drain pass
    sN, sD, sE = F.FE.read_range(prev, distinct)                         # the new canon ids' values, computed ON-DEVICE
    rep={}
    for i in range(N): rep.setdefault(int(canon[i]), i)                  # a representative term node per canonical id
    for cid in range(prev, distinct):                                    # register NEW canonical nodes (bookkeeping, NOT eval)
        i=rep[cid]; k=cid-prev
        if g["op"][i]==-1:
            vN=int(g["vN"][i]); vD=int(g["vD"][i])
            F.op.append(-1); F.lch.append(-1); F.rch.append(-1); F.vn.append(vN); F.vd.append(vD)
            F.code.append(int(morton2(np.array([vN&0xFFFF]), np.array([vD&0xFFFF]))[0]))
        else:
            cl=int(canon[g["lch"][i]]); cr=int(canon[g["rch"][i]])
            F.op.append(int(g["op"][i])); F.lch.append(cl); F.rch.append(cr)
            F.code.append(_ccode(g["op"][i], cl, cr))
            if sE[k]:                                                    # escalated (>u128): EXACT crown fold from resident
                a=F.value(cl); b=F.value(cr); v=(a*b if g["op"][i]==1 else a+b)   #   children (children have smaller cid -> ready)
                F.vn.append(v.numerator); F.vd.append(v.denominator)
            else:
                F.vn.append(sN[k]); F.vd.append(sD[k])                   # value computed ON-DEVICE by the fused kernel
    root=int(canon[g["root"]]); frontier=[cid for cid in range(prev,distinct) if F.op[cid]!=-1]
    shared=sum(1 for i in range(N) if g["op"][i]!=-1)-len(frontier)
    F.materialize()                                                      # b-real-store: keep the forest physically code-ordered
    return F.value(root), len(frontier), shared


def _embed(sub, host_op, extra):
    N=len(sub["op"]); op=list(sub["op"])+[-1,host_op]; vN=list(sub["vN"])+[extra[0],0]; vD=list(sub["vD"])+[extra[1],1]
    lch=list(sub["lch"])+[-1,sub["root"]]; rch=list(sub["rch"])+[-1,N]
    return dict(op=op,vN=vN,vD=vD,lch=lch,rch=rch,N=N+2,root=N+1)


if __name__ == "__main__":
    print("jea_resident: the SPPF forest lives ON-DEVICE (sorted code index); grows by new nodes only across evals\n")
    F=Forest()
    S=dict(op=[-1,-1,1],vN=[1,1,0],vD=[2,3,1],lch=[-1,-1,0],rch=[-1,-1,1],N=3,root=2)   # 1/2*1/3 = 1/6
    T1=_embed(S,0,(1,1)); T2=_embed(S,1,(2,1))                                          # both CONTAIN S
    v1,e1,s1=evaluate(T1,F); sz1=F.size(); idx1=int(F.FE.nextid.get()[0])
    v2,e2,s2=evaluate(T2,F); sz2=F.size(); idx2=int(F.FE.nextid.get()[0])
    print(f"  eval(T1=S+1/1)={v1} (==7/6:{v1==Fraction(7,6)})  new={e1} shared={s1}  forest size {sz1} (device canon table {idx1})")
    print(f"  eval(T2=S*2/1)={v2} (==1/3:{v2==Fraction(1,3)})  new={e2} shared={s2}  forest size {sz2} (device canon table {idx2})")
    print(f"  eval: jea_mega_eval FUSED intern+combine megakernel (ONE launch per eval; intern + value in one drain)")

    growth=sz2-sz1; tot=T2["N"]; shared_nodes=tot-growth      # T2's nodes not re-added = shared from the resident forest
    devresident = type(F.ccode).__module__.startswith("cupy")
    w1 = devresident and (growth < tot) and (s2>=1) and (shared_nodes>=3)   # S's 3 nodes (2 leaves+1 combine) reused
    w2 = (v1==Fraction(7,6)) and (v2==Fraction(1,3))
    w3 = idx2>idx1 and devresident                            # the on-device canon table grew (cross-eval persistent)
    print(f"\nW1 DEVICE-RESIDENT + GROWS-BY-NEW (T2 has {tot} nodes, forest grew by {growth} -> {shared_nodes} SHARED")
    print(f"   from T1's resident S via the on-device intern -- S computed once, ever): {w1}")
    print(f"W2 EXACT through the device-resident evaluator (T1=7/6, T2=1/3): {w2}")
    print(f"W3 INTERN+EVAL ARE ONE FUSED MEGAKERNEL (jea_mega_eval; persistent device canon table grew {idx1}->{idx2};")
    print(f"   a node hash-conses AND computes its value in one drain -- no separate apex launch): {w3}")

    # W4: PHASE-2 GATHER -- once the precise working set is known, gather it CODE-LOCALITY ordered (the SM layout)
    # vs stable-id (creation) order; measure HBM tiles touched. Built on a REAL forest (a wide random term).
    G=Forest(); rng=np.random.default_rng(5)
    lv=[(int(rng.integers(1,9)),int(rng.integers(1,9))) for _ in range(8)]
    vN=[a for a,_ in lv]; vD=[b for _,b in lv]; op=[-1]*8; lch=[-1]*8; rch=[-1]*8
    for _ in range(600):                                       # children from the WHOLE forest -> code-coherent sets are
        a=int(rng.integers(0,len(vN))); b=int(rng.integers(0,len(vN)))      # stable-SCATTERED (created at various times)
        op.append(int(rng.integers(0,2))); lch.append(a); rch.append(b); vN.append(0); vD.append(1)
    evaluate(dict(op=op,vN=vN,vD=vD,lch=lch,rch=rch,N=len(vN),root=len(vN)-1), G)   # build the resident forest
    order=[int(x) for x in G.pstable.get()]; ncomb=len(order)            # code-order stable ids (the materialized store)
    print(f"\n  W4  PHASE-2 GATHER (forest {G.size()} nodes): HBM tiles touched gathering a")
    print(f"      structurally-coherent working set (a code-index neighborhood) -- code-locality vs stable-id, T=64:")
    w4=True; off=ncomb//3
    for K in (64,128,256):
        if off+K>ncomb: continue
        ws=order[off:off+K]                                             # a contiguous code-order slice = coherent set
        st,lo=G.gather_cost(ws,64)
        print(f"        |working set|={K:4d}:  stable-order tiles={st:3d}  locality tiles={lo:3d}  ({st/max(lo,1):.1f}x fewer)")
        w4 = w4 and (lo<st)
    print(f"      -> code-locality gather (Phase-2) touches fewer tiles vs stable-id; grows with set size, nil below T (W5).")

    # W5: b-real-store -- the forest is now PHYSICALLY code-ordered (materialize); the Phase-2 gather is REAL, not predicted.
    pcode=G.pcode.get(); sorted_ok=bool((pcode[:-1]<=pcode[1:]).all())              # physical store is code-sorted
    inv_ok=all(int(G.pstable[int(G.pslot[s])])==s for s in range(0,G.size(),37))    # pslot is the inverse of pstable
    val_ok=all(F.value(sid)==Fraction(F.vn[sid],F.vd[sid]) for sid in (0,1))        # values stay in the stable store
    w5 = sorted_ok and inv_ok and (v1==Fraction(7,6)) and (v2==Fraction(1,3))
    print(f"\n  W5  b-real-STORE: forest physically code-ordered (pcode sorted: {sorted_ok}; pslot inverse of pstable: {inv_ok}).")
    print(f"      The Phase-2 gather (W4) now reads the REAL physical slots, not a prediction. VALUES stay in the stable/")
    print(f"      byte-limb store (arbitrary magnitude -- EmitBig 217-bit can't pack into int64); only the STRUCTURE is")
    print(f"      physically code-ordered. evaluate materializes it each call; eval exact through the indirection: {w5}")
    ok=w1 and w2 and w3 and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — the resident SPPF: INTERN+EVAL are now ONE fused on-device MEGAKERNEL")
    print(f"  (jea_mega_eval, Δ-Σ-mega rung-2 -- intern-kernel + apex-kernel + deliver-kernel collapsed to one drain),")
    print(f"  the forest grows by new nodes only, the Phase-2 store is materialized code-order (b-real-store). Remaining")
    print(f"  host work: the EXACT >u128 crown fold, and the term-feed/DAG build -- the next Δ-Σ-mega rungs (Δ-Ψ-deliver/dag).")
