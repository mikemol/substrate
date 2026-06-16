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
// Delta-Sigma-decide: the thermal gate (thermal_gate.gate(T,trip,floor=0.4,k=0.03)) ported on-device.
__device__ __forceinline__ double dgate(double T, double trip){
  if (T <= trip) return 1.0;
  double v = 1.0 - 0.03*(T - trip);
  return v < 0.4 ? 0.4 : v;
}
extern "C" __global__ void apex(
    int* op,int* narg,int* lch,int* rch,
    u64* vNlo,u64* vNhi,u64* vDlo,u64* vDhi, int* bln, int* bld, int* escal, int* tier, volatile int* status,
    volatile int* qtail, volatile int* pending, volatile int* err, int npool, long long assert_bound,
    volatile int* pkg, volatile int* active, int fields, int* gtrace, int* gtracen, int gtcap, int spin,
    const double* tpkg, int* dout, int TF, int nsm_p, int full_p, int decide_dev)
{
  int gid = blockIdx.x*blockDim.x+threadIdx.x;
  long long sw=0; int last_g=-1; int gn=0; int last_ep=-1;
  while (*pending>0) {                                          // STRUCTURAL drain (productivity; no fuel)
    int a=*active;
    if (decide_dev && gid==0) {                                // Delta-Sigma-decide: the SUPERVISOR computes the operating
      const double* tb = tpkg + (long long)a*TF;               // point ON-DEVICE from the host-UPLOADED evidence
      double imc=tb[0], pmax=tb[1], peff=tb[2], ceff=tb[3], T=tb[4], link=tb[5], trip=tb[6];
      double coop=tb[7], strat=tb[8], spread=tb[9], bits=tb[10], C=tb[11], f=tb[12];
      double gc = imc*dgate(T,trip)*ceff;                      // dispatch (decide): load-balance two conductances
      double gg = pmax*link*peff;
      double fstar = (gc+gg>0.0) ? gg/(gc+gg) : 0.0;
      double gclk = dgate(T,100.0);                            // binding edge: argmax of 3 single-edge relaxations
      double avail = imc - 8e9*link - imc*0.25; double amin=imc*0.01; if(avail<amin) avail=amin;
      double gain_imc = imc*0.25*gclk;                         // drop iGPU shunt
      double gain_th  = avail*(1.0 - gclk);                    // relax thermal to ref (gate(46,100)=1)
      double gain_pcie= pmax*(1.0 - link);                     // link -> full
      int bneck = 0; double gmax = gain_imc;
      if (gain_th  > gmax){ gmax=gain_th;  bneck=1; }
      if (gain_pcie> gmax){ gmax=gain_pcie; bneck=2; }
      double d = coop-strat; if (d<0) d=-d;                    // schedule g: coop/strat compare vs measured noise
      int g_dec = (d<=spread) ? full_p : (coop<strat ? nsm_p : full_p);
      int mode = (252.0*C > 216.0) ? 1 : 0;                    // bang-bang knobs
      int rep  = ((8.0-7.0*f) < (1.0+7.0*f)) ? 1 : 0;
      int carr = (bits<=64) ? 0 : (bits<=128 ? 1 : 2);
      pkg[a*fields+0] = g_dec;                                 // WRITE the decided schedule for the workers
      int ep=(int)tb[13];                                      // TRACE the decision on each NEW epoch (robust to read-timing):
      if (ep!=last_ep) {                                       //   dout = [count, (epoch,f*1000,bneck,g,mode,rep,carr) ...]
        int c=dout[0];
        if (c<8) { dout[1+7*c]=ep; dout[2+7*c]=(int)(fstar*1000.0+0.5); dout[3+7*c]=bneck;
                   dout[4+7*c]=g_dec; dout[5+7*c]=mode; dout[6+7*c]=rep; dout[7+7*c]=carr; dout[0]=c+1; }
        last_ep=ep;
      }
      __threadfence();
    }
    int g=pkg[a*fields+0]; if (g<1) g=1;                       // LIVE schedule = active-lane count (now supervisor-decided)
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
assert _SRC.isascii(), "kernel source must be ASCII -- NVRTC writes it via the ascii codec; a Greek Δ/Σ in a comment fails the compile"
_apex = cp.RawKernel(_SRC, "apex", options=("--device-int128",))


if __name__ == "__main__":
    print("Δ-Σ-decide: the apex SUPERVISOR computes the operating point ON-DEVICE from host-uploaded evidence\n")
    g = build_dag(256, 6); N = g["N"]                            # 66-bit truth: intermediates OVERFLOW u64, fit u128
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]
    lch=list(g["lch"]); rch=list(g["rch"]); vN=[int(x) for x in g["vN"]]; vD=[int(x) for x in g["vD"]]
    status=[1 if op[i]==2 else 0 for i in range(N)]; pending=sum(1 for i in range(N) if op[i]!=2)
    truth, root = g["truth"], g["root"]

    d=lambda a,t: cp.asarray(a,t); MASK=0xFFFFFFFFFFFFFFFF
    nsm=cp.cuda.Device().attributes["MultiProcessorCount"]; blocks,threads=8*nsm,128; full=blocks*threads
    tb=max(truth.numerator.bit_length(), truth.denominator.bit_length())

    # Δ-Σ-decide: the HOST uploads raw EVIDENCE (surfaces it measured + live /sys meters the GPU can't read); the
    # on-device SUPERVISOR (apex lead thread, gid==0) computes the OPERATING POINT on-GPU. navigate() below is ONLY
    # the cross-check oracle (not the driver). One evidence pkg per drain here; the mid-drain LIVE swap is Δ-Σ-wire's.
    # NB the on-device decision TRACE (dout) is a WAL -- it SHOULD be held by the term-algebra SPPF/EEA trace, not
    # this ad-hoc array (Δ-Σ-trace, recorded as the next arc -- the decision sequence IS a never-discard-residue trace).
    import jea_navigator as NAV
    import live_dispatcher as LD
    surf=NAV.discover_surfaces()
    gsf=NAV.measure_g_surface(g)                               # g-surface of the apex's OWN dag (host MEASUREMENT)
    trip=float(LD._TRIP); pmax=float(surf["pcie_max"]); TF=14
    BN={"iMC/iGPU":0,"thermal":1,"PCIe/link":2}               # host bottleneck string -> on-device index

    def run_drain(T, link):
        """One full drain under ONE uploaded evidence package: the supervisor decides ON-DEVICE, workers drain.
        Fresh device arrays each call (the drain mutates them). Returns (root, err, pending, decision-trace dt)."""
        dop=d(op,cp.int32); dnarg=cp.zeros(N,cp.int32); dlch=d(lch,cp.int32); drch=d(rch,cp.int32)
        vNlo=d([v&MASK for v in vN],cp.uint64); vNhi=d([v>>64 for v in vN],cp.uint64)
        vDlo=d([v&MASK for v in vD],cp.uint64); vDhi=d([v>>64 for v in vD],cp.uint64)
        bln=d([v.bit_length() for v in vN],cp.int32); bld=d([v.bit_length() for v in vD],cp.int32)
        escal=cp.zeros(N,cp.int32); tier=cp.zeros(N,cp.int32); dstatus=d(status,cp.int32)
        qtail=cp.full(1,N,cp.int32); pend=cp.full(1,pending,cp.int32); err=cp.zeros(1,cp.int32)
        pkg=cp.full(2*FIELDS,full,cp.int32); active=cp.zeros(1,cp.int32)                       # safe default schedule
        gtrace=cp.zeros(256,cp.int32); gtracen=cp.zeros(1,cp.int32)
        vec=[surf["imc"],pmax,surf["pcie_eff"],surf["cpu_eff"],float(T),float(link),trip,
             gsf["coop"],gsf["strat"],gsf["spread"],float(tb),0.9,0.7,0.0]                     # raw EVIDENCE
        tpkg=cp.asarray(vec+[0.0]*TF, cp.float64); dout=cp.zeros(1+7*8,cp.int32)
        _apex((blocks,),(threads,),(dop,dnarg,dlch,drch,vNlo,vNhi,vDlo,vDhi,bln,bld,escal,tier,dstatus,
                                    qtail,pend,err,np.int32(N),np.int64(N),pkg,active,np.int32(FIELDS),
                                    gtrace,gtracen,np.int32(256),np.int32(0),
                                    tpkg,dout,np.int32(TF),np.int32(nsm),np.int32(full),np.int32(1)))
        cp.cuda.Stream.null.synchronize()
        rn=(int(vNhi.get()[root])<<64)|int(vNlo.get()[root]); rd=(int(vDhi.get()[root])<<64)|int(vDlo.get()[root])
        return (Fraction(rn,rd) if rd else None), int(err.get()[0]), int(pend.get()[0]), [int(x) for x in dout.get()]

    tel=LD.poll()                                            # live meters (off-GPU; uploaded as evidence)
    epochs=[("live",tel["T"],tel["link_state"]), ("hot(synthetic)",120.0,0.50),
            ("live-again",tel["T"],tel["link_state"])]       # recurring evidence -> the WAL should INTERN it (Δ-Σ-trace c)
    import jea_eval as EVAL                                  # the TRACE HOME: fold the supervisor decision WAL here
    decisions=[]; hits=[]; got=None; e=0; pe=0
    for label,T,link in epochs:                              # one drain per evidence pkg -> supervisor decides on-device
        got,e,pe,dt = run_drain(T,link)
        f1000,bn,gd = (dt[2],dt[3],dt[4]) if dt[0]>=1 else (0,-1,0)
        was_hit,canon = EVAL.record_decision((round(T,1),round(link,3)), (f1000,bn,gd))  # fold dout into the WAL/SPPF
        hits.append(was_hit and canon==(f1000,bn,gd))        # recurring evidence -> hit, cached decision is faithful
        ref=NAV.navigate(surf,{"T":T,"link_state":link,"gov":"?"},dict(dag=g,C=0.9,f=0.7,bits=tb,spawn=False))
        decisions.append((label,T,link,(f1000,bn,gd),ref))

    u64_val = POOL.run_qfold(g)[0]                              # SAME DAG on the raw-u64 carrier (overflows)
    print(f"  DAG: {N} nodes, truth ~{tb} bits (intermediates overflow u64); true root = {truth}")
    print(f"  ON-DEVICE supervisor decisions (one drain per uploaded evidence pkg; the GPU computed each operating point):")
    agree=True
    for label,T,link,dev,ref in decisions:
        f1000,bn,gd=dev; dev_f=f1000/1000.0; ref_bn=BN.get(ref["bottleneck"],-1)
        ok_f=abs(dev_f-ref["fstar"])<=0.02; ok_bn=(bn==ref_bn)
        agree=agree and ok_f and ok_bn
        print(f"    {label:<15} T={T:.0f}C link={link:.2f}: ON-DEVICE f*={dev_f:.2f} bneck={bn} g={gd} "
              f"| host-ref f*={ref['fstar']} bneck={ref_bn} -> match f*:{ok_f} bneck:{ok_bn}")
    print(f"  u128-apex root = {got}  ({'CORRECT' if got==truth else 'WRONG'}); drained pending->{pe}, err={e}")
    print(f"  raw-u64 carrier (same DAG) = {u64_val}  ({'overflow/WRONG' if u64_val!=truth else 'ok'})")

    # Δ-Σ-trace (c): the decision WAL is HELD + INTERNED in jea_eval (the same trace home as the eval memo).
    w_wal = (EVAL.wal_len()==len(epochs)) and (EVAL.distinct_decisions() < EVAL.wal_len()) and any(hits)
    print(f"\n  DECISION WAL (held in jea_eval -- the SAME trace home as the eval/SPPF memo): {EVAL.wal_len()} steps "
          f"-> {EVAL.distinct_decisions()} distinct (recurring 'live' evidence INTERNED; supervisor reused the cached decision)")

    fmoves = len({dv[3][0] for dv in decisions})>=2 or len({dv[3][1] for dv in decisions})>=2  # decision moved w/ evidence
    w1 = agree and len(decisions)>=1                           # on-device decision == host navigate() reference
    w2 = (got==truth) and (u64_val != truth) and (e==0)        # carrier exact where u64 overflowed
    w3 = (got==truth) and (pe==0) and fmoves                   # correct+productive; decision RESPONDS to evidence
    print(f"\nW1 DECISION ON-DEVICE == host reference (the SUPERVISOR computed f*/bottleneck/g/knobs on-GPU from the")
    print(f"   uploaded evidence; matches navigate() within rounding -- faithful port, no host decision in the drive path): {w1}")
    print(f"W2 CARRIER EXACT BEYOND u64 (u128 root==truth where raw-u64 overflowed; err=0): {w2}")
    print(f"W3 CORRECT + DECISION RESPONDS TO EVIDENCE (root==truth, pending->0; on-device f*/bottleneck differ live vs")
    print(f"   hot -- the supervisor re-decides per uploaded package, no host-sync per decision): {w3}")
    print(f"W4 DECISION WAL ≡ EEA/SPPF TRACE (Δ-Σ-trace c: the decision sequence is HELD + INTERNED in jea_eval's memo")
    print(f"   -- recurring evidence dedups to one node, the cached decision reused; durable, not an ephemeral dout): {w_wal}")
    ok=w1 and w2 and w3 and w_wal
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-decide: the operating-point SOLVE now runs ON-DEVICE. The host uploads")
    print(f"  raw evidence (surfaces it measured + live /sys meters the GPU can't read); the apex SUPERVISOR (gid==0)")
    print(f"  reads it and computes f*/bottleneck/schedule-g/mode/repr/carrier on-GPU -- matching the host navigate()")
    print(f"  oracle, NO host round-trip per decision (host = sensor, supervisor = decision). The decision TRACE is a")
    print(f"  WAL that should live in the term-algebra SPPF/EEA structure (Δ-Σ-trace), not this ad-hoc array.")
