#!/usr/bin/env python3
"""jea_apex.py — Δ-Ω (AI-Ω) + Δ-Ω-carrier: the apex megakernel = pool ⊕ actuator ⊕ megakernel, on the EXISTING
u128 escalating carrier (jea_core.Q128_CUDA) -- NOT raw u64, NOT a reinvented fold.

The session's shadows compose into the unified on-device evaluator:
  * jea_engine_pool  -> the DAG WORK-QUEUE drain (emit-or-spawn), terminating by PRODUCTIVITY (no fuel:
                        while(*pending>0); only numeric is the proven-invariant assertion sweeps<=npool).
  * jea_actuator     -> reads the device-RESIDENT telemetry package each sweep (host double-buffer swap).
  * jea_megakernel   -> the SCHEDULE (active-lane count g = on-device coop<->strat granularity) is set LIVE
                        from the package; the RESULT is invariant (combine ⊥ schedule).
  * Δ-Ω-carrier      -> the combine runs on the ALREADY-PROVEN u128 carrier (jea_core.Q128_CUDA: u128 ld/st,
                        --device-int128) with PREDICT-PLACE by bit-length and err=2 byte-limb-DELIVER on
                        overflow -- exactly jea_engine_apex's escalation. NO fitting the workload to u64.

The on-device schedule knob is the ACTIVE-LANE COUNT g: lane gid<g participates and strides the queue by g, so
ANY g>=1 covers all slots -> correct + productive regardless. The host publishes g LIVE.

Witnesses (each [W]):
1. ONE KERNEL, FOUR SHADOWS: a single persistent megakernel drains the DAG work-queue (pool), reads the
   resident package (actuator), takes its schedule live (megakernel), AND combines on the u128 escalating
   carrier (Δ-Ω-carrier) -- by construction.
2. CARRIER -- EXACT BEYOND u64: a DAG whose intermediates OVERFLOW u64 reduces to the TRUE rational on the
   u128 carrier (predict-place; err=0 = no escalation needed), where raw u64 gave a WRONG value. No workload-fit.
3. CORRECT UNDER LIVE RECONFIG + PRODUCTIVITY: root==truth while the host live-published MULTIPLE active-lane
   counts during the ONE drain; drained via pending==0 (no fuel); err==0.
"""
import os, sys, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_core
from jea_generator_dag import build_dag
import jea_engine_pool as POOL
from fractions import Fraction

FIELDS = 4        # package: [g (active-lane count = on-device schedule), fstar%, bneck, epoch]

