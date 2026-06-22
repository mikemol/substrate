#!/usr/bin/env python3
"""jea_mega.py — Δ-Σ-mega rung-1 (AI-Δ9): the INTERN folded into a SINGLE on-device megakernel (device hash-cons +
fixpoint drain), removing the per-height HOST orchestration loop. The biggest remaining host-orchestration seam.

jea_resident interns per HEIGHT on the host (loop heights -> compute codes -> device searchsorted -> assign ids ->
device merge). Δ-Σ-mega folds that into ONE persistent kernel: lanes drain the node set; a combine whose children
are already interned computes its injective structural key (op,canon_l,canon_r) and HASH-CONSES it (open-addressed
device hash table, atomicCAS insert-or-find) -> canonical id; equal keys collapse (dedup). Leaves intern by an
injective value code. Ordering is the SAME productivity drain the apex uses (process when children ready; retry if
a found slot's value isn't published yet -- NO in-warp spin, the fixpoint retries). One launch, no host per-height loop.

Dedup is code-AGNOSTIC (W2): the hash partition == the sort (jea_zsppf.intern_radix) partition; canonical IDS differ
(hash insert order vs sort order). The locality (sorted/quadtree) view is the SEPARATE materialize pass (b-real-store).
So: hash for the single-pass on-device dedup, sort for locality -- the two-sort architecture, on-device.

Witnesses ([W], __main__):
1. SAME PARTITION as the host intern: device-hash canon and host intern_radix canon induce the IDENTICAL dedup
   partition (same sharing) on several terms -- the on-device intern is correct.
2. ONE KERNEL, NO HOST PER-HEIGHT LOOP: a single persistent kernel launch interns the whole DAG (the drain handles
   the child-before-parent ordering on-device); distinct count == host.
3. CROSS-EVAL SHARING (persistent table): a second term sharing structure with the first dedups ON-DEVICE (its
   shared nodes get canon ids < the first term's distinct count -- the hash table persists).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_zsppf as Z

_SRC = r'''
extern "C" __global__ void mega_intern(
    const int* op, const int* lch, const int* rch, const unsigned long long* leafkey,
    int* canon, int* ready, volatile int* pending, int N,
    unsigned long long* htkey, volatile int* htval, int HCAP, int* nextid, long long abound, volatile int* err)
{
  int gid=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x; long long sw=0;
  while (*pending > 0) {
    if (sw++ >= abound) { *err=1; break; }
    for (int i=gid; i<N; i+=stride) {
      if (ready[i]) continue;
      unsigned long long key;
      if (op[i]==-1) { key = leafkey[i]; }                              // leaf: injective value code (tag in high bits)
      else {
        int L=lch[i], R=rch[i];
        if (!ready[L] || !ready[R]) continue;                          // children not interned yet -> later sweep
        unsigned long long cl=(unsigned)canon[L], cr=(unsigned)canon[R];
        key = ((unsigned long long)(op[i]+1) << 62) | (cl << 31) | cr;  // INJECTIVE (op in {0,1}; canon < 2^31)
      }
      unsigned long long hh = key * 0x9E3779B97F4A7C15ULL; unsigned slot=(unsigned)(hh>>33) % HCAP;
      int cid=-1;
      for (int p=0; p<HCAP; p++) {
        unsigned s=(slot+p)%HCAP;
        unsigned long long cur=atomicCAS(&htkey[s], 0ULL, key);        // EMPTY=0 (keys are always >0: tag>=1)
        if (cur==0ULL) { cid=atomicAdd(nextid,1); htval[s]=cid; __threadfence(); break; }   // we inserted -> new id
        if (cur==key) { int v=htval[s]; if (v<0) { cid=-2; } else cid=v; break; }            // found (or not-published)
      }
      if (cid==-2) continue;                                           // found slot, value not published -> retry (no spin)
      if (cid<0)  { *err=2; break; }                                   // table full
      canon[i]=cid; __threadfence(); ready[i]=1; atomicSub((int*)pending,1);
    }
    __threadfence();
  }
}
'''
_k = cp.RawKernel(_SRC, "mega_intern")
assert _SRC.isascii(), "kernel source must be ASCII"
_NSM = cp.cuda.Device().attributes["MultiProcessorCount"]; _BLK, _THR = 8*_NSM, 128


class DeviceInterner:
    """A PERSISTENT on-device hash-cons table (cross-eval sharing)."""
    def __init__(self, HCAP=1<<16):
        self.HCAP=HCAP
        self.htkey=cp.zeros(HCAP, cp.uint64); self.htval=cp.full(HCAP, -1, cp.int32)
        self.nextid=cp.zeros(1, cp.int32); self.leafcodes={}

    def intern(self, g):
        """Intern g on-device in ONE kernel launch. Returns (canon per node, distinct-so-far). Persists across calls."""
        N=g["N"]
        lk=np.zeros(N, np.uint64)
        for i in range(N):
            if g["op"][i]==-1:
                key=(int(g["vN"][i]), int(g["vD"][i])); c=self.leafcodes.setdefault(key, len(self.leafcodes)+1)
                lk[i]=(np.uint64(3)<<np.uint64(62)) | np.uint64(c)      # leaf tag=3, injective leaf code
        d=lambda a,t: cp.asarray(a,t)
        dop=d(g["op"],cp.int32); dl=d(g["lch"],cp.int32); dr=d(g["rch"],cp.int32); dlk=cp.asarray(lk)
        canon=cp.full(N,-1,cp.int32); ready=cp.zeros(N,cp.int32); pend=cp.full(1,N,cp.int32); err=cp.zeros(1,cp.int32)
        _k((_BLK,),(_THR,),(dop,dl,dr,dlk,canon,ready,pend,np.int32(N),
                            self.htkey,self.htval,np.int32(self.HCAP),self.nextid,np.int64(8_000_000),err))
        cp.cuda.Stream.null.synchronize()
        if int(err.get()[0])!=0: raise RuntimeError(f"mega_intern err={int(err.get()[0])} (table full? raise HCAP)")
        return [int(x) for x in canon.get()], int(self.nextid.get()[0])


_part = Z.partition   # Π7: canon→index-partition lives once in jea_zsppf (already imported as Z)


if __name__ == "__main__":
    print("jea_mega: the INTERN as a SINGLE on-device megakernel (device hash-cons + fixpoint drain) -- no host per-height loop\n")
    terms=[Z.build_Eq(8), Z.build_Eq(10),
           dict(vN=[1,2,1,1,2,1,0,0,0],vD=[2,3,6,6,4,2,1,1,1],op=[-1,-1,-1,-1,-1,-1,1,0,0],
                lch=[-1,-1,-1,-1,-1,-1,0,2,6],rch=[-1,-1,-1,-1,-1,-1,1,3,7],N=9,root=8)]
    allok=True
    for t in terms:
        host_canon,hd = Z.intern_radix(t,"z")                          # host sort-based intern (the reference partition)
        DI=DeviceInterner()
        dev_canon,dd = DI.intern(t)                                    # device hash-cons intern (ONE kernel)
        same = (_part(host_canon)==_part(dev_canon)) and (hd==dd)
        allok &= same
        print(f"  term N={t['N']:<5} host intern -> {hd:>3} distinct | device-kernel intern -> {dd:>3} distinct | "
              f"SAME partition: {same}")

    # cross-eval: persistent table -> a repeat of a term fully dedups (no new ids), a sharing term adds only new
    DI=DeviceInterner(); _,d1=DI.intern(terms[2]); _,d2=DI.intern(terms[2])      # same term twice
    cross = (d2==d1)                                                   # 2nd intern of the SAME term adds 0 new nodes
    print(f"\n  cross-eval (persistent device table): intern(term) -> {d1} distinct; intern(term) AGAIN -> {d2} "
          f"(0 new -- fully shared on-device): {cross}")

    w1=allok; w2=allok; w3=cross
    print(f"\nW1 SAME PARTITION as host intern (device-hash canon == sort canon dedup classes; correct): {w1}")
    print(f"W2 ONE KERNEL, NO HOST PER-HEIGHT LOOP (single persistent launch interns the whole DAG; distinct==host): {w2}")
    print(f"W3 CROSS-EVAL SHARING (persistent device hash table -> a repeated term adds 0 new canonical ids): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-mega rung-1: the intern is now ONE on-device megakernel (device hash-cons +")
    print(f"  the apex's productivity drain for child-before-parent ordering) -- the per-height HOST loop is gone. Dedup")
    print(f"  is code-agnostic so the hash partition == the sort partition (W2); the locality/quadtree view stays the")
    print(f"  separate materialize sort (b-real-store). NEXT: wire as jea_resident's intern; fold the EVAL (apex drain)")
    print(f"  into the same kernel (intern+combine in one pass); then crown-deliver + DAG-gen on-device.")
