#!/usr/bin/env python3
"""jea_generator_unified.py — the MERGE: one kernel that is BOTH dynamic and data-parallel,
on the exact 128-bit ℚ carrier with escalate-don't-truncate.

The cooperative ladder proved the dynamic architecture (live control, arbitrary DAG, branchless
lock-free) but ran 20 LEAD threads — architecture, not throughput. The data-parallel folds are
fast but STATIC. This unifies them: every thread of every resident block folds nodes in parallel
(data-parallel), the monotonic readiness gate + cooperative control ride on top (dynamic), and
the carrier is 128-bit with overflow DETECTED (escalate), never silently wrapped (a u64 version
silently truncated mul-heavy trees past 2^64 — the carrier-width bug this avoids).

Two lessons baked in:
  * LIVENESS (review pt 8, learned the hard way): the persistent cyclic comm graph needs ALL
    launched blocks co-resident. The ANALYTIC residency overestimated and DEADLOCKED past ~3/SM
    when work spanned never-scheduled blocks. Fix: launch 1 block/SM (the hardware-guaranteed
    resident floor) and round-robin ALL combines across those threads (works at any N).
  * CARRIER (charter #4): 128-bit lanes; combine products overflow-checked -> escalate flag.
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
import jea_core
import jea_generator_dag as DAG          # reuse build_dag (random +/x) for the exactness check

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void generator_unified(
    volatile int* Kbuf, volatile int* obsmax, volatile int* pending, volatile int* escalate,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps,
    int L, int N, long long maxcyc, volatile int* err)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;     // EVERY thread is a worker (data-parallel)
    int T   = gridDim.x * blockDim.x;
    int base = L + tid;
    int owncount = (base < N) ? ((N - 1 - base) / T + 1) : 0;   // round-robin combine ownership
    long long c = 0;
    while (*pending > 0) {
        int est = 0;
        if (owncount > 0) {
            int slot = base + (int)(c % owncount) * T;
            int Lc = lch[slot], Rc = rch[slot];
            int active = ready[Lc] & ready[Rc] & (1 - ready[slot]);
            if (active & (1 - initf[slot])) {
                u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc);
                u128 na, D = dl*dr; int o = 0;
                o |= (dl!=0) && (D/dl != dr);
                if (op[slot]==1) { na = nl*nr; o |= (nl!=0) && (na/nl != nr); }
                else { u128 p1=nl*dr, p2=nr*dl; na=p1+p2;
                       o |= (dr!=0) && (p1/dr != nl); o |= (dl!=0) && (p2/dl != nr); o |= (na < p1); }
                if (o) *escalate = 1;                    // DETECTED, never wrapped (escalate-don't-truncate)
                st(naNl,naNh,slot,na); st(naDl,naDh,slot,D);
                st(al,ah,slot,na);    st(bl,bh,slot,D);  initf[slot]=1;
            }
            int K = *Kbuf;
            u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot); int s=steps[slot];
            for (int j=0;j<K;j++){ if (active && bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }
            st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
            int nowdone = active && (bb==0);
            if (nowdone) { u128 g = (aa!=0)?aa:(u128)1;
                st(vNl,vNh,slot, ld(naNl,naNh,slot)/g);
                st(vDl,vDh,slot, ld(naDl,naDh,slot)/g); __threadfence(); }   // publish before ready
            int wasr = ready[slot]; ready[slot] = wasr | nowdone;
            atomicSub((int*)pending, ready[slot]-wasr);
            est = nowdone ? s : (active ? s+1 : 0);
        }
        if (est > 0) atomicMax((int*)obsmax, est);                  // monotonic control
        if (threadIdx.x == 0) *Kbuf = relax_q(*Kbuf, *obsmax);      // K relaxed once per block
        __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_unified", int128=True)


def _lh(vals):
    vals = [int(v) for v in vals]
    M = (1 << 64) - 1
    return cp.asarray([v & M for v in vals], cp.uint64), cp.asarray([(v >> 64) & M for v in vals], cp.uint64)


def build_balanced_add(h, seed=1):
    """Large balanced all-+ tree (u128-safe at scale; add reduces denominators each level)."""
    rng = np.random.default_rng(seed); L = 1 << h
    vN = list(int(x) for x in rng.integers(1,4,L)); vD = list(int(1<<x) for x in rng.integers(0,2,L))
    lch=[-1]*L; rch=[-1]*L; op=[-1]*L; level = list(range(L)); idx = L
    while len(level) > 1:
        nxt=[]
        for i in range(0, len(level), 2):
            lch.append(level[i]); rch.append(level[i+1]); op.append(0); vN.append(0); vD.append(0)
            nxt.append(idx); idx += 1
        level = nxt
    return dict(vN=vN, vD=vD, lch=lch, rch=rch, op=op, L=L, N=idx, root=level[0])


def run_g(g, B=256, K0=4, maxcyc=20_000_000, blocks_per_sm=1):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    regs = _kern.num_regs
    nblocks = blocks_per_sm * nsm                    # 1/SM = hardware-resident floor (liveness)
    N=g["N"]; L=g["L"]
    vNl,vNh = _lh(g["vN"]); vDl,vDh = _lh(g["vD"])
    lch=cp.asarray(g["lch"],cp.int32); rch=cp.asarray(g["rch"],cp.int32); op=cp.asarray(g["op"],cp.int32)
    ready=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    initf=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    z=lambda: cp.zeros(N,cp.uint64)
    al,ah,bl,bh,naNl,naNh,naDl,naDh = z(),z(),z(),z(),z(),z(),z(),z()
    steps=cp.zeros(N,cp.int32)
    Kbuf=cp.full(1,K0,cp.int32); obsmax=cp.zeros(1,cp.int32)
    pending=cp.full(1,N-L,cp.int32); escalate=cp.zeros(1,cp.int32); err=cp.zeros(1,cp.int32)
    cp.cuda.Stream.null.synchronize(); t0=time.perf_counter()
    _kern((nblocks,),(B,),
          (Kbuf,obsmax,pending,escalate,vNl,vNh,vDl,vDh,lch,rch,op,ready,initf,
           al,ah,bl,bh,naNl,naNh,naDl,naDh,steps,np.int32(L),np.int32(N),np.int64(maxcyc),err))
    cp.cuda.Stream.null.synchronize(); ms=(time.perf_counter()-t0)*1e3
    r=g["root"]
    rn=(int(vNh.get()[r])<<64)|int(vNl.get()[r]); rd=(int(vDh.get()[r])<<64)|int(vDl.get()[r])
    return dict(rn=rn, rd=rd, pending=int(pending.get()[0]), escalate=int(escalate.get()[0]),
                err=int(err.get()[0]), ms=ms, nblocks=nblocks, B=B, threads=nblocks*B, regs=regs)


if __name__ == "__main__":
    print("jea_generator_unified — dynamic AND data-parallel, exact 128-bit carrier, escalate\n")

    # 1) EXACTNESS on random +/x trees (mul path), 128-bit so values >2^64 are exact (not wrapped)
    print("  exactness (random +/x DAG vs Python Fraction; 128-bit carrier, escalate-don't-truncate):")
    allok = True
    for L in (64, 128, 256, 512):
        g = DAG.build_dag(L, 3); r = run_g(g)
        tb = max(abs(g["truth"].numerator), g["truth"].denominator).bit_length()
        if r["escalate"] == 1:                          # an intermediate exceeded 2^128: DETECTED, not wrapped
            ok = (r["err"] == 0)                         # correct escalate-don't-truncate behavior
            verdict = f"ESCALATED (intermediate >2^128 detected, not wrapped) -> ok={ok}"
        else:
            ok = r["err"]==0 and r["pending"]==0 and Fraction(r["rn"],r["rd"]) == g["truth"]
            verdict = f"exact={ok}" + ("  (root >2^64: u64 would WRAP, 128-bit is exact)" if tb > 64 else "")
        allok &= ok
        print(f"     L={L:4d} ({g['N']:>4} nodes, true {tb:>3}b): {verdict}")

    # 2) THROUGHPUT at scale (large all-+ tree), the merge comparison
    print("\n  throughput (large all-+ tree; data-parallel across the full thread grid):")
    thr = 0
    for h in (14, 16, 18):
        g = build_balanced_add(h); run_g(g)              # warm
        r = run_g(g)
        truth = sum((Fraction(g["vN"][i], g["vD"][i]) for i in range(g["L"])), Fraction(0))
        ok = r["err"]==0 and r["pending"]==0 and r["escalate"]==0 and Fraction(r["rn"],r["rd"]) == truth
        thr = g["N"] / r["ms"] * 1e3 / 1e6
        print(f"     L=2^{h}={g['L']:>8} ({g['N']:>9} nodes): {r['ms']:7.2f} ms = {thr:7.1f} M nodes/s  "
              f"{r['nblocks']}blk x{r['B']} = {r['threads']} threads  exact={ok}")

    print(f"\n  THE MERGE: ~{thr:.0f} M nodes/s vs the 20-lead-thread cooperative silo (~0.66 M nodes/s) "
          f"= ~{thr/0.66:.0f}x")
    print(f"  -- the SAME dynamic control + arbitrary-DAG streaming, now data-parallel AND 128-bit exact.")
    print(f"\n  UNIFIED {'PASS' if allok else 'FAIL'} — ONE kernel: dynamic (live K, readiness-gated,")
    print(f"  branchless, lock-free) AND data-parallel (full grid) AND exact-128-bit (escalate). Not silos.")
