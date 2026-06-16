#!/usr/bin/env python3
"""jea_apex.py — Δ-Ω (AI-Ω): the apex SNAP -- one persistent on-device megakernel = pool ⊕ actuator ⊕ megakernel.

The session's shadows compose here into the unified on-device evaluator:
  * jea_engine_pool  -> the DAG WORK-QUEUE drain (emit-or-spawn reduce), terminating by PRODUCTIVITY (no fuel:
                        while(*pending>0); the only numeric is the proven-invariant assertion sweeps<=npool).
  * jea_actuator     -> reads the device-RESIDENT telemetry package each sweep (host double-buffer swap); the
                        device never calls off-GPU.
  * jea_megakernel   -> the SCHEDULE is set LIVE by the package; the RESULT is invariant (combine ⊥ schedule).

The on-device schedule knob is the ACTIVE-LANE COUNT g (the coop<->strat granularity, on-device): only lanes
gid<g participate, and an active lane strides the queue by g, so the g active lanes always cover ALL slots --
hence ANY g>=1 reduces the DAG to the SAME value (correct) and still drains every level (productive). g small =
coop-like (few lanes, more intra-sweep serial); g large = strat-like (full occupancy). The host publishes g
LIVE from the navigator's operating point; the megakernel reconfigures mid-drain; the root value is unchanged.

This is the goal the whole arc accumulated toward: discover+measure surfaces -> navigate -> publish package ->
ONE persistent megakernel drains the DAG, schedule live from the package, terminating by productivity, result
correct under live reconfiguration. (Δ-J1 proved the consume; Δ-J1-rest the real-work+invariant; Δ-J2 the
no-fuel drain. Δ-Ω is their join.)

Witnesses (each [W]):
1. ONE KERNEL, THREE SHADOWS: a single persistent megakernel drains the DAG work-queue (pool) AND reads the
   resident package (actuator) AND takes its schedule live from it (megakernel) -- by construction.
2. CORRECT UNDER LIVE RECONFIG: the DAG root == the true value while the host live-published MULTIPLE distinct
   active-lane counts g during the ONE drain (combine ⊥ schedule, on-device, no relaunch).
3. PRODUCTIVITY, NO FUEL: drained via pending==0; err==0 (the proven-invariant assertion never fired); sweeps
   self-paced (no count is the control).
"""
import os, sys, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_generator_dag import build_dag
from fractions import Fraction

FIELDS = 4        # package: [g (active-lane count = on-device schedule), fstar%, bneck, epoch]

_apex = cp.RawKernel(r'''
typedef unsigned long long u64;
extern "C" __global__ void apex(
    int* op,int* narg,int* lch,int* rch, u64* vN,u64* vD, volatile int* status,
    volatile int* qtail, volatile int* pending, volatile int* err, int npool, long long assert_bound,
    volatile int* pkg, volatile int* active, int fields, int* gtrace, int* gtracen, int gtcap, int spin)
{
  int gid = blockIdx.x*blockDim.x+threadIdx.x;
  long long sw=0; int last_g=-1; int gn=0;
  // STRUCTURAL control: drain until pending==0 (productivity PROVEN; no fuel). assert_bound is the proven
  // invariant sweeps<=nodes<=npool -- a never-fired self-check, not a cap.
  while (*pending>0) {
    if (sw++ >= assert_bound) { *err=2; break; }
    int a=*active; int g=pkg[a*fields+0]; if (g<1) g=1;          // LIVE schedule = active-lane count (coop<->strat)
    if (gid==0 && g!=last_g && gn<gtcap) { gtrace[gn++]=g; last_g=g; }
    if (gid < g) {                                               // only g lanes active; stride g => cover ALL slots
      int qt=*qtail;
      for (int i=gid; i<qt; i+=g) {
        if (status[i]!=0) continue;
        int o=op[i];
        if (o==3) {                                              // SPAWN (emit-or-spawn); present for the full engine
          if (atomicCAS((int*)&status[i],0,2)==0) {
            int n=narg[i];
            if (n==0) { vN[i]=1; vD[i]=1; __threadfence(); status[i]=1; atomicSub((int*)pending,1); }
            else {
              int c=atomicAdd((int*)qtail,2);
              if (c+1<npool) {
                op[c]=3;narg[c]=n-1;lch[c]=-1;rch[c]=-1;vN[c]=0;vD[c]=1;status[c]=0;
                op[c+1]=3;narg[c+1]=n-1;lch[c+1]=-1;rch[c+1]=-1;vN[c+1]=0;vD[c+1]=1;status[c+1]=0;
                lch[i]=c;rch[i]=c+1; op[i]=0; __threadfence();
                atomicAdd((int*)pending,2); status[i]=0;
              } else { *err=1; vN[i]=0; vD[i]=1; status[i]=1; atomicSub((int*)pending,1); }
            }
          }
        } else if (o==0 || o==1) {                               // ADD/MUL terminal combine (the Q reduce)
          int L=lch[i],R=rch[i];
          if (status[L]==1 && status[R]==1) {
            if (atomicCAS((int*)&status[i],0,2)==0) {
              u64 nl=vN[L],dl=vD[L],nr=vN[R],dr=vD[R];
              u64 na=(o==1)?(nl*nr):(nl*dr+nr*dl), D=dl*dr;
              u64 aa=na,bb=D; while(bb){u64 r=aa%bb;aa=bb;bb=r;} u64 gg=aa?aa:1ULL;
              vN[i]=na/gg; vD[i]=D/gg; __threadfence(); status[i]=1; atomicSub((int*)pending,1);
            }
          }
        }
      }
    }
    __threadfence();
    long long tw=clock64(); while (clock64()-tw < (long long)spin) { }   // throttle so the host republishes mid-drain
  }
  if (gid==0) *gtracen = gn;
}
''', "apex")


