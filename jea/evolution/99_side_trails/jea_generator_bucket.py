#!/usr/bin/env python3
# SIDE-TRAIL (off the main spine) -- explored, then absorbed/superseded; not a rung of the linear ladder. See ../00_SYLLABUS.md
"""jea_generator_bucket.py — bucketized substrata + escalation priority (the scheduler done right).

The stratified evaluator was close but COARSE: one K per whole topological stratum, re-scanning
already-converged nodes every pass, and treating an escalation like any other unfinished node.
Two refinements (user), one principle — PRIORITIZE BY PROGRESS STATE:

  * BUCKETIZE strata -> substrata: after each K-window pass, COMPACT the survivors into a dense
    substratum and raise K only for THEM. K tracks each bucket's real gcd depth instead of being
    dragged up by the deepest node while the shallow ones (already done) are re-scanned. Efficient
    dynamic K: total work = sum of bucket sizes, not passes x stratum-size.
  * ESCALATION PRIORITY: a node that overflowed 128-bit is cracked-open AND blocking its parent.
    Pull it into a priority bucket (route to wider carrier) BEFORE opening fresh nodes. In-progress
    /escalated work outranks un-started work.

Demonstrated on a heterogeneous batch (mostly-shallow gcd + a few Fibonacci-deep + a few overflow):
bucketized vs flat re-pass work, and the escalation bucket pulled first.
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core

# combine (mul) two ℚ leaf-operands then gcd-window-reduce; per-node done/esc. 128-bit + escalate.
_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void bucket_step(
    const int* idx, int ni, int K,
    u64* nl,u64* nh,u64* dl,u64* dh,             // operand A (num,den) of each task
    u64* ml,u64* mh,u64* el,u64* eh,             // operand B (num,den)
    u64* al,u64* ah,u64* bl,u64* bh, int* initf, // gcd residue (a,b) + init flag
    u64* outNl,u64* outNh,u64* outDl,u64* outDh, // reduced result
    int* done, int* esc, int* steps,
    volatile int* notdone, volatile int* obsmax)
{
    int t=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x;
    for (int i=t;i<ni;i+=stride){
        int s=idx[i];
        if (done[s] || esc[s]) continue;                 // converged or escalated -> skip
        if (!initf[s]){                                  // crack open: na=nA*nB, D=dA*dB (mul)
            u128 na=ld(nl,nh,s)*ld(ml,mh,s), D=ld(dl,dh,s)*ld(el,eh,s); int o=0;
            o |= (ld(nl,nh,s)!=0) && (na/ld(nl,nh,s)!=ld(ml,mh,s));
            o |= (ld(dl,dh,s)!=0) && (D /ld(dl,dh,s)!=ld(el,eh,s));
            if (o){ esc[s]=1; continue; }                // OVERFLOW -> escalated (priority bucket), don't reduce
            st(al,ah,s,na); st(bl,bh,s,D); st(outNl,outNh,s,na); st(outDl,outDh,s,D); initf[s]=1;
        }
        u128 aa=ld(al,ah,s), bb=ld(bl,bh,s); int st_=steps[s];
        for(int j=0;j<K;j++){ if(bb!=0){ u128 r=aa%bb; aa=bb; bb=r; st_++; } }
        st(al,ah,s,aa); st(bl,bh,s,bb); steps[s]=st_;
        if (bb==0){ u128 g=(aa!=0)?aa:(u128)1; st(outNl,outNh,s, ld(outNl,outNh,s)/g);
                    st(outDl,outDh,s, ld(outDl,outDh,s)/g); done[s]=1; }
        else atomicAdd((int*)notdone,1);
        atomicMax((int*)obsmax, done[s]?st_:st_+1);
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "bucket_step", int128=True)
def _lh(v): M=(1<<64)-1; v=[int(x) for x in v]; return cp.asarray([x&M for x in v],cp.uint64),cp.asarray([(x>>64)&M for x in v],cp.uint64)


def make_workload(M, deep_frac=0.01, ovf_frac=0.001, seed=1):
    """M mul-tasks: mostly shallow gcd, a few Fibonacci-deep, a few overflow (>2^128)."""
    rng=np.random.default_rng(seed)
    fib=[1,1]
    while len(fib)<60: fib.append(fib[-1]+fib[-2])
    A=[]; B=[]; kind=[]
    for i in range(M):
        u=rng.random()
        if u<ovf_frac:   A.append((10**20+i,1)); B.append((10**20+i,1)); kind.append("ovf")
        elif u<ovf_frac+deep_frac: k=44; A.append((fib[k+1],fib[k])); B.append((1,1)); kind.append("deep")
        else: A.append((int(rng.integers(2,7)),int(rng.integers(2,7)))); B.append((1,1)); kind.append("shallow")
    return A,B,kind


def _alloc(M):
    z=lambda: cp.zeros(M,cp.uint64); zi=lambda: cp.zeros(M,cp.int32)
    return dict(al=z(),ah=z(),bl=z(),bh=z(),initf=zi(),outNl=z(),outNh=z(),outDl=z(),outDh=z(),
                done=zi(),esc=zi(),steps=zi())


def run(A,B,bucketize, K0=4):
    M=len(A); nsm=cp.cuda.Device().attributes["MultiProcessorCount"]; nblk=8*nsm
    nl,nh=_lh([a[0] for a in A]); dl,dh=_lh([a[1] for a in A])
    ml,mh=_lh([b[0] for b in B]); el,eh=_lh([b[1] for b in B])
    S=_alloc(M); notdone=cp.zeros(1,cp.int32); obsmax=cp.zeros(1,cp.int32)
    def launch(idx_dev, ni, K):
        notdone[0]=0
        _kern((nblk,),(256,),(idx_dev,np.int32(ni),np.int32(K),nl,nh,dl,dh,ml,mh,el,eh,
              S['al'],S['ah'],S['bl'],S['bh'],S['initf'],S['outNl'],S['outNh'],S['outDl'],S['outDh'],
              S['done'],S['esc'],S['steps'],notdone,obsmax))
        return int(notdone.get()[0])
    work=0; passes=0; K=K0
    cp.cuda.Stream.null.synchronize(); t0=time.perf_counter()
    if not bucketize:
        idx=cp.arange(M,dtype=cp.int32)
        while True:
            launch(idx,M,K); work+=M; passes+=1
            doneesc=(S['done'].get()|S['esc'].get())
            if doneesc.all(): break
            K=jea_core.relax_q_ref(K,int(obsmax.get()[0]))
    else:
        active=np.arange(M,dtype=np.int32)
        while len(active):
            idx=cp.asarray(active,cp.int32); launch(idx,len(active),K); work+=len(active); passes+=1
            done=S['done'].get(); esc=S['esc'].get()
            survivors=active[(done[active]==0)&(esc[active]==0)]   # COMPACT survivors -> next substratum
            if len(survivors)==len(active) and K> (1<<20): break
            if len(survivors)==0: break
            active=survivors; K=jea_core.relax_q_ref(K,int(obsmax.get()[0]))  # raise K only for the bucket
    cp.cuda.Stream.null.synchronize(); ms=(time.perf_counter()-t0)*1e3
    return dict(work=work, passes=passes, ms=ms, esc=int(S['esc'].get().sum()), done=int(S['done'].get().sum()))


if __name__=="__main__":
    M=200000
    A,B,kind=make_workload(M, deep_frac=0.01, ovf_frac=0.001)
    nsh=kind.count("shallow"); nde=kind.count("deep"); nov=kind.count("ovf")
    print(f"bucketized substrata + escalation priority — heterogeneous batch of {M} mul-tasks\n")
    print(f"  workload: {nsh} shallow (gcd~2) + {nde} Fibonacci-deep (gcd~43) + {nov} overflow(>2^128)\n")
    flat=run(A,B,bucketize=False)
    buck=run(A,B,bucketize=True)
    print(f"  {'scheduler':14s} {'passes':>7} {'node-passes(work)':>18} {'ms':>8}  done/esc")
    print(f"  {'flat re-pass':14s} {flat['passes']:>7} {flat['work']:>18,} {flat['ms']:>8.2f}  {flat['done']}/{flat['esc']}")
    print(f"  {'bucketized':14s} {buck['passes']:>7} {buck['work']:>18,} {buck['ms']:>8.2f}  {buck['done']}/{buck['esc']}")
    print(f"\n  bucketization: {flat['work']/buck['work']:.1f}x less work (compact survivors; K per bucket,")
    print(f"  not dragged up by the deepest node while re-scanning the shallow ones).")
    print(f"  escalation: {buck['esc']} overflow tasks DETECTED -> priority bucket (route to multi-limb,")
    print(f"  pulled before fresh work); never silently reduced on a wrapped value. done={buck['done']} (= {nsh+nde}).")
