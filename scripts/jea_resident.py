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


class Forest:
    """The device-resident SPPF: append-only stable payload + a device sorted (code -> stable id) linear quadtree."""
    def __init__(self):
        self.op=[]; self.lch=[]; self.rch=[]; self.vn=[]; self.vd=[]      # stable payload by sid (append-only)
        self.code=[]                                                     # per-node locality code (structural / value z-code)
        self.leafmap={}                                                  # (vN,vD) -> sid (leaves are few; host)
        self.ccode=cp.zeros(0,cp.int64); self.csid=cp.zeros(0,cp.int64)  # DEVICE sorted combine-code index (quadtree)

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

    def loc_slot(self, sids):                                            # Phase-2: code-order position of each combine sid
        codes=cp.asarray([self.code[s] for s in sids],cp.int64)          # (via the EXISTING Phase-1 code index, DEVICE)
        return cp.searchsorted(self.ccode, codes).get()

    def gather_cost(self, sids, T):                                      # HBM tiles touched gathering a working set:
        stable=len({int(s)//T for s in sids})                           #   stable-id (creation) order  vs
        loc=len({int(p)//T for p in self.loc_slot(sids)})               #   code-locality order (the Phase-2 gather)
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
    """Intern g into the device-resident forest F (share via searchsorted / add+merge per height), evaluate ONLY
    the new frontier on the apex, store values. Returns (value, evaluated_new, shared). Forest persists across calls."""
    from jea_apex_deliver import run_apex_u128, deliver_subtree           # lazy: keep module-import light (no apex pull)
    N=g["N"]; ht=heights(g); H=int(ht.max()) if N else 0; nid=[0]*N; frontier=[]
    F._pc=[]; F._ps=[]
    for h in range(H+1):
        idx=[i for i in range(N) if ht[i]==h]
        if h==0:
            for i in idx: nid[i]=F.leaf(int(g["vN"][i]), int(g["vD"][i]))
            continue
        codes=[_ccode(g["op"][i], nid[g["lch"][i]], nid[g["rch"][i]]) for i in idx]
        sids=F.lookup(codes)                                             # DEVICE sharing-lookup
        for j,i in enumerate(idx):
            if sids[j]>=0: nid[i]=int(sids[j])                           # SHARE the resident node (referenced)
            else:
                s=F.add_combine(codes[j], int(g["op"][i]), nid[g["lch"][i]], nid[g["rch"][i]]); nid[i]=s; frontier.append(s)
        F.merge()                                                        # DEVICE merge the new combines into the index
    root=nid[g["root"]]; shared=sum(1 for i in range(N) if g["op"][i]!=-1)-len(frontier)
    if frontier:
        fset=set(frontier); children=set()
        for s in frontier: children.add(F.lch[s]); children.add(F.rch[s])
        resident=[s for s in children if s not in fset]                  # the WORKING SET gathered from the forest
        resident.sort(key=lambda s: F.code[s])                           # Phase-2: gather in CODE-LOCALITY order (leaves
        local = resident + sorted(fset)                                  #   are order-free; frontier stays topo by sid)
        li={s:j for j,s in enumerate(local)}
        op2=[]; vN2=[]; vD2=[]; lch2=[]; rch2=[]
        for s in local:
            if s in fset: op2.append(F.op[s]); vN2.append(0); vD2.append(1); lch2.append(li[F.lch[s]]); rch2.append(li[F.rch[s]])
            else: v=F.value(s); op2.append(-1); vN2.append(v.numerator); vD2.append(v.denominator); lch2.append(-1); rch2.append(-1)
        g2=dict(op=op2,vN=vN2,vD=vD2,lch=lch2,rch=rch2,N=len(local),root=li[root])
        val,err,nodes=run_apex_u128(g2, return_nodes=True)
        if err==2: val,_=deliver_subtree(g2, nodes["vN"], nodes["vD"], escal=nodes["escal"])
        for s in local:                                                  # store new-node values (crown -> exact host fold)
            if s not in fset: continue
            j=li[s]
            if nodes["escal"][j]==0 and nodes["vD"][j]:
                F.vn[s]=int(nodes["vN"][j]); F.vd[s]=int(nodes["vD"][j])
            else:
                a=F.value(F.lch[s]); b=F.value(F.rch[s]); v=(a*b if F.op[s]==1 else a+b); F.vn[s]=v.numerator; F.vd[s]=v.denominator
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
    v1,e1,s1=evaluate(T1,F); sz1=F.size(); idx1=int(F.ccode.size)
    v2,e2,s2=evaluate(T2,F); sz2=F.size(); idx2=int(F.ccode.size)
    print(f"  eval(T1=S+1/1)={v1} (==7/6:{v1==Fraction(7,6)})  new={e1} shared={s1}  forest size {sz1} (device index {idx1})")
    print(f"  eval(T2=S*2/1)={v2} (==1/3:{v2==Fraction(1,3)})  new={e2} shared={s2}  forest size {sz2} (device index {idx2})")
    print(f"  device index type: {type(F.ccode).__module__}.{type(F.ccode).__name__} (cupy = on-device); searchsorted lookup")

    growth=sz2-sz1; tot=T2["N"]; shared_nodes=tot-growth      # T2's nodes not re-added = shared from the resident forest
    devresident = type(F.ccode).__module__.startswith("cupy")
    w1 = devresident and (growth < tot) and (s2>=1) and (shared_nodes>=3)   # S's 3 nodes (2 leaves+1 combine) reused
    w2 = (v1==Fraction(7,6)) and (v2==Fraction(1,3))
    w3 = idx2>idx1 and devresident                            # the device sorted index grew via searchsorted+merge
    print(f"\nW1 DEVICE-RESIDENT + GROWS-BY-NEW (cupy index; T2 has {tot} nodes, forest grew by {growth} -> {shared_nodes}")
    print(f"   SHARED from T1's resident S via the device searchsorted lookup -- S computed once, ever): {w1}")
    print(f"W2 EXACT through the device-resident evaluator (T1=7/6, T2=1/3): {w2}")
    print(f"W3 SHARING IS A DEVICE LOOKUP (cp.searchsorted into the sorted z-code index + device merge; index {idx1}->{idx2}): {w3}")

    # W4: PHASE-2 GATHER -- once the precise working set is known, gather it CODE-LOCALITY ordered (the SM layout)
    # vs stable-id (creation) order; measure HBM tiles touched. Built on a REAL forest (a wide random term).
    G=Forest(); rng=np.random.default_rng(5)
    lv=[(int(rng.integers(1,9)),int(rng.integers(1,9))) for _ in range(8)]
    vN=[a for a,_ in lv]; vD=[b for _,b in lv]; op=[-1]*8; lch=[-1]*8; rch=[-1]*8
    for _ in range(600):                                       # children from the WHOLE forest -> code-coherent sets are
        a=int(rng.integers(0,len(vN))); b=int(rng.integers(0,len(vN)))      # stable-SCATTERED (created at various times)
        op.append(int(rng.integers(0,2))); lch.append(a); rch.append(b); vN.append(0); vD.append(1)
    evaluate(dict(op=op,vN=vN,vD=vD,lch=lch,rch=rch,N=len(vN),root=len(vN)-1), G)   # build the resident forest
    ncomb=int(G.csid.size); csid=[int(x) for x in G.csid.get()]          # code-order stable ids (the linear quadtree)
    print(f"\n  W4  PHASE-2 GATHER (forest {G.size()} nodes, {ncomb} combines): HBM tiles touched gathering a")
    print(f"      structurally-coherent working set (a code-index neighborhood) -- code-locality vs stable-id, T=64:")
    w4=True; off=ncomb//3
    for K in (64,128,256):
        if off+K>ncomb: continue
        ws=csid[off:off+K]                                              # a contiguous code-order slice = coherent set
        st,lo=G.gather_cost(ws,64)
        print(f"        |working set|={K:4d}:  stable-order tiles={st:3d}  locality tiles={lo:3d}  ({st/max(lo,1):.1f}x fewer)")
        w4 = w4 and (lo<st)
    print(f"      -> code-locality gather (Phase-2, via the Phase-1 index) touches <= tiles vs stable-id; the benefit")
    print(f"         grows with working-set size and is nil below the SM-tile (W5). Wired: evaluate gathers resident")
    print(f"         children in code order. (Full benefit needs payload physically code-ordered -- storage step.)")
    ok=w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — the resident SPPF is a cupy sorted z-code index (a linear quadtree): sharing")
    print(f"  is cp.searchsorted (device), growth is a device merge, the forest persists + grows by new nodes only. The")
    print(f"  per-height orchestration is still host; the full on-device form folds intern+eval into one megakernel.")