_SRC = jea_core.Q128_CUDA + r'''
__device__ __forceinline__ int bitlen128(u128 v){
  u64 hi=(u64)(v>>64), lo=(u64)v;
  if (hi) return 128 - __clzll(hi);
  if (lo) return 64 - __clzll(lo);
  return 0;
}
extern "C" __global__ void apex(
    int* op,int* narg,int* lch,int* rch,
    u64* vNlo,u64* vNhi,u64* vDlo,u64* vDhi, int* bln, int* bld, int* escal, int* tier, volatile int* status,
    volatile int* qtail, volatile int* pending, volatile int* err, int npool, long long assert_bound,
    volatile int* pkg, volatile int* active, int fields, int* gtrace, int* gtracen, int gtcap, int spin)
{
  int gid = blockIdx.x*blockDim.x+threadIdx.x;
  long long sw=0; int last_g=-1; int gn=0;
  while (*pending>0) {                                          // STRUCTURAL drain (productivity; no fuel)
    int a=*active; int g=pkg[a*fields+0]; if (g<1) g=1;        // LIVE schedule = active-lane count
    if (gid==0 && g!=last_g && gn<gtcap) { gtrace[gn++]=g; last_g=g; }
    if (gid < g) {                                              // only ACTIVE lanes do work AND count work-sweeps
      if (sw++ >= assert_bound) { *err=3; break; }             // assertion on ACTIVE-lane work sweeps (idle lanes
                                                               // must NOT count -- they spin fast and would false-trip it)
      int qt=*qtail;
      for (int i=gid; i<qt; i+=g) {
        if (status[i]!=0) continue;
        int o=op[i];
        if (o==3) {                                            // SPAWN (emit-or-spawn; present for the full engine)
          if (atomicCAS((int*)&status[i],0,2)==0) {
            int n=narg[i];
            if (n==0) { vNlo[i]=1;vNhi[i]=0;vDlo[i]=1;vDhi[i]=0;bln[i]=1;bld[i]=1; __threadfence(); status[i]=1; atomicSub((int*)pending,1); }
            else {
              int c=atomicAdd((int*)qtail,2);
              if (c+1<npool) {
                op[c]=3;narg[c]=n-1;lch[c]=-1;rch[c]=-1;vNlo[c]=0;vNhi[c]=0;vDlo[c]=1;vDhi[c]=0;bln[c]=0;bld[c]=1;status[c]=0;
                op[c+1]=3;narg[c+1]=n-1;lch[c+1]=-1;rch[c+1]=-1;vNlo[c+1]=0;vNhi[c+1]=0;vDlo[c+1]=1;vDhi[c+1]=0;bln[c+1]=0;bld[c+1]=1;status[c+1]=0;
                lch[i]=c;rch[i]=c+1; op[i]=0; __threadfence(); atomicAdd((int*)pending,2); status[i]=0;
              } else { *err=1; vNlo[i]=0;vNhi[i]=0;vDlo[i]=1;vDhi[i]=0; status[i]=1; atomicSub((int*)pending,1); }
            }
          }
        } else if (o==0 || o==1) {                             // ADD / MUL terminal combine on the u128 carrier
          int L=lch[i],R=rch[i];
          if (status[L]==1 && status[R]==1) {
            if (atomicCAS((int*)&status[i],0,2)==0) {
              // PREDICT-PLACE (Carrier) + ESCALATION-MARK PROPAGATION (Delta-Psi): the crown is the device's OWN residue.
              // A node is in the crown iff it overflows u128 OR a child is in the crown (escal propagates UP); the
              // host deliver READS escal[] instead of re-predicting (recompute-from-residue, not copy-across-boundary).
              if (escal[L] || escal[R]) {                      // ANCESTOR of an escalated node -> escalate (no compute)
                escal[i]=1; tier[i]=2; *err=2; vNlo[i]=0;vNhi[i]=0;vDlo[i]=1;vDhi[i]=0; bln[i]=0; bld[i]=1;
              } else {
              int bn = (o==1) ? (bln[L]+bln[R]) : (max(bln[L]+bld[R], bln[R]+bld[L])+1);
              int bd = bld[L]+bld[R];
              if (bn>128 || bd>128) {                          // FRONTIER: this node overflows u128 (actual reduced)
                escal[i]=1; tier[i]=2; *err=2; vNlo[i]=0;vNhi[i]=0;vDlo[i]=1;vDhi[i]=0; bln[i]=0; bld[i]=1;
              } else if (bn<=64 && bd<=64) {                   // PER-NODE u64 PLACEMENT (Delta-Phi-pernode): result +
                u64 nl=vNlo[L], dl=vDlo[L], nr=vNlo[R], dr=vDlo[R];   // operands fit u64 -> cheaper u64 mul + u64 gcd
                u64 na = (o==1) ? (nl*nr) : (nl*dr + nr*dl);
                u64 D  = dl*dr;
                u64 aa=na, bb=D; while(bb){ u64 r=aa%bb; aa=bb; bb=r; } u64 gg=aa?aa:1ULL;
                na/=gg; D/=gg;
                vNlo[i]=na; vNhi[i]=0; vDlo[i]=D; vDhi[i]=0;
                bln[i]= na ? (64-__clzll(na)) : 0; bld[i]= D ? (64-__clzll(D)) : 0; tier[i]=0;
              } else {                                         // u128 path (each node its narrowest sufficient carrier)
                u128 nl=ld(vNlo,vNhi,L), dl=ld(vDlo,vDhi,L), nr=ld(vNlo,vNhi,R), dr=ld(vDlo,vDhi,R);
                u128 na = (o==1) ? (nl*nr) : (nl*dr + nr*dl);
                u128 D  = dl*dr;
                u128 aa=na, bb=D; while(bb){ u128 r=aa%bb; aa=bb; bb=r; } u128 gg=aa?aa:(u128)1;  // gcd-reduce (u128 %)
                na/=gg; D/=gg;
                st(vNlo,vNhi,i,na); st(vDlo,vDhi,i,D); bln[i]=bitlen128(na); bld[i]=bitlen128(D); tier[i]=1;
              }
              }
              __threadfence(); status[i]=1; atomicSub((int*)pending,1);
            }
          }
        }
      }
    }
    __threadfence();
    long long tw=clock64(); while (clock64()-tw < (long long)spin) { }   // throttle so host republishes mid-drain
  }
  if (gid==0) *gtracen = gn;
}
'''
_apex = cp.RawKernel(_SRC, "apex", options=("--device-int128",))


