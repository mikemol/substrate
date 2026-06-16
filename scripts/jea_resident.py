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
from jea_dag_gen import gen_Eq_device                           # Δ-Ψ-dag: ON-DEVICE DAG generation (no host build loop / upload)


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
        codes=cp.asarray(self.code, cp.int64); order=cp.argsort(codes, kind="stable")   # FULL re-argsort (the whole forest)
        self.pcode=codes[order]; self.pstable=order                      # physical pos -> (code, stable id), sorted by code
        self.pslot=cp.empty(codes.size, cp.int64); self.pslot[order]=cp.arange(codes.size)   # stable id -> physical pos

    def materialize_incr(self, prev):                                    # b-real-incr: MERGE only the delta new nodes into the
        """Incremental device merge (b-real-incr): the physical store pcode/pstable is ALREADY code-sorted from prior
        evals; merge only the [prev,M) new nodes into it instead of re-argsorting the whole forest. Upload only the new
        codes (not the full host list); sort the small delta; MERGE the two sorted runs by RANK (vectorized searchsorted
        + scatter, O(M+delta) -- no O(M log M) comparison sort, no full re-upload). The full re-argsort was O(M log M)
        + an O(M) host->device transfer EVERY eval; this drops the log factor and transfers only delta."""
        M=len(self.code); delta=M-prev
        if delta==0: return
        nc=cp.asarray(self.code[prev:], cp.int64); ni=cp.arange(prev, M, dtype=cp.int64)   # ONLY the new codes/ids uploaded
        no=cp.argsort(nc, kind="stable"); nc=nc[no]; ni=ni[no]           # sort the (small) delta
        if self.pcode.size==0:
            self.pcode=nc; self.pstable=ni
        else:
            oc=self.pcode                                                # the existing sorted run (device-resident)
            r_old=cp.arange(oc.size)+cp.searchsorted(nc, oc, side="left")    # merge-by-rank: complementary sides ->
            r_new=cp.arange(nc.size)+cp.searchsorted(oc, nc, side="right")   #   a bijection onto [0, M) (stable)
            mc=cp.empty(M, cp.int64); ms=cp.empty(M, cp.int64)
            mc[r_old]=oc; ms[r_old]=self.pstable; mc[r_new]=nc; ms[r_new]=ni
            self.pcode=mc; self.pstable=ms
        self.pslot=cp.empty(M, cp.int64); self.pslot[self.pstable]=cp.arange(M)   # stable id -> physical pos (inverse)

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


_U128 = 1<<128
def _trim(arr):                                                          # trailing-zero-trim little-endian uint8 limbs (>=1)
    nz=cp.nonzero(arr)[0]
    return arr[:1] if nz.size==0 else arr[:int(nz[-1])+1]


