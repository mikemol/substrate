#!/usr/bin/env python3
"""jea_engine.py — C1 of the consolidation arc: ONE parameterized combine, carrier as a typedef + mode/K
runtime params. Collapses the duplicated combine bodies of jea_generator_dag (u64), jea_generator_dag128
(u128), and jea_generator_dag_mode (u64 eager/lazy) into a single CUDA source.

The unification: store/compute ALWAYS in u128 lo/hi lanes (u64 is just hi==0); the CARRIER is a compile-
time switch (-DCARRIER_U128) that sets only (a) the escalate threshold (2^64 vs 2^128) and (b) which
overflow check applies (a wider-type value-compare for u64; a division-check for u128, since no native is
wider). MODE (eager/lazy) and K (gcd window) are runtime params. Same cooperative readiness-gated body as
the dag family. This is "carrier is a typedef" enacted, not narrated -- one source, compiled per carrier.

This is C1 only (the combine). C2 will make scheduling a strategy over this combine; C3 folds the carrier
OPS (bucket/escalate-tier/trace/byte-limb); C4 wires intern + oracle; C5 makes the demos thin callers + a
regression runner. The unification is "done" only when the runner shows one engine reproduces every witness.

Witnesses (each [W]) -- reproduce the scripts this collapses, bit-exact:
1. EAGER u64 == Python truth, canonical (== jea_generator_dag / dag_mode eager).
2. LAZY u64 == truth (reduced at readout), non-canonical>0 (== jea_generator_dag_mode lazy).
3. CARRIER WIDENS: a DAG whose value is >2^64 -- carrier=64 ESCALATES, carrier=128 is EXACT (the typedef
   param reaches where u64 can't; == jea_generator_dag128's wider reach). SAME source, different -D.
4. u128 OVERFLOW: an all-mul product >2^128 -- carrier=128 ESCALATES (detected, not wrapped; == dag128).
5. ONE SOURCE: both carriers compiled from the identical _SRC, differing only by -DCARRIER_U128 (the dedup).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
from fractions import Fraction
import jea_core
from jea_generator_dag import build_dag
from jea_generator_strat import _lh

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void combine(volatile int* Kbuf, volatile int* obsmax, volatile int* pending, volatile int* mode,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps, int* esc,
    const int* own,const int* own_count, long long* cyc, volatile int* err,
    int nblocks,int maxown,long long maxcyc)
{
    if (threadIdx.x != 0) return;                       // cooperative: one lead thread / block
    int w = blockIdx.x; int oc = own_count[w]; long long c = 0;
    while (*pending > 0) {
        int est = 0;
        if (oc > 0) {
            int slot = own[w*maxown + (int)(c % oc)];
            int Lc = lch[slot], Rc = rch[slot];
            int active = ready[Lc] & ready[Rc] & (1 - ready[slot]);
            if (active & (1 - initf[slot])) {            // the combine (carrier-parameterized)
                if (esc[Lc] | esc[Rc]) { esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); st(al,ah,slot,0); st(bl,bh,slot,0); }
                else {
                    u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc);
                    u128 na, D;
#ifdef CARRIER_U128
                    int o=0; D=dl*dr; o|=(dl!=0)&&(D/dl!=dr);          // u128: division-check (no wider native)
                    if (op[slot]==1){ na=nl*nr; o|=(nl!=0)&&(na/nl!=nr); }
                    else { u128 p1=nl*dr,p2=nr*dl; na=p1+p2; o|=(dr!=0)&&(p1/dr!=nl); o|=(dl!=0)&&(p2/dl!=nr); o|=(na<p1); }
                    if (o){ esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); st(al,ah,slot,0); st(bl,bh,slot,0); }
                    else { st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); }
#else
                    const u128 LIM = ((u128)1) << 64;                  // u64: operands<2^64 -> products fit __int128; escalate >=2^64
                    na = (op[slot]==1) ? (nl*nr) : (nl*dr + nr*dl); D = dl*dr;
                    if (na>=LIM || D>=LIM) {                           // reduce-when-forced, then check
                        u128 x=na,y=D; while(y){ u128 t=x%y; x=y; y=t; } u128 g=x?x:1; u128 rn=na/g, rd=D/g;
                        if (rn>=LIM||rd>=LIM){ esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); }
                        else { st(naNl,naNh,slot,rn); st(naDl,naDh,slot,rd); }
                        st(al,ah,slot,0); st(bl,bh,slot,0);
                    } else { st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); }
#endif
                }
                initf[slot]=1;
            }
            int md=*mode, K=*Kbuf, nowdone=0, s=steps[slot];
            u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot);
            if (active & initf[slot]) {
                if (esc[slot]) { st(vNl,vNh,slot,0); st(vDl,vDh,slot,1); nowdone=1; }
                else if (aa==0 && bb==0) { st(vNl,vNh,slot, ld(naNl,naNh,slot)); st(vDl,vDh,slot, ld(naDl,naDh,slot)); nowdone=1; }
                else if (md==1) {                          // EAGER windowed gcd
                    for (int j=0;j<K;j++){ if (bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }
                    st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
                    if (bb==0){ u128 g=aa?aa:(u128)1; st(vNl,vNh,slot, ld(naNl,naNh,slot)/g); st(vDl,vDh,slot, ld(naDl,naDh,slot)/g); nowdone=1; }
                } else { st(vNl,vNh,slot, ld(naNl,naNh,slot)); st(vDl,vDh,slot, ld(naDl,naDh,slot)); nowdone=1; }  // LAZY
            }
            int wasready=ready[slot]; ready[slot]=wasready|nowdone; atomicSub((int*)pending, ready[slot]-wasready);
            est = nowdone ? (s>0?s:1) : 0;
        }
        atomicMax((int*)obsmax, est); *Kbuf = relax_q(*Kbuf, *obsmax); __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cyc[w] = c;
}
'''
# ONE source, compiled per carrier (the typedef switch) -- the dedup of dag/dag128/dag_mode combine bodies
def _ascii(s):
    assert s.isascii(); return s
_KERN = {64:  cp.RawKernel(_ascii(_SRC), "combine", options=("--device-int128",)),
         128: cp.RawKernel(_ascii(_SRC), "combine", options=("--device-int128", "-DCARRIER_U128"))}


def run_engine(g, carrier=64, mode=1, K0=4, maxcyc=4_000_000):
    """The C1 engine: evaluate a DAG with carrier in {64,128} (typedef) and mode in {1=eager,0=lazy}."""
    ker = _KERN[carrier]
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]; nblocks = min(20, nsm)
    N, L = g["N"], g["L"]
    vNl, vNh = _lh(g["vN"]); vDl, vDh = _lh(g["vD"])
    lch = cp.asarray(g["lch"], cp.int32); rch = cp.asarray(g["rch"], cp.int32); op = cp.asarray(g["op"], cp.int32)
    ready = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    initf = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    z = lambda: cp.zeros(N, cp.uint64); al,ah,bl,bh,naNl,naNh,naDl,naDh = z(),z(),z(),z(),z(),z(),z(),z()
    steps = cp.zeros(N, cp.int32); esc = cp.zeros(N, cp.int32)
    combines = list(range(L, N)); per = [[] for _ in range(nblocks)]
    for k, ci in enumerate(combines): per[k % nblocks].append(ci)
    maxown = max((len(x) for x in per), default=1) or 1
    own = np.full((nblocks, maxown), -1, np.int32)
    for wi in range(nblocks):
        for j, ci in enumerate(per[wi]): own[wi, j] = ci
    own_count = cp.asarray([len(x) for x in per], cp.int32); own = cp.asarray(own.ravel(), cp.int32)
    Kbuf = cp.full(1, K0, cp.int32); obsmax = cp.zeros(1, cp.int32); pending = cp.full(1, len(combines), cp.int32)
    modebuf = cp.full(1, mode, cp.int32); cyc = cp.zeros(nblocks, cp.int64); err = cp.zeros(1, cp.int32)
    ker((nblocks,), (32,), (Kbuf, obsmax, pending, modebuf, vNl,vNh,vDl,vDh, lch,rch,op, ready,initf,
                            al,ah,bl,bh, naNl,naNh,naDl,naDh, steps,esc, own,own_count, cyc,err,
                            np.int32(nblocks), np.int32(maxown), np.int64(maxcyc)))
    cp.cuda.Stream.null.synchronize()
    r = g["root"]; gNl,gNh,gDl,gDh,ge = vNl.get(),vNh.get(),vDl.get(),vDh.get(),esc.get()
    rn = (int(gNh[r])<<64)|int(gNl[r]); rd = (int(gDh[r])<<64)|int(gDl[r])
    nc = sum(1 for i in range(L,N) if ge[i]==0 and ((int(gNh[i])<<64)|int(gNl[i])) and
             gcd((int(gNh[i])<<64)|int(gNl[i]), (int(gDh[i])<<64)|int(gDl[i])) != 1)
    return dict(rn=rn, rd=rd, esc_root=int(ge[r]), nesc=int(ge.sum()), noncanon=nc,
                pending=int(pending.get()[0]), err=int(err.get()[0]))


def build_mul_tree(vals):
    vN=list(vals); vD=[1]*len(vals); lch=[-1]*len(vals); rch=[-1]*len(vals); op=[-1]*len(vals)
    fv=[Fraction(v,1) for v in vals]; level=list(range(len(vals)))
    while len(level)>1:
        nxt=[]
        for i in range(0,len(level)-1,2):
            li,ri=level[i],level[i+1]; idx=len(vN); vN.append(0);vD.append(0);lch.append(li);rch.append(ri);op.append(1)
            fv.append(fv[li]*fv[ri]); nxt.append(idx)
        if len(level)%2: nxt.append(level[-1])
        level=nxt
    return dict(vN=vN,vD=vD,lch=lch,rch=rch,op=op,L=len(vals),N=len(vN),root=level[0],truth=fv[level[0]])


if __name__ == "__main__":
    g = build_dag(128, 3); truth = g["truth"]
    e = run_engine(g, 64, 1); l = run_engine(g, 64, 0)
    w1 = Fraction(e["rn"], e["rd"]) == truth and e["esc_root"] == 0 and e["noncanon"] == 0 and e["err"] == 0
    w2 = Fraction(l["rn"], l["rd"]) == truth and l["esc_root"] == 0 and l["noncanon"] > 0 and l["err"] == 0

    g2 = build_dag(256, 3); t2 = g2["truth"]; tb = max(abs(t2.numerator), t2.denominator).bit_length()
    e64 = run_engine(g2, 64, 1); e128 = run_engine(g2, 128, 1)
    w3 = tb > 64 and e64["esc_root"] == 1 and e128["esc_root"] == 0 and Fraction(e128["rn"], e128["rd"]) == t2

    primes = [1000000007,1000000009,1000000021,1000000033,1000000087,1000000093,1000000097,1000000103]
    gm = build_mul_tree(primes); ov = run_engine(gm, 128, 1)
    w4 = ov["esc_root"] == 1 and gm["truth"].numerator.bit_length() > 128

    w5 = _KERN[64].code == _KERN[128].code                    # identical source, differ only by -D

    print("C1 -- one parameterized combine (carrier typedef + mode/K), collapsing dag / dag128 / dag_mode\n")
    print(f"1. EAGER u64 == truth, canonical: {w1}  (root {e['rn']}/{e['rd']})")
    print(f"2. LAZY u64 == truth (reduced), non-canonical={l['noncanon']}>0: {w2}")
    print(f"3. CARRIER WIDENS (truth {tb}b >64): carrier64 esc={e64['esc_root']}, carrier128 exact={Fraction(e128['rn'],e128['rd'])==t2}: {w3}")
    print(f"4. u128 OVERFLOW (all-mul {gm['truth'].numerator.bit_length()}b >128): carrier128 esc={ov['esc_root']}: {w4}")
    print(f"5. ONE SOURCE (both carriers from identical _SRC, only -DCARRIER_U128 differs): {w5}")
    ok = w1 and w2 and w3 and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — C1: the combine body is now ONE CUDA source, carrier a compile-time")
    print(f"  typedef switch, mode/K runtime params. Reproduces dag (u64 eager) / dag128 (u128 + escalate) /")
    print(f"  dag_mode (eager,lazy) -- the copy-pasted combine bodies, deduplicated. NEXT: C2 (schedule as a")
    print(f"  strategy over this combine), then C3 (carrier ops), C4 (intern+oracle), C5 (regression runner).")
