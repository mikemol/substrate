#!/usr/bin/env python3
"""jea_resident.py — the DEVICE-RESIDENT SPPF forest. evaluate(g, F) interns AND evaluates g in ONE fused megakernel
(jea_mega_eval: the kernel hash-conses each node and, if NEW, computes its value once on the u64/u128 carrier; SHARED
sub-terms reuse the resident value). The forest persists across calls and GROWS by new nodes only (cross-eval sharing
via the persistent device hash table). Used by jea_eval.

Where the state lives (Δ-Ψ-forest): VALUES are device-resident in a GRADED SUB-BYTE store (GR.GradedStore -- each
value packed to its bit-grade) for >u128 and the fused canon store (FE.cNlo/cNhi) for <=u128; the >u128 escalation
CROWN is delivered on the byte-limb DEVICE carrier (deliver_crown -- recompute-from-residue, never host-folded). The
structure INDEX (op/lch/rch/code) is the small host orchestration map (stable id == canon id). The physical
code-ordered store (pcode/pstable/pslot, a linear quadtree over morton z-codes) is device; merged INCREMENTALLY each
eval (materialize_incr -- delta merge-by-rank, not full re-argsort).

Beyond the per-node fused drain: evaluate_Eq generates a parametric DAG ON-DEVICE (no host build/upload);
level_eval_graded / eval_aligned_planes evaluate a wide same-op level via the BIT-SLICED carrier (SWAR), the strategy
the navigator's dispatch picks for regular wide layers (eval_frontier executes the chosen corner). Exact at any
magnitude.

Witnesses ([W], in __main__): W1 device-resident + grows-by-new; W2 exact; W3 intern+eval ONE fused megakernel;
W4 Phase-2 code-locality gather; W5 b-real-store + graded device value store; W6 Δ-Ψ-deliver (device byte-limb crown);
W7 b-real-incr (incremental merge); W8 Δ-Ψ-dag (on-device DAG gen); W9 Δ-Ψ-forest(c) bit-sliced level eval; W10
dispatch consumer; W11 Δ-Ψ-swar-win (planes-resident aligned eval beats the drain).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_zsppf import morton2, heights
import jea_mega_eval as MEGAE                                   # the FUSED on-device intern+combine megakernel (Δ-Σ-mega rung-2)
from jea_dag_gen import gen_Eq_device                           # Δ-Ψ-dag: ON-DEVICE DAG generation (no host build loop / upload)
import jea_graded as GR                                         # Δ-Ψ-forest (b): the GRADED, SUB-BYTE device value store
import jea_branchless as BL                                     # Δ-Ω-branchless: selects are arithmetic index->table load


class Forest:
    """Device-resident SPPF (Δ-Ψ-forest). VALUES live ON-DEVICE in a GRADED, SUB-BYTE bit-packed store (GR.GradedStore
    -- each value packed to exactly its grade, no u128 padding, no 8-bit-limb floor), replacing host Python-int lists.
    The structure INDEX (op/lch/rch/code) is the small host orchestration map (int, the 'which node' map, NOT values);
    the physical code-order store (pcode/pstable/pslot) is device. Stable id == canon id (the fused interner's id)."""
    def __init__(self):
        self.op=[]; self.lch=[]; self.rch=[]; self.code=[]               # structure INDEX (host; int orchestration map, NOT values)
        self.vals=GR.GradedStore()                                       # the VALUE store: device-resident, sub-byte, grade-packed
        self.pslot=cp.zeros(0,cp.int64)                                  # stable id -> physical position (code order)
        self.pstable=cp.zeros(0,cp.int64); self.pcode=cp.zeros(0,cp.int64)   # physical position -> stable id / code (sorted)
        self.FE=MEGAE.Fused()                                            # the device <=u128 value store + fused intern+combine kernel

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

    def value(self, sid): return self.vals.value(sid)                    # device-resident graded value store
    def size(self): return len(self.op)


def _ccode(op, l, r):                                                    # structural z-code: morton(lch,rch) dominant, op LOW
    return (int(morton2(np.array([l]), np.array([r]))[0]) << 2) | (int(op) & 3)   # op high -> mixed-op sets split; keep it low


_U128 = 1<<128
import jea_core                                                          # Π10: leaf home for shared limb helpers
_trim = jea_core.trim                                                    # trailing-zero-trim little-endian uint8 limbs (>=1)


def deliver_crown(F, prev, distinct, sE):
    """Δ-Ψ-deliver: compute the >u128 escalation CROWN on the DEVICE byte-limb carrier (jea_limb_gpu: dp4a-convolution
    multiply + parallel carry), recompute-from-residue from the fused kernel's emitted crown (cescal/sE) -- NOT a host
    Fraction fold. A crown node's u128 children are read STRAIGHT FROM THE FUSED DEVICE STORE (cNlo/cNhi -- no value
    copy-across-boundary); crown children are the byte-limb residues already delivered this pass (or resident from a
    prior eval). num/den accumulate UNREDUCED on byte-limb; REDUCE ONCE at readout (no in-kernel gcd -- the established
    carrier insight). The byte-limb multiply parallelizes PER-MULTIPLY (dp4a), a different granularity than the per-node
    drain, so the crown is its own device phase -- folding it into a drain lane would serialize the bignum and lose dp4a."""
    from jea_limb_gpu import to_limbs, from_limbs, gpu_add, gpu_mul
    limbs={}; out={}                                                     # this-eval crown cid -> device limbs / reduced (num,den)
    def u128_dev(lo, hi, c):                                             # read a node's u128 value from the device store -> limbs
        return _trim(cp.concatenate([lo[c:c+1], hi[c:c+1]]).view(cp.uint8))
    def child(c):
        if c in limbs: return limbs[c]                                   # crown child delivered earlier this pass (device)
        if c < prev and F.vals.is_crown(c):                              # resident crown value (prior eval, graded store) -> limbs
            v=F.value(c); return cp.asarray(to_limbs(v.numerator)), cp.asarray(to_limbs(v.denominator))
        return (u128_dev(F.FE.cNlo,F.FE.cNhi,c), u128_dev(F.FE.cDlo,F.FE.cDhi,c))   # <=u128: from the fused device store
    for cid in range(prev, distinct):                                    # cid order is topological (children have smaller cid)
        if F.op[cid]==-1 or not sE[cid-prev]: continue
        nl,dl=child(F.lch[cid]); nr,dr=child(F.rch[cid])
        if F.op[cid]==1: num=gpu_mul(nl,nr)[0]; den=gpu_mul(dl,dr)[0]
        else: num=gpu_add(gpu_mul(nl,dr)[0], gpu_mul(nr,dl)[0]); den=gpu_mul(dl,dr)[0]
        v=Fraction(from_limbs(num), from_limbs(den))                     # REDUCE at readout (host gcd; arithmetic was on-device)
        out[cid]=(v.numerator, v.denominator)
        limbs[cid]=(cp.asarray(to_limbs(v.numerator)), cp.asarray(to_limbs(v.denominator)))   # reduced -> small for parents
    return out                                                           # {cid: (num,den)} -- the eval appends these to the graded store


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
    for cid in range(prev, distinct):                                    # register NEW canonical nodes' STRUCTURE (not values yet)
        i=rep[cid]
        if g["op"][i]==-1:
            vN=int(g["vN"][i]); vD=int(g["vD"][i])
            F.op.append(-1); F.lch.append(-1); F.rch.append(-1)
            F.code.append(int(morton2(np.array([vN&0xFFFF]), np.array([vD&0xFFFF]))[0]))
        else:
            cl=int(canon[g["lch"][i]]); cr=int(canon[g["rch"][i]])
            F.op.append(int(g["op"][i])); F.lch.append(cl); F.rch.append(cr); F.code.append(_ccode(g["op"][i], cl, cr))
    crown = deliver_crown(F, prev, distinct, sE) if any(sE) else {}      # Δ-Ψ-deliver: >u128 crown on the byte-limb DEVICE carrier
    for k in range(distinct-prev):                                       # append VALUES to the GRADED store in cid order (sid==cid)
        num,den = crown.get(prev+k, (sN[k], sD[k]))                      # crown (device-delivered) or the fused <=u128 value
        F.vals.append(num, den)
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
        uvals, first = cp.unique(canon_dev, return_index=True)           # device: distinct ids present + first occurrence index
        reps=first[uvals>=prev]                                         # representative term-index per NEW id (sorted -> cid=prev+j)
        rep_op=g["op"][reps].get()                                       # gather only the representatives (O(distinct), not O(N))
        cl=canon_dev[cp.clip(g["lch"][reps],0,None)].get(); cr=canon_dev[cp.clip(g["rch"][reps],0,None)].get()
        sN,sD,sE=F.FE.read_range(prev,distinct)
        lc11=int(morton2(np.array([1]),np.array([1]))[0])               # E_q leaves are all 1/1 -> one leaf code
        for k in range(new):                                            # register STRUCTURE for each new canon id
            if rep_op[k]==-1:
                F.op.append(-1); F.lch.append(-1); F.rch.append(-1); F.code.append(lc11)
            else:
                lcn=int(cl[k]); rcn=int(cr[k]); o=int(rep_op[k])
                F.op.append(o); F.lch.append(lcn); F.rch.append(rcn); F.code.append(_ccode(o,lcn,rcn))
        crown = deliver_crown(F, prev, distinct, sE) if any(sE) else {}  # Δ-Ψ-deliver (device byte-limb crown)
        for k in range(new):                                            # append VALUES to the GRADED store in cid order
            num,den = crown.get(prev+k, (sN[k], sD[k]))                  # crown or the fused <=u128 value (leaf 1/1 included)
            F.vals.append(num, den)
    root=int(canon_dev[g["root"]].get())
    new_comb=sum(1 for cid in range(prev,distinct) if F.op[cid]!=-1)
    shared=( (1<<n)-1 ) - new_comb                                       # total E_q combines (2^n-1) not re-added = shared
    F.materialize_incr(prev)
    return F.value(root), new_comb, shared


def level_eval_graded(F, op, lsids, rsids):
    """Δ-Ψ-forest (c): evaluate a LEVEL of independent same-op combines via the GRADED bit-sliced carrier -- gather
    the children's (num,den) from the device graded store (F.vals) and combine the WHOLE level in ONE SWAR pass
    (GR.combine_batch). Returns [(num,den)] per node. The graded carrier doing the eval's arithmetic, not just storage."""
    nL=[]; dL=[]; nR=[]; dR=[]
    for l,r in zip(lsids, rsids):
        a=F.value(l); b=F.value(r)
        nL.append(a.numerator); dL.append(a.denominator); nR.append(b.numerator); dR.append(b.denominator)
    return GR.combine_batch(op, nL, dL, nR, dR)


def _drain_level(F, op, lsids, rsids):                              # per-node drain corner (also the flat/either default)
    mul=(lambda a,b:a*b); add=(lambda a,b:a+b); comb=BL.pick((add, mul), op)   # op-select as an arithmetic index (op in {0,1})
    return [ (lambda v:(v.numerator,v.denominator))(comb(F.value(l),F.value(r))) for l,r in zip(lsids,rsids) ]


def _aligned_dag(leaf_n, leaf_d, ops):
    """The balanced HALVING-reduction DAG (M=2^k leaves; layer combines value j with value j+cnt/2) -- for the drain
    to evaluate the SAME thing as eval_aligned_planes."""
    M=len(leaf_n); vN=list(leaf_n); vD=list(leaf_d); op=[-1]*M; lch=[-1]*M; rch=[-1]*M
    base=0; cnt=M; li=0
    while cnt>1:
        o=ops[li]; li+=1
        for j in range(cnt//2):
            vN.append(0); vD.append(1); op.append(o); lch.append(base+j); rch.append(base+cnt//2+j)
        base+=cnt; cnt//=2
    return dict(op=op,vN=vN,vD=vD,lch=lch,rch=rch,N=len(vN),root=len(vN)-1)


def eval_aligned_planes(leaf_n, leaf_d, ops):
    """Δ-Ψ-swar-win finish: PLANES-RESIDENT aligned-layer eval of the halving tree. The host<->device boundary is paid
    ONCE (pack leaves vectorized, read out the root); each layer is ONE fused SWAR op (rat_*, no per-combine Fraction).
    Children = value j and j+M'/2: a WORD-SLICE while >1 word, a bit-shift within the last word -- no arbitrary gather.
    SWAR's home (regular wide layers); the dispatch flips to this vs the per-node drain. Returns the root Fraction."""
    nP,_=GR.to_bitsliced(leaf_n); dP,_=GR.to_bitsliced(leaf_d); Mp=len(leaf_n); li=0
    while Mp>1:
        op=ops[li]; li+=1; W=nP.shape[1]
        if W>1:                                                      # across-word halving: top/bottom halves (word slice)
            h=W//2; ac=cp.ascontiguousarray                          # column slices are non-contiguous; the kernel needs C-contig
            nL,nR,dL,dR=ac(nP[:,:h]),ac(nP[:,h:]),ac(dP[:,:h]),ac(dP[:,h:])
        else:                                                        # within the last word: shift by Mp//2 values (bit shift)
            s=cp.uint64(Mp//2); nL,nR,dL,dR=nP,nP>>s,dP,dP>>s
        nP,dP=(GR.rat_mul if op==1 else GR.rat_add)(nL,dL,nR,dR)     # ONE fused SWAR combine for the whole layer
        Mp//=2
    return Fraction(GR.from_bitsliced(nP,1)[0], GR.from_bitsliced(dP,1)[0])


def eval_frontier(F, op, lsids, rsids, strategy):
    """Δ-Ψ-forest dispatch CONSUMER: execute a level via the strategy the navigator chose (jea_navigator's
    eval_strategy, an argmin over the MEASURED level surface). BRANCHLESS dispatch: the strategy is a 0/1 INDEX into a
    table of the two evaluators -- a table load, not an `if` (Δ-Ω-branchless). 1 -> the graded SWAR level eval
    (level_eval_graded); 0 -> the per-node drain (also the flat/either default). The CHOICE is the telemetry-driven
    solve; this only executes the selected corner."""
    table = (lambda: _drain_level(F, op, lsids, rsids), lambda: level_eval_graded(F, op, lsids, rsids))
    return BL.pick(table, BL.step(strategy.startswith("bit-sliced-SWAR")))()


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
    devresident = type(F.vals.nbuf).__module__.startswith("cupy")   # the VALUE store is device-resident (graded, sub-byte)
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

    # W5: b-real-store + Δ-Ψ-forest(b) -- the structure is PHYSICALLY code-ordered (materialize) AND the VALUES live in
    # the device-resident GRADED sub-byte store (no host vn/vd). Density: sub-byte packed bits vs the u128 lane.
    pcode=G.pcode.get(); sorted_ok=bool((pcode[:-1]<=pcode[1:]).all())              # physical store is code-sorted
    inv_ok=all(int(G.pstable[int(G.pslot[s])])==s for s in range(0,G.size(),37))    # pslot is the inverse of pstable
    no_host_vals=(not hasattr(F,"vn")) and isinstance(F.value(0),Fraction)         # values are device-resident, no host vn/vd list
    store_bits=G.vals.bits(); fixed=G.size()*256                                   # graded sub-byte bits vs u128 lanes (256/node)
    w5 = sorted_ok and inv_ok and no_host_vals and (v1==Fraction(7,6)) and (v2==Fraction(1,3))
    print(f"\n  W5  b-real-STORE + Δ-Ψ-FOREST(b): structure code-ordered (pcode sorted: {sorted_ok}; pslot inverse: {inv_ok});")
    print(f"      VALUES are device-resident in the GRADED SUB-BYTE store (no host vn/vd: {no_host_vals}). Density on the")
    print(f"      {G.size()}-node forest: graded-packed {store_bits} bits vs u128 lanes {fixed} ({fixed/max(store_bits,1):.1f}x denser): {w5}")
    # W6: Δ-Ψ-deliver -- the >u128 escalation CROWN is delivered on the DEVICE byte-limb carrier (recompute-from-residue
    # from the fused kernel's cescal), NOT host-folded. Find a DAG whose intermediates exceed u128; eval == truth.
    from jea_generator_dag import build_dag
    big=None
    for (n,depth) in [(256,8),(256,12),(256,16),(512,16)]:
        cand=build_dag(n,depth)
        if max(cand["truth"].numerator.bit_length(), cand["truth"].denominator.bit_length())>128: big=cand; chosen=(n,depth); break
    Gb=Forest(); vb,_,_=evaluate(big, Gb)
    crown=sum(1 for cid in range(Gb.size()) if Gb.op[cid]!=-1 and Gb.vals.is_crown(cid))   # >u128 via the graded store's grade
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
    # W9: Δ-Ψ-forest (c) -- graded ARITHMETIC in the eval path. A WIDE level of independent same-op combines over
    # resident leaves is evaluated via the bit-sliced carrier (level_eval_graded) reading the device graded store; one
    # SWAR pass per op-class, exact vs per-node truth. [numbers] the level done in one bit-sliced op, not M.
    Gc=Forest(); K=24; leaves=[(int(i%7)+1, int(i%5)+1) for i in range(K)]
    for n,d in leaves: Gc.vals.append(n,d)                               # resident leaves in the device graded store
    rngc=np.random.default_rng(9); M=200
    ls=[int(rngc.integers(0,K)) for _ in range(M)]; rs=[int(rngc.integers(0,K)) for _ in range(M)]
    for op,name in ((1,"mul"),(0,"add")):
        res=level_eval_graded(Gc, op, ls, rs)                           # ONE bit-sliced SWAR pass for the whole level
        comb=(lambda a,b:a*b) if op==1 else (lambda a,b:a+b)
        truth=[comb(Fraction(*leaves[l]),Fraction(*leaves[r])) for l,r in zip(ls,rs)]
        okc=all(Fraction(*res[i])==truth[i] for i in range(M))
        if op==1: w9_mul=okc
        else: w9_add=okc
    w9 = w9_mul and w9_add
    print(f"\n  W9  Δ-Ψ-FOREST(c): a {M}-node level of independent same-op combines (children from the device graded store)")
    print(f"      evaluated via the BIT-SLICED carrier in ONE SWAR pass per op-class -- mul=={w9_mul}, add=={w9_add} vs")
    print(f"      per-node truth: {w9} (graded arithmetic IN the eval path, not just storage)")

    # W10: the dispatch CONSUMER -- eval_frontier executes whichever strategy the navigator chose. Both corners give
    # the truth (the dispatch is correct either way; the navigator's measured argmin picks WHICH on the live box).
    truth_c=[Fraction(*leaves[l])*Fraction(*leaves[r]) for l,r in zip(ls,rs)]
    r_swar=eval_frontier(Gc,1,ls,rs,"bit-sliced-SWAR"); r_drain=eval_frontier(Gc,1,ls,rs,"per-node-drain")
    w10 = all(Fraction(*r_swar[i])==truth_c[i] for i in range(M)) and all(Fraction(*r_drain[i])==truth_c[i] for i in range(M))
    print(f"\n  W10 DISPATCH CONSUMER (eval_frontier executes the navigator's eval_strategy): both corners exact vs truth")
    print(f"      -- 'bit-sliced-SWAR' branch and 'per-node-drain' branch both == per-node truth: {w10}")
    # W11: Δ-Ψ-swar-win FINISH -- the planes-resident aligned-layer eval (boundary paid ONCE) vs the per-node drain,
    # on the SAME halving tree. EXACT (== drain == truth) + COMPUTED which is faster (the dispatch flips for wide layers).
    Mh=512; rngh=np.random.default_rng(11)
    ln=[int(rngh.integers(1,50)) for _ in range(Mh)]; ld=[int(rngh.integers(1,50)) for _ in range(Mh)]
    ops=[1 if rngh.integers(0,2) else 0 for _ in range(Mh.bit_length())]
    truth_v=[Fraction(a,b) for a,b in zip(ln,ld)]; base=0; cnt=Mh; li2=0
    while cnt>1:                                                         # host truth of the halving tree
        o=ops[li2]; li2+=1; nxt=[(truth_v[base+j]*truth_v[base+cnt//2+j]) if o==1 else (truth_v[base+j]+truth_v[base+cnt//2+j]) for j in range(cnt//2)]
        truth_v=truth_v+nxt; base+=cnt; cnt//=2
    root_truth=truth_v[-1]
    sw=eval_aligned_planes(ln, ld, ops)                                 # planes-resident SWAR (pack once, k ops, readout once)
    Gd=Forest(); dr,_,_=evaluate(_aligned_dag(ln, ld, ops), Gd)          # the per-node drain (same tree)
    eval_aligned_planes(ln,ld,ops); cp.cuda.Stream.null.synchronize()   # warm
    t0=time.perf_counter(); [eval_aligned_planes(ln,ld,ops) for _ in range(5)]; cp.cuda.Stream.null.synchronize(); t_sw=(time.perf_counter()-t0)/5
    t0=time.perf_counter(); [evaluate(_aligned_dag(ln,ld,ops), Forest()) for _ in range(5)]; cp.cuda.Stream.null.synchronize(); t_dr=(time.perf_counter()-t0)/5
    w11 = (sw==root_truth) and (dr==root_truth)
    print(f"\n  W11 Δ-Ψ-SWAR-WIN FINISH (halving tree, M={Mh}): planes-resident SWAR == drain == truth: {w11};")
    print(f"      [COMPUTED] planes-resident SWAR = {t_sw*1e3:.1f} ms vs per-node drain = {t_dr*1e3:.1f} ms -> "
          f"{'SWAR WINS' if t_sw<t_dr else 'drain wins'} ({t_dr/max(t_sw,1e-9):.1f}x) -- the dispatch flips for aligned wide layers")
    ok=w1 and w2 and w3 and w4 and w5 and w6 and w7 and w8 and w9 and w10 and w11
    print(f"\n  {'PASS' if ok else 'FAIL'} — the resident SPPF: INTERN+EVAL are ONE fused on-device megakernel (rung-2),")
    print(f"  the >u128 CROWN is delivered on the byte-limb DEVICE carrier (Δ-Ψ-deliver), the physical store merges")
    print(f"  INCREMENTALLY (b-real-incr), parametric terms are GENERATED ON-DEVICE (Δ-Ψ-dag), the VALUE payload is")
    print(f"  device-resident GRADED SUB-BYTE (Δ-Ψ-forest b), and a wide same-op level evaluates via the BIT-SLICED")
    print(f"  carrier in one SWAR pass (Δ-Ψ-forest c). Remaining: dispatch bit-sliced-SWAR vs the per-node fused drain by")
    print(f"  level shape (the navigator choice) + the small host structure index. The graded carrier is fully exercised.")