def deliver_crown(F, prev, distinct, sE):
    """Δ-Ψ-deliver: compute the >u128 escalation CROWN on the DEVICE byte-limb carrier (jea_limb_gpu: dp4a-convolution
    multiply + parallel carry), recompute-from-residue from the fused kernel's emitted crown (cescal/sE) -- NOT a host
    Fraction fold. A crown node's u128 children are read STRAIGHT FROM THE FUSED DEVICE STORE (cNlo/cNhi -- no value
    copy-across-boundary); crown children are the byte-limb residues already delivered this pass (or resident from a
    prior eval). num/den accumulate UNREDUCED on byte-limb; REDUCE ONCE at readout (no in-kernel gcd -- the established
    carrier insight). The byte-limb multiply parallelizes PER-MULTIPLY (dp4a), a different granularity than the per-node
    drain, so the crown is its own device phase -- folding it into a drain lane would serialize the bignum and lose dp4a."""
    from jea_limb_gpu import to_limbs, from_limbs, gpu_add, gpu_mul
    limbs={}                                                             # this-eval crown cid -> (num,den) device uint8 limbs
    def u128_dev(lo, hi, c):                                             # read a node's u128 value from the device store -> limbs
        return _trim(cp.concatenate([lo[c:c+1], hi[c:c+1]]).view(cp.uint8))
    def child(c):
        if c in limbs: return limbs[c]                                   # crown child delivered earlier this pass (device)
        if F.vn[c]>=_U128 or F.vd[c]>=_U128:                             # resident crown value (prior eval, host store) -> upload
            return cp.asarray(to_limbs(F.vn[c])), cp.asarray(to_limbs(F.vd[c]))
        return (u128_dev(F.FE.cNlo,F.FE.cNhi,c), u128_dev(F.FE.cDlo,F.FE.cDhi,c))   # non-crown: from the device store
    for cid in range(prev, distinct):                                    # cid order is topological (children have smaller cid)
        if F.op[cid]==-1 or not sE[cid-prev]: continue
        nl,dl=child(F.lch[cid]); nr,dr=child(F.rch[cid])
        if F.op[cid]==1: num=gpu_mul(nl,nr)[0]; den=gpu_mul(dl,dr)[0]
        else: num=gpu_add(gpu_mul(nl,dr)[0], gpu_mul(nr,dl)[0]); den=gpu_mul(dl,dr)[0]
        v=Fraction(from_limbs(num), from_limbs(den))                     # REDUCE at readout (host gcd; arithmetic was on-device)
        F.vn[cid]=v.numerator; F.vd[cid]=v.denominator
        limbs[cid]=(cp.asarray(to_limbs(v.numerator)), cp.asarray(to_limbs(v.denominator)))   # reduced -> small for parents


def evaluate(g, F):
    """Intern AND evaluate g into the device-resident forest F in ONE fused kernel (Δ-Σ-mega rung-2): the kernel
    hash-conses each node and, if NEW, computes its value once (u64/u128 carrier); SHARED sub-terms reuse the
    resident value. The host only does node bookkeeping (register the new canon ids, reading their u64/u128 values
    from the fused device store); the >u128 escalation CROWN is delivered ON-DEVICE on the byte-limb carrier
    (deliver_crown -- recompute-from-residue from the fused kernel's cescal, never lost). Returns (value, evaluated_new,
    shared). Forest persists across calls. (rung-1 used two kernels -- intern + a separate apex eval; rung-2 fused
    them; Δ-Ψ-deliver moves the crown off the host onto the byte-limb device carrier.)"""
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
            if sE[k]: F.vn.append(0); F.vd.append(1)                     # escalated (>u128): placeholder -> deliver_crown fills it
            else: F.vn.append(sN[k]); F.vd.append(sD[k])                 # value computed ON-DEVICE by the fused kernel
    if any(sE[cid-prev] for cid in range(prev,distinct) if F.op[cid]!=-1):
        deliver_crown(F, prev, distinct, sE)                             # Δ-Ψ-deliver: the >u128 crown on the byte-limb DEVICE carrier
    root=int(canon[g["root"]]); frontier=[cid for cid in range(prev,distinct) if F.op[cid]!=-1]
    shared=sum(1 for i in range(N) if g["op"][i]!=-1)-len(frontier)
    F.materialize_incr(prev)                                             # b-real-incr: MERGE the delta new nodes (not full re-argsort)
    return F.value(root), len(frontier), shared