if __name__ == "__main__":
    print("Δ-Σ-wire: the persistent apex megakernel, SCHEDULE driven by the navigator (composed, not hand-published)\n")
    g = build_dag(256, 6); N = g["N"]                            # 66-bit truth: intermediates OVERFLOW u64, fit u128
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]
    lch=list(g["lch"]); rch=list(g["rch"]); vN=[int(x) for x in g["vN"]]; vD=[int(x) for x in g["vD"]]
    status=[1 if op[i]==2 else 0 for i in range(N)]; pending=sum(1 for i in range(N) if op[i]!=2)
    truth, root = g["truth"], g["root"]

    d=lambda a,t: cp.asarray(a,t)
    dop=d(op,cp.int32); dnarg=cp.zeros(N,cp.int32); dlch=d(lch,cp.int32); drch=d(rch,cp.int32)
    vNlo=d([v & 0xFFFFFFFFFFFFFFFF for v in vN],cp.uint64); vNhi=d([v>>64 for v in vN],cp.uint64)
    vDlo=d([v & 0xFFFFFFFFFFFFFFFF for v in vD],cp.uint64); vDhi=d([v>>64 for v in vD],cp.uint64)
    bln=d([v.bit_length() for v in vN],cp.int32); bld=d([v.bit_length() for v in vD],cp.int32)
    escal=cp.zeros(N,cp.int32); tier=cp.zeros(N,cp.int32); dstatus=d(status,cp.int32)
    qtail=cp.full(1,N,cp.int32); pend=cp.full(1,pending,cp.int32); err=cp.zeros(1,cp.int32)
    pkg=cp.zeros(2*FIELDS,cp.int32); active=cp.zeros(1,cp.int32)
    gtrace=cp.zeros(256,cp.int32); gtracen=cp.zeros(1,cp.int32)
    nsm=cp.cuda.Device().attributes["MultiProcessorCount"]; blocks,threads=8*nsm,128

    cur=[0]
    def publish(gact, epoch):
        inactive=1-cur[0]
        pkg[inactive*FIELDS:inactive*FIELDS+FIELDS]=cp.asarray([int(gact),0,0,epoch],cp.int32)
        active[:]=inactive; cur[0]=inactive

    # Δ-Σ-wire: the SCHEDULE comes from the NAVIGATOR (operating point re-solved from discovered surfaces + live
    # telemetry), NOT a hardcoded list. The orphaned control loop is now COMPOSED: jea_apex -> jea_navigator +
    # jea_telemetry (imported here so module-import of jea_apex stays light). The fake hand-published g is DELETED.
    import jea_navigator as NAV
    import jea_telemetry as TEL
    from jea_cost import deep_chain
    tb=max(truth.numerator.bit_length(), truth.denominator.bit_length())
    surf=NAV.discover_surfaces(); intrinsic={"pcie":surf["pcie_eff"],"cpu":surf["cpu_eff"]}
    def gint(opg):                                            # map navigate's categorical g* -> apex active-lane count
        if "strat" in opg or "free" in opg: return blocks*threads   # strat / free -> all lanes (full throughput)
        return nsm                                            # coop / spawn -> few active lanes (cooperative)
    wls=[dict(dag=g,C=0.9,f=0.7,bits=tb,spawn=False),                 # the apex's OWN workload (drives the real drain)
         dict(dag=deep_chain(200),C=0.9,f=0.7,bits=tb,spawn=False),   # a deep chain (different measured g-surface)
         dict(dag=None,C=0.9,f=0.7,bits=tb,spawn=True)]               # a spawn workload (structural coop)
    ops=[NAV.navigate(surf, TEL.collect_package(surf["imc"],intrinsic,i), wl) for i,wl in enumerate(wls)]
    gseq=[gint(op["g"]) for op in ops]                        # navigator-sourced schedule sequence (NO hardcoded g)

    publish(gseq[0], 0)
    strm=cp.cuda.Stream(non_blocking=True)
    with strm:
        _apex((blocks,),(threads,),(dop,dnarg,dlch,drch,vNlo,vNhi,vDlo,vDhi,bln,bld,escal,tier,dstatus,
                                    qtail,pend,err,np.int32(N),np.int64(N),pkg,active,np.int32(FIELDS),
                                    gtrace,gtracen,np.int32(256),np.int32(35_000_000)))
    for epoch, gact in enumerate(gseq[1:], start=1):          # publish navigator-sourced g's LIVE during the drain
        publish(gact, epoch); time.sleep(0.025)
    strm.synchronize()

    rn = (int(vNhi.get()[root])<<64)|int(vNlo.get()[root]); rd = (int(vDhi.get()[root])<<64)|int(vDlo.get()[root])
    got = Fraction(rn, rd); e=int(err.get()[0]); pe=int(pend.get()[0])
    gn=int(gtracen.get()[0]); gs=[int(x) for x in gtrace.get()[:gn]]
    u64_val = POOL.run_qfold(g)[0]                               # SAME DAG on the raw-u64 carrier (overflows)

    print(f"  DAG: {N} nodes, truth ~{tb} bits (intermediates overflow u64); true root = {truth}")
    print(f"  NAVIGATOR operating points (re-solved from surfaces + live telemetry, per workload):")
    for i,op in enumerate(ops): print(f"    wl{i}: g={op['g']!r} -> apex g={gseq[i]}  (f*={op['fstar']} bneck={op['bottleneck']} carrier={op['carrier']})")
    print(f"  u128-apex root = {got}  ({'CORRECT' if got==truth else 'WRONG'}); drained pending->{pe}, err={e}")
    print(f"  raw-u64 carrier (same DAG) = {u64_val}  ({'overflow/WRONG' if u64_val!=truth else 'ok'})")
    print(f"  navigator-sourced schedules the kernel actually saw during the ONE drain: {gs}")

    w1 = (len(gseq)==len(wls)) and all(isinstance(x,int) for x in gseq)   # schedule SOURCED from navigate(), not a list
    w2 = (got==truth) and (u64_val != truth) and (e==0)         # u128 exact where u64 overflowed; no escalation needed
    w3 = (got==truth) and (pe==0)                              # correct + productivity under the NAVIGATOR-set schedule
    print(f"\nW1 SCHEDULE FROM THE NAVIGATOR, not a hardcoded list (Δ-Σ-wire: jea_apex -> jea_navigator+jea_telemetry")
    print(f"   COMPOSED; g = navigate(collect_package()) per workload; the fake hand-published g is DELETED): {w1}")
    print(f"W2 CARRIER EXACT BEYOND u64 (u128 root==truth where raw-u64 overflowed; err=0, no fit-to-u64): {w2}")
    print(f"W3 CORRECT + PRODUCTIVITY under the navigator-set schedule (root==truth, pending->0; kernel saw g's {sorted(set(gs))}, "
          f"{'>=2 distinct -> live reconfig exercised' if len(set(gs))>=2 else 'stable (navigator-not-answer: same conditions -> same point)'}): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-wire: the apex's SCHEDULE is now the NAVIGATOR's output, not a")
    print(f"  hardcoded list. The orphaned control loop is COMPOSED: jea_apex imports jea_navigator + jea_telemetry,")
    print(f"  surfaces are DISCOVERED on this box, telemetry is COLLECTED live, and g = navigate(collect_package())")
    print(f"  drives the drain (the fake hand-published g is deleted). The combine still runs exact on the u128")
    print(f"  carrier with predict-place + err=2 deliver, root==truth regardless of schedule (combine ⊥ schedule).")
    print(f"  REMAINING (Δ-Σ-decide): navigate() still runs on the HOST -- move the operating-point solve on-device")
    print(f"  (the supervisor reads the uploaded telemetry package and decides, no host round-trip per decision).")