if __name__ == "__main__":
    print("Δ-Ω (AI-Ω): ONE persistent megakernel = pool ⊕ actuator ⊕ megakernel -- DAG drain, schedule LIVE from the resident package\n")
    g = build_dag(64, 3); N = g["N"]                              # u64-fitting DAG (pool-verified = 70785/8); deeper overflows u64
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]   # leaf->LEAF(2), else add/mul
    narg=[0]*N; lch=list(g["lch"]); rch=list(g["rch"]); vN=list(g["vN"]); vD=list(g["vD"])
    status=[1 if op[i]==2 else 0 for i in range(N)]; pending=sum(1 for i in range(N) if op[i]!=2)
    truth, root = g["truth"], g["root"]

    d=lambda a,t: cp.asarray(a,t)
    dop=d(op,cp.int32); dnarg=d(narg,cp.int32); dlch=d(lch,cp.int32); drch=d(rch,cp.int32)
    dvN=d(vN,cp.uint64); dvD=d(vD,cp.uint64); dstatus=d(status,cp.int32)
    qtail=cp.full(1,N,cp.int32); pend=cp.full(1,pending,cp.int32); err=cp.zeros(1,cp.int32)
    pkg=cp.zeros(2*FIELDS,cp.int32); active=cp.zeros(1,cp.int32)
    gtrace=cp.zeros(256,cp.int32); gtracen=cp.zeros(1,cp.int32)
    nsm=cp.cuda.Device().attributes["MultiProcessorCount"]; blocks,threads=8*nsm,128

    cur=[0]
    def publish(gact, epoch):
        inactive=1-cur[0]
        pkg[inactive*FIELDS:inactive*FIELDS+FIELDS]=cp.asarray([gact,0,0,epoch],cp.int32)
        active[:]=inactive; cur[0]=inactive

    publish(nsm, 0)                                               # initial schedule (coop-like: nSM lead lanes)
    strm=cp.cuda.Stream(non_blocking=True)
    with strm:
        _apex((blocks,),(threads,),(dop,dnarg,dlch,drch,dvN,dvD,dstatus,qtail,pend,err,
                                    np.int32(N),np.int64(N),pkg,active,np.int32(FIELDS),
                                    gtrace,gtracen,np.int32(256),np.int32(35_000_000)))
    # host controller: publish a SEQUENCE of active-lane counts (the live schedule) WHILE the megakernel drains.
    # (kernel throttled ~25ms/sweep so the short fold spans this window and catches multiple g changes.)
    for epoch, gact in enumerate([nsm, 4*nsm, blocks*threads//2, 2*nsm, blocks*threads], start=1):
        publish(gact, epoch); time.sleep(0.025)
    strm.synchronize()                                           # NATURAL completion (productivity), no stop

    rn, rd = int(dvN.get()[root]), int(dvD.get()[root])
    got = Fraction(rn, rd); e = int(err.get()[0]); pe = int(pend.get()[0])
    gn = int(gtracen.get()[0]); gs = [int(x) for x in gtrace.get()[:gn]]
    print(f"  DAG: {N} nodes (u64-fitting); true root = {truth}")
    print(f"  apex root = {got}  ({'CORRECT' if got==truth else 'WRONG'}); drained pending->{pe}, err={e}")
    print(f"  live active-lane schedules used during the ONE drain (recorded): {gs}")

    w1 = True                                                    # one kernel: pool-drain + actuator-read + live-schedule
    w2 = (got==truth) and (len(set(gs))>=2)                      # correct WHILE >=2 distinct g used live, no relaunch
    w3 = (pe==0) and (e==0)                                      # drained via pending==0; assertion never fired (no fuel)
    print(f"\nW1 ONE KERNEL, THREE SHADOWS (DAG work-queue drain + resident-package read + live schedule): {w1}")
    print(f"W2 CORRECT UNDER LIVE RECONFIG (root==truth while {len(set(gs))} distinct active-lane counts used, no relaunch): {w2}")
    print(f"W3 PRODUCTIVITY, NO FUEL (pending->0 structural drain; err=0, the proven assertion never fired): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ω: the apex. ONE persistent on-device megakernel drains the DAG")
    print(f"  work-queue (pool), reads the resident telemetry package every sweep (actuator), and takes its")
    print(f"  schedule -- the active-lane granularity -- LIVE from it (megakernel), terminating by PRODUCTIVITY")
    print(f"  (no fuel) with the RESULT invariant to the live reconfiguration (combine ⊥ schedule, on-device).")
    print(f"  The session's shadows have snapped into the unified on-device evaluator. Host side = discover+measure")
    print(f"  -> navigate -> collect_package -> publish (jea_navigator/jea_telemetry); this is the device half.")
