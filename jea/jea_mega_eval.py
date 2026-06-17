#!/usr/bin/env python3
"""jea_mega_eval.py — Δ-Σ-mega rung-2 (AI-Δ9): FUSE the two megakernels into ONE. The intern (jea_mega hash-cons)
and the combine (apex u128 carrier) run in a SINGLE drain pass: a node, when its children are ready, hash-conses
its key; if it is a NEW canonical node it COMPUTES its value once (u64/u128 carrier, predict-place); if SHARED it
REUSES the resident value. Memoization fused into evaluation -- the charter's "on-GPU resident memoizing trace,"
one kernel. (rung-1 had intern + eval as two separate kernels with host bookkeeping between; this collapses them.)

Value store is CANON-indexed (each distinct sub-term computed ONCE). Escalation (>u128, or a child escalated) is
FLAGGED per canon id (err=3, cescal) for the host byte-limb crown deliver -- folding that on-device is a later rung.
No in-warp spin: a found-but-unpublished slot/value retries next sweep (the apex's productivity drain).

Witnesses ([W], __main__):
1. EXACT, FUSED: one kernel interns+combines a term to the TRUE rational (== host Fraction), on the u128 carrier.
2. MEMOIZED (computed once): distinct canon nodes << term nodes on a sharing term; the value store is canon-indexed.
3. CROSS-EVAL: a repeated term re-evaluates with 0 new canon nodes (persistent hash table + value store).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_core
import jea_zsppf as Z
import jea_mega as MEGA                                                  # rung-1 intern (cross-checked: fused partition == hash intern)
_U128 = 1<<128

_SRC = jea_core.Q128_CUDA + r'''
__device__ __forceinline__ int bitlen128(u128 v){
  u64 hi=(u64)(v>>64), lo=(u64)v; if(hi) return 128-__clzll(hi); if(lo) return 64-__clzll(lo); return 0; }
extern "C" __global__ void mega_eval(
    const int* op, const int* lch, const int* rch, const unsigned long long* leafkey,
    const u64* lNlo, const u64* lNhi, const u64* lDlo, const u64* lDhi,            // leaf values (per node; leaves only)
    int* canon, int* nready, volatile int* pending, int N,
    unsigned long long* htkey, volatile int* htval, int HCAP, int* nextid,
    u64* cNlo, u64* cNhi, u64* cDlo, u64* cDhi, int* cbln, int* cbld, int* cescal, volatile int* cready,  // CANON value store
    long long abound, volatile int* err)
{
  int gid=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x; long long sw=0;
  while(*pending>0){
    if(sw++>=abound){ *err=1; break; }
    for(int i=gid;i<N;i+=stride){
      if(nready[i]) continue;
      int isleaf=(op[i]==-1); int cl=0,cr=0; unsigned long long key;
      if(isleaf){ key=leafkey[i]; }
      else { int L=lch[i],R=rch[i]; if(!nready[L]||!nready[R]) continue; cl=canon[L]; cr=canon[R];
             key=((unsigned long long)(op[i]+1)<<62)|((unsigned long long)(unsigned)cl<<31)|(unsigned)cr; }
      unsigned long long hh=key*0x9E3779B97F4A7C15ULL; unsigned slot=(unsigned)(hh>>33)%HCAP;
      int cid=-1, mine=0;
      for(int p=0;p<HCAP;p++){ unsigned s=(slot+p)%HCAP;
        unsigned long long cur=atomicCAS(&htkey[s],0ULL,key);
        if(cur==0ULL){ cid=atomicAdd(nextid,1); htval[s]=cid; __threadfence(); mine=1; break; }
        if(cur==key){ int v=htval[s]; if(v<0) cid=-2; else cid=v; break; } }
      if(cid==-2) continue;                                   // slot found, id not published -> retry
      if(cid<0){ *err=2; break; }                             // table full
      if(mine){                                               // WE created cid -> compute the value ONCE
        if(isleaf){ cNlo[cid]=lNlo[i];cNhi[cid]=lNhi[i];cDlo[cid]=lDlo[i];cDhi[cid]=lDhi[i];
                    cbln[cid]=bitlen128(ld(cNlo,cNhi,cid)); cbld[cid]=bitlen128(ld(cDlo,cDhi,cid)); cescal[cid]=0; }
        else {
          int o=op[i];
          if(cescal[cl]||cescal[cr]){ cescal[cid]=1; *err=3; cNlo[cid]=0;cNhi[cid]=0;cDlo[cid]=1;cDhi[cid]=0;cbln[cid]=0;cbld[cid]=1; }
          else {
            int bn=(o==1)?(cbln[cl]+cbln[cr]):(max(cbln[cl]+cbld[cr],cbln[cr]+cbld[cl])+1); int bd=cbld[cl]+cbld[cr];
            if(bn>128||bd>128){ cescal[cid]=1; *err=3; cNlo[cid]=0;cNhi[cid]=0;cDlo[cid]=1;cDhi[cid]=0;cbln[cid]=0;cbld[cid]=1; }
            else if(bn<=64&&bd<=64){ u64 nl=cNlo[cl],dl=cDlo[cl],nr=cNlo[cr],dr=cDlo[cr];
              u64 na=(o==1)?(nl*nr):(nl*dr+nr*dl), D=dl*dr; u64 a=na,b=D; while(b){u64 r=a%b;a=b;b=r;} u64 gg=a?a:1ULL;
              na/=gg; D/=gg; cNlo[cid]=na;cNhi[cid]=0;cDlo[cid]=D;cDhi[cid]=0;
              cbln[cid]=na?(64-__clzll(na)):0; cbld[cid]=D?(64-__clzll(D)):0; cescal[cid]=0; }
            else { u128 nl=ld(cNlo,cNhi,cl),dl=ld(cDlo,cDhi,cl),nr=ld(cNlo,cNhi,cr),dr=ld(cDlo,cDhi,cr);
              u128 na=(o==1)?(nl*nr):(nl*dr+nr*dl), D=dl*dr; u128 a=na,b=D; while(b){u128 r=a%b;a=b;b=r;} u128 gg=a?a:(u128)1;
              na/=gg; D/=gg; st(cNlo,cNhi,cid,na); st(cDlo,cDhi,cid,D); cbln[cid]=bitlen128(na); cbld[cid]=bitlen128(D); cescal[cid]=0; }
          }
        }
        __threadfence(); cready[cid]=1;
      } else { if(!cready[cid]) continue; }                   // shared cid, value not published -> retry
      canon[i]=cid; __threadfence(); nready[i]=1; atomicSub((int*)pending,1);
    }
    __threadfence();
  }
}
'''
assert _SRC.isascii(), "kernel source must be ASCII"
_k = cp.RawKernel(_SRC, "mega_eval", options=("--device-int128",))
_NSM = cp.cuda.Device().attributes["MultiProcessorCount"]; _BLK,_THR = 8*_NSM, 128
_M = (1<<64)-1


class Fused:
    """Persistent fused intern+eval: one device hash table + one canon-indexed value store (cross-eval memoizing)."""
    def __init__(self, HCAP=1<<16, CAP=1<<16):
        self.HCAP=HCAP; self.CAP=CAP
        self.htkey=cp.zeros(HCAP,cp.uint64); self.htval=cp.full(HCAP,-1,cp.int32); self.nextid=cp.zeros(1,cp.int32)
        z=lambda: cp.zeros(CAP,cp.uint64)
        self.cNlo,self.cNhi,self.cDlo,self.cDhi=z(),z(),z(),z()
        self.cbln=cp.zeros(CAP,cp.int32); self.cbld=cp.zeros(CAP,cp.int32)
        self.cescal=cp.zeros(CAP,cp.int32); self.cready=cp.zeros(CAP,cp.int32); self.leafcodes={}

    def _launch(self, dop, dl, dr, dlk, dNlo, dNhi, dDlo, dDhi, N):
        """Run the fused kernel on DEVICE arrays. Returns (canon DEVICE array, distinct). The shared launch core for
        the host-fed path (intern_eval) and the on-device DAG-gen path (intern_eval_dev -- the term never round-trips)."""
        canon=cp.full(N,-1,cp.int32); nready=cp.zeros(N,cp.int32); pend=cp.full(1,N,cp.int32); err=cp.zeros(1,cp.int32)
        abound = max(8_000_000, 64 * N)                              # runaway BACKSTOP only (err=1) -- the drain TERMINATES by
        _k((_BLK,),(_THR,),(dop,dl,dr,dlk,dNlo,dNhi,dDlo,dDhi,        # productivity (every sweep makes progress); this just
                            canon,nready,pend,np.int32(N),self.htkey,self.htval,np.int32(self.HCAP),self.nextid,  # caps a hypothetical
                            self.cNlo,self.cNhi,self.cDlo,self.cDhi,self.cbln,self.cbld,self.cescal,self.cready,  # bug, scaled to N
                            np.int64(abound),err))
        cp.cuda.Stream.null.synchronize()
        e=int(err.get()[0])
        if e in (1,2): raise RuntimeError(f"mega_eval err={e} (1=productivity bound, 2=table full -- raise HCAP/CAP)")
        return canon, int(self.nextid.get()[0])

    def intern_eval(self, g):
        """Fused intern+combine in ONE kernel (HOST-fed term). Returns (canon per node, distinct). The CANON-indexed
        value store (cNlo/cNhi/cDlo/cDhi, cescal) persists on the device -- read new ids with read_range. (err=3 = some
        node escalated >u128 -> flagged in cescal for the host byte-limb crown fold; that fold is exact, never lost.)"""
        N=g["N"]; lk=np.zeros(N,np.uint64); lNlo=np.zeros(N,np.uint64); lNhi=np.zeros(N,np.uint64)
        lDlo=np.zeros(N,np.uint64); lDhi=np.zeros(N,np.uint64)
        for i in range(N):
            if g["op"][i]==-1:
                vN=int(g["vN"][i]); vD=int(g["vD"][i])
                assert 0<=vN<_U128 and 0<vD<_U128, "fused kernel: leaf value must be non-negative and fit u128 (leaf escalation is a later rung)"
                key=(vN,vD); c=self.leafcodes.setdefault(key,len(self.leafcodes)+1)
                lk[i]=(np.uint64(3)<<np.uint64(62))|np.uint64(c)
                lNlo[i]=vN & _M; lNhi[i]=vN>>64; lDlo[i]=vD & _M; lDhi[i]=vD>>64
        d=lambda a,t: cp.asarray(a,t)
        canon,distinct=self._launch(d(g["op"],cp.int32),d(g["lch"],cp.int32),d(g["rch"],cp.int32),
                                    cp.asarray(lk),cp.asarray(lNlo),cp.asarray(lNhi),cp.asarray(lDlo),cp.asarray(lDhi),N)
        return [int(x) for x in canon.get()], distinct

    def intern_eval_dev(self, dop, dl, dr, dlk, dNlo, dNhi, dDlo, dDhi, N):
        """Δ-Ψ-dag: fused intern+combine on a DEVICE-GENERATED term -- the op/lch/rch/leaf arrays are built on-device
        from the generator parameters (jea_dag_gen), NEVER constructed on the host nor uploaded. Returns (canon DEVICE
        array, distinct); the canon stays on device so the caller can do O(distinct) bookkeeping via cp.unique."""
        return self._launch(dop, dl, dr, dlk, dNlo, dNhi, dDlo, dDhi, N)

    def read_range(self, lo, hi):
        """Read the canon value store for ids [lo,hi): host (vN, vD, escal) lists. Escalated ids (>u128) carry a
        placeholder (the host folds those from resident children -- exact). One device->host copy of the slice."""
        if hi<=lo: return [], [], []
        nlo=self.cNlo[lo:hi].get(); nhi=self.cNhi[lo:hi].get(); dlo=self.cDlo[lo:hi].get(); dhi=self.cDhi[lo:hi].get()
        esc=self.cescal[lo:hi].get(); n=hi-lo
        vN=[(int(nhi[k])<<64)|int(nlo[k]) for k in range(n)]; vD=[(int(dhi[k])<<64)|int(dlo[k]) for k in range(n)]
        return vN, vD, [int(x) for x in esc]

    def eval(self, g):
        """Standalone: fused intern+combine, then read the root. Returns (root Fraction or None-if-escalated, distinct, esc)."""
        canon, distinct = self.intern_eval(g); rc=canon[g["root"]]
        if int(self.cescal.get()[rc])==1: return None, distinct, True           # escalated (>u128) -> host crown fold
        rn=(int(self.cNhi.get()[rc])<<64)|int(self.cNlo.get()[rc]); rd=(int(self.cDhi.get()[rc])<<64)|int(self.cDlo.get()[rc])
        return Fraction(rn,rd), distinct, False


if __name__ == "__main__":
    print("jea_mega_eval: Δ-Σ-mega rung-2 -- INTERN + COMBINE fused into ONE kernel (memoized eval, one pass)\n")
    from jea_generator_dag import build_dag
    terms=[("E_q(8) 1/1-tree", Z.build_Eq(8)),
           ("rung-b DAG", dict(vN=[1,2,1,1,2,1,0,0,0],vD=[2,3,6,6,4,2,1,1,1],op=[-1,-1,-1,-1,-1,-1,1,0,0],
                               lch=[-1,-1,-1,-1,-1,-1,0,2,6],rch=[-1,-1,-1,-1,-1,-1,1,3,7],N=9,root=8)),
           ("build_dag(256,6) 66-bit", build_dag(256,6))]
    def truth(g):
        v=[None]*g["N"]
        for i in range(g["N"]):
            if g["op"][i]==-1: v[i]=Fraction(int(g["vN"][i]),int(g["vD"][i]))
            elif g["op"][i]==1: v[i]=v[g["lch"][i]]*v[g["rch"][i]]
            else: v[i]=v[g["lch"][i]]+v[g["rch"][i]]
        return v[g["root"]]
    allok=True
    for name,g in terms:
        F=Fused(); val,distinct,esc=F.eval(g); t=truth(g); ok=(val==t)
        allok&=ok
        print(f"  {name:<26} fused-eval -> {str(val)[:36]} == truth {str(t)[:36]}: {ok}  (distinct {distinct}/{g['N']} nodes)")

    # cross-eval: repeat a term -> 0 new canon nodes (persistent table + value store)
    F=Fused(); _,d1,_=F.eval(terms[1][1]); _,d2,_=F.eval(terms[1][1])
    cross=(d2==d1)
    print(f"\n  cross-eval (persistent fused state): eval(term) -> {d1} distinct; eval AGAIN -> {d2} (0 new -- memoized): {cross}")

    eq=Z.build_Eq(12); Feq=Fused(); veq,deq,_=Feq.eval(eq)
    memo=(veq==Fraction(1<<12,1)) and (deq < eq["N"])
    print(f"  memoized: E_q(12) {eq['N']} nodes -> {deq} distinct (computed ONCE each), value {veq} == 2^12: {memo}")

    # W4 the fused INTERN half == rung-1's standalone hash-cons intern (jea_mega): same dedup PARTITION (the fused
    # kernel's intern is the rung-1 hash-cons + a value compute -- the dedup is unchanged). Keeps rung-1 consumed.
    def part(canon):
        from collections import defaultdict; d=defaultdict(list)
        for i,c in enumerate(canon): d[int(c)].append(i)
        return set(frozenset(v) for v in d.values())
    samepart=True
    for _,g in terms:
        fcanon,fd=Fused().intern_eval(g); hcanon,hd=MEGA.DeviceInterner().intern(g)
        samepart &= (part(fcanon)==part(hcanon)) and (fd==hd)

    w1=allok; w2=memo; w3=cross; w4=samepart
    print(f"\n  W4 fused-intern partition == rung-1 hash-cons intern (jea_mega) partition (dedup unchanged): {w4}")
    print(f"\nW1 EXACT, FUSED (one kernel interns+combines to the true rational on the u128 carrier): {w1}")
    print(f"W2 MEMOIZED (distinct << nodes; each distinct sub-term computed ONCE; canon-indexed value store): {w2}")
    print(f"W3 CROSS-EVAL (persistent hash table + value store -> a repeated term adds 0 new canon nodes): {w3}")
    print(f"W4 DEDUP UNCHANGED (the fused intern partition == the rung-1 standalone hash-cons intern partition): {w4}")
    ok=w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-mega rung-2: intern + combine are ONE kernel. A node hash-conses and, if")
    print(f"  new, computes its value once (u64/u128, predict-place); shared nodes reuse. Two megakernels collapsed to")
    print(f"  one (the per-eval host bookkeeping between them is gone). Escalation (>u128) is flagged for the host crown")
    print(f"  fold (exact, never lost) -- folding the byte-limb crown + the term-feed on-device are the next rungs.")