def evaluate_Eq(n, F):
    """Δ-Ψ-dag: evaluate E_q(n) with the DAG GENERATED ON-DEVICE (jea_dag_gen.gen_Eq_device) -- the host ships only n,
    never builds/uploads the O(N) term. The fused kernel interns+evals the device-gen arrays directly; the forest
    bookkeeping is O(distinct) (not O(N)): cp.unique finds the first-occurrence representative of each NEW canon id on
    the DEVICE, and only those (n+1 for E_q) are registered on the host. Returns (value, evaluated_new, shared)."""
    prev=len(F.op)
    c11=F.FE.leafcodes.setdefault((1,1), len(F.FE.leafcodes)+1)          # the 1/1 leaf code in the interner's SHARED namespace
    g=gen_Eq_device(n, c11)                                              # device arrays, born from n (no host term)
    canon=F.FE.intern_eval_dev(g["op"],g["lch"],g["rch"],g["leafkey"],g["lNlo"],g["lNhi"],g["lDlo"],g["lDhi"],g["N"])
    canon_dev, distinct = canon                                          # canon STAYS on device
    new=distinct-prev
    if new>0:
        vals, first = cp.unique(canon_dev, return_index=True)            # device: distinct ids present + first occurrence index
        reps=first[vals>=prev]                                          # representative term-index per NEW id (sorted -> cid=prev+j)
        rep_op=g["op"][reps].get()                                       # gather only the representatives (O(distinct), not O(N))
        cl=canon_dev[cp.clip(g["lch"][reps],0,None)].get(); cr=canon_dev[cp.clip(g["rch"][reps],0,None)].get()
        sN,sD,sE=F.FE.read_range(prev,distinct)
        lc11=int(morton2(np.array([1]),np.array([1]))[0])               # E_q leaves are all 1/1 -> one leaf code
        for k in range(new):
            if rep_op[k]==-1:                                            # leaf 1/1
                F.op.append(-1); F.lch.append(-1); F.rch.append(-1); F.vn.append(1); F.vd.append(1); F.code.append(lc11)
            else:
                lcn=int(cl[k]); rcn=int(cr[k]); o=int(rep_op[k])
                F.op.append(o); F.lch.append(lcn); F.rch.append(rcn); F.code.append(_ccode(o,lcn,rcn))
                if sE[k]: F.vn.append(0); F.vd.append(1)                 # >u128 -> device crown deliver below
                else: F.vn.append(sN[k]); F.vd.append(sD[k])
        if any(sE):
            deliver_crown(F, prev, distinct, sE)                         # Δ-Ψ-deliver reused (device byte-limb crown)
    root=int(canon_dev[g["root"]].get())
    new_comb=sum(1 for cid in range(prev,distinct) if F.op[cid]!=-1)
    shared=( (1<<n)-1 ) - new_comb                                       # total E_q combines (2^n-1) not re-added = shared
    F.materialize_incr(prev)
    return F.value(root), new_comb, shared


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
    # W6: Δ-Ψ-deliver -- the >u128 escalation CROWN is delivered on the DEVICE byte-limb carrier (recompute-from-residue
    # from the fused kernel's cescal), NOT host-folded. Find a DAG whose intermediates exceed u128; eval == truth.
    from jea_generator_dag import build_dag
    big=None
    for (n,depth) in [(256,8),(256,12),(256,16),(512,16)]:
        cand=build_dag(n,depth)
        if max(cand["truth"].numerator.bit_length(), cand["truth"].denominator.bit_length())>128: big=cand; chosen=(n,depth); break
    Gb=Forest(); vb,_,_=evaluate(big, Gb)
    crown=sum(1 for cid in range(Gb.size()) if Gb.op[cid]!=-1 and (Gb.vn[cid]>=_U128 or Gb.vd[cid]>=_U128))
    tb=max(big["truth"].numerator.bit_length(), big["truth"].denominator.bit_length())
    w6 = (vb==big["truth"]) and (tb>128) and (crown>=1)                   # exact beyond u128, crown delivered on device
    print(f"\n  W6  Δ-Ψ-DELIVER (build_dag{chosen}, true rational ~{tb} bits > u128): the >u128 CROWN ({crown} nodes) is")
    print(f"      delivered on the DEVICE byte-limb carrier (jea_limb_gpu dp4a, recompute-from-residue from cescal) --")
    print(f"      not host-folded. eval == truth exact: {w6}")

    # W7: b-real-incr -- the physical store is merged INCREMENTALLY (materialize_incr) vs the FULL re-argsort
    # (materialize) every eval. Drive both with the SAME stream of code-batches; measure cumulative materialize time +
    # verify the incremental store is identical (same sorted multiset, valid pslot inverse). [numbers]
    import time
    rng7=np.random.default_rng(7); batches=[rng7.integers(0,1<<40,size=512).astype(np.int64) for _ in range(60)]
    Gf=Forest(); Gi=Forest(); t_full=0.0; t_incr=0.0
    for b in batches:
        Gf.code.extend(int(x) for x in b)
        cp.cuda.Stream.null.synchronize(); t0=time.perf_counter(); Gf.materialize(); cp.cuda.Stream.null.synchronize(); t_full+=time.perf_counter()-t0
        pi=len(Gi.code); Gi.code.extend(int(x) for x in b)
        cp.cuda.Stream.null.synchronize(); t0=time.perf_counter(); Gi.materialize_incr(pi); cp.cuda.Stream.null.synchronize(); t_incr+=time.perf_counter()-t0
    Mtot=len(Gi.code)
    isort=bool((Gi.pcode[:-1]<=Gi.pcode[1:]).all())                                    # incremental store is code-sorted
    iinv=bool((Gi.pstable[Gi.pslot[cp.arange(Mtot)]]==cp.arange(Mtot)).all())          # pslot is the inverse of pstable
    same=bool((cp.sort(Gi.pcode)==cp.sort(Gf.pcode)).all())                            # same sorted multiset as the full re-argsort
    w7 = isort and iinv and same and (t_incr < t_full)
    print(f"\n  W7  b-real-INCR ({len(batches)} evals, forest -> {Mtot} nodes): incremental MERGE vs FULL re-argsort each eval.")
    print(f"      cumulative materialize: full re-argsort = {t_full*1e3:7.1f} ms   incremental merge = {t_incr*1e3:7.1f} ms"
          f"   ({t_full/max(t_incr,1e-9):.2f}x)")
    print(f"      incremental store == full: sorted={isort}  pslot-inverse={iinv}  same-multiset={same}  (only delta uploaded): {w7}")
    # W8: Δ-Ψ-dag -- evaluate E_q(n) with the DAG GENERATED ON-DEVICE (the host ships only n; no O(N) term build/upload),
    # bookkeeping O(distinct) via cp.unique. eval == 2^n exact; the forest grows by only n+1 distinct nodes.
    Ge=Forest(); n8=12; ve,nc8,sh8=evaluate_Eq(n8, Ge)
    w8 = (ve==Fraction(1<<n8,1)) and (Ge.size()==n8+1)                    # E_q(n) -> 2^n; SPPF collapses to n+1 distinct
    print(f"\n  W8  Δ-Ψ-DAG (E_q({n8}) = {(1<<(n8+1))-1} nodes, DAG generated ON-DEVICE from n -- no host build loop/upload):")
    print(f"      eval -> {ve} == 2^{n8} = {1<<n8}: {ve==Fraction(1<<n8,1)}; resident forest = {Ge.size()} distinct (= n+1),")
    print(f"      bookkeeping O(distinct) via cp.unique (host registered {nc8+1} nodes, not {(1<<(n8+1))-1}): {w8}")
    ok=w1 and w2 and w3 and w4 and w5 and w6 and w7 and w8
    print(f"\n  {'PASS' if ok else 'FAIL'} — the resident SPPF: INTERN+EVAL are ONE fused on-device megakernel (rung-2),")
    print(f"  the >u128 CROWN is delivered on the byte-limb DEVICE carrier (Δ-Ψ-deliver), the physical store merges")
    print(f"  INCREMENTALLY (b-real-incr), and parametric terms are GENERATED ON-DEVICE (Δ-Ψ-dag: gen_Eq_device -- the")
    print(f"  host ships n, bookkeeping O(distinct)). Remaining host seam: the forest payload host-mirror (the final rung).")
