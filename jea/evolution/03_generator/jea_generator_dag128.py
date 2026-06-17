#!/usr/bin/env python3
"""jea_generator_dag128.py — increment (2): the 128-bit CARRIER for the streaming DAG fold.
The carrier is the only thing that changes from jea_generator_dag.py (u64); the generator body,
the monotonic readiness gate, the cooperative control are identical — "carrier is a typedef".
In CUDA the swap is: each ℚ component (num,den; the gcd residue a,b; the unreduced na,D) is now
an unsigned __int128 stored as a (lo,hi) u64 lane pair, with nvrtc --device-int128.

ESCALATE-DON'T-TRUNCATE (charter #4): the combine's products (nl*nr, nl*dr+nr*dl, dl*dr) can
exceed 128 bits. Each is OVERFLOW-CHECKED (division/carry test, the jea_gpu _combine_level_q
discipline) and a sticky `escalate` flag is set — DETECTED, never silently wrapped. This is the
exact point u64 fails: a fold whose intermediates exceed 2^64 wraps silently in u64 (wrong) but
is exact in 128-bit; one exceeding 2^128 sets the escalate flag (the signal to widen further).
Verified: (a) small fold == the u64 result; (b) a fold with intermediates > 2^64 is bit-exact vs
Python (u64 would wrap), escalate=0; (c) a fold exceeding 2^128 sets escalate=1 (not wrapped).
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
import jea_core                                  # strict shared structure (control law, Q128, ASCII gate)

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void generator_dag128(
    volatile int* Kbuf, volatile int* obsmax, volatile int* pending, volatile int* escalate,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready,int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps,
    const int* own,const int* own_count, long long* cycles_by, volatile int* err,
    int nblocks,int maxown,long long maxcyc)
{
    if (threadIdx.x != 0) return;
    int w = blockIdx.x; int oc = own_count[w]; long long c=0;
    while (*pending > 0) {
        int est=0;
        if (oc>0) {
            int slot = own[w*maxown + (int)(c % oc)];
            int Lc=lch[slot], Rc=rch[slot];
            int active = ready[Lc] & ready[Rc] & (1 - ready[slot]);
            if (active & (1 - initf[slot])) {
                u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc);
                u128 na, D = dl*dr; int o = 0;
                o |= (dl!=0) && (D/dl != dr);                 // den product overflow
                if (op[slot]==1) {                            // multiply
                    na = nl*nr; o |= (nl!=0) && (na/nl != nr);
                } else {                                      // add
                    u128 p1=nl*dr, p2=nr*dl; na=p1+p2;
                    o |= (dr!=0) && (p1/dr != nl);
                    o |= (dl!=0) && (p2/dl != nr);
                    o |= (na < p1);                           // unsigned add carry-out
                }
                if (o) *escalate = 1;                          // DETECTED, never wrapped
                st(naNl,naNh,slot,na); st(naDl,naDh,slot,D);
                st(al,ah,slot,na);    st(bl,bh,slot,D);  initf[slot]=1;
            }
            int K=*Kbuf;
            u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot); int s=steps[slot];
            for (int j=0;j<K;j++){ if(active && bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }
            st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
            int nowdone = active && (bb==0);
            if (nowdone) {
                u128 g = (aa!=0)?aa:(u128)1;
                st(vNl,vNh,slot, ld(naNl,naNh,slot)/g);
                st(vDl,vDh,slot, ld(naDl,naDh,slot)/g);
            }
            int wasr=ready[slot]; ready[slot]=wasr|nowdone;
            atomicSub((int*)pending, ready[slot]-wasr);
            est = nowdone ? s : (active ? s+1 : 0);
        }
        atomicMax((int*)obsmax, est);
        *Kbuf = relax_q(*Kbuf, *obsmax); __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cycles_by[w]=c;
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_dag128", int128=True)
residency = jea_core.residency


def _lh(vals):
    vals = [int(v) for v in vals]
    lo = cp.asarray([v & ((1<<64)-1) for v in vals], cp.uint64)
    hi = cp.asarray([(v >> 64) & ((1<<64)-1) for v in vals], cp.uint64)
    return lo, hi


def build_dag(leaves, ops_seed, force_op=None):
    """leaves: list of (num,den) (arbitrary precision ints). +/x tree (random, or all force_op).
    Returns flat arrays + root + Python-Fraction truth."""
    rng = np.random.default_rng(ops_seed)
    vN = [int(n) for (n,_d) in leaves]; vD = [int(d) for (_n,d) in leaves]
    L = len(leaves); lch=[-1]*L; rch=[-1]*L; op=[-1]*L
    fval = [Fraction(vN[i], vD[i]) for i in range(L)]
    level = list(range(L))
    while len(level) > 1:
        nxt=[]
        for i in range(0, len(level), 2):
            li, ri = level[i], level[i+1]; o = force_op if force_op is not None else int(rng.integers(0,2))
            idx=len(vN); vN.append(0); vD.append(0); lch.append(li); rch.append(ri); op.append(o)
            fval.append(fval[li]*fval[ri] if o==1 else fval[li]+fval[ri]); nxt.append(idx)
        level=nxt
    return dict(vN=vN,vD=vD,lch=lch,rch=rch,op=op,L=L,N=len(vN),root=level[0],truth=fval[level[0]])


def run(leaves, ops_seed=3, K0=4, maxcyc=5_000_000, force_op=None):
    nblocks = min(20, cp.cuda.Device().attributes["MultiProcessorCount"])
    g = build_dag(leaves, ops_seed, force_op); N=g["N"]; L=g["L"]
    per_sm, max_resident, _nsm, regs = residency(_kern, 32); assert nblocks <= max_resident
    vNl,vNh = _lh(g["vN"]); vDl,vDh = _lh(g["vD"])
    lch=cp.asarray(g["lch"],cp.int32); rch=cp.asarray(g["rch"],cp.int32); op=cp.asarray(g["op"],cp.int32)
    ready=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    initf=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    z=lambda: cp.zeros(N,cp.uint64)
    al,ah,bl,bh,naNl,naNh,naDl,naDh = z(),z(),z(),z(),z(),z(),z(),z()
    steps=cp.zeros(N,cp.int32)
    comb=list(range(L,N)); pb=[[] for _ in range(nblocks)]
    for k,ci in enumerate(comb): pb[k%nblocks].append(ci)
    maxown=max((len(x) for x in pb),default=1) or 1
    own=np.full((nblocks,maxown),-1,np.int32)
    for wv in range(nblocks):
        for j,ci in enumerate(pb[wv]): own[wv,j]=ci
    own_count=cp.asarray([len(x) for x in pb],cp.int32); own=cp.asarray(own.ravel(),cp.int32)
    Kbuf=cp.full(1,K0,cp.int32); obsmax=cp.zeros(1,cp.int32); pending=cp.full(1,len(comb),cp.int32)
    escalate=cp.zeros(1,cp.int32); cyc=cp.zeros(nblocks,cp.int64); err=cp.zeros(1,cp.int32)
    _kern((nblocks,),(32,),
        (Kbuf,obsmax,pending,escalate,vNl,vNh,vDl,vDh,lch,rch,op,ready,initf,
         al,ah,bl,bh,naNl,naNh,naDl,naDh,steps,own,own_count,cyc,err,
         np.int32(nblocks),np.int32(maxown),np.int64(maxcyc)))
    cp.cuda.Stream.null.synchronize()
    r=g["root"]
    rn=(int(vNh.get()[r])<<64)|int(vNl.get()[r]); rd=(int(vDh.get()[r])<<64)|int(vDl.get()[r])
    return dict(g=g,rn=rn,rd=rd,pending=int(pending.get()[0]),escalate=int(escalate.get()[0]),
                err=int(err.get()[0]),regs=regs,per_sm=per_sm,max_resident=max_resident,launched=nblocks)


if __name__ == "__main__":
    U64 = 1 << 64; U128 = 1 << 128
    print("increment (2) 128-bit CARRIER for the streaming DAG fold (escalate-don't-truncate)\n")

    # (a) small: matches the u64 build's regime
    a = run([(int(n),int(d)) for n,d in zip([1,2,3,1,2,3,1,2],[1,2,1,2,1,2,1,2])], ops_seed=3)
    a_ok = a["rd"] and Fraction(a["rn"],a["rd"]) == a["g"]["truth"] and a["escalate"]==0 and a["err"]==0
    print(f"  (a) small fold: root {a['rn']}/{a['rd']} == Python {a['g']['truth']}  escalate={a['escalate']}  -> {'OK' if a_ok else 'FAIL'}")

    # (b) ALL-MULTIPLY of 4 big primes: root = product > 2^64, < 2^128. u64 would WRAP; 128-bit exact.
    primes4 = [2_000_003, 2_000_029, 2_000_039, 2_000_081]
    b = run([(p,1) for p in primes4], force_op=1)
    val = max(abs(b["rn"]), b["rd"])
    b_ok = b["rd"] and Fraction(b["rn"],b["rd"]) == b["g"]["truth"] and U64 <= val < U128 and b["escalate"]==0 and b["err"]==0
    print(f"  (b) >2^64 fold: root = {b['rn']}/{b['rd']} = {val.bit_length()} bits ({U64<=val}: >2^64, {val<U128}: <2^128)")
    print(f"      root == Python (u64 would WRAP here): {Fraction(b['rn'],b['rd'])==b['g']['truth'] if b['rd'] else False}  escalate={b['escalate']}  -> {'OK' if b_ok else 'FAIL'}")

    # (c) ALL-MULTIPLY of 8 big primes: product > 2^128 -> escalate must fire (detected, not wrapped).
    primes8 = [2_000_003, 2_000_029, 2_000_039, 2_000_081, 2_000_083, 2_000_113, 2_000_153, 2_000_159]
    c = run([(p,1) for p in primes8], force_op=1)
    c_ok = (c["escalate"] == 1)
    print(f"  (c) >2^128 fold: escalate={c['escalate']} (1=DETECTED, not wrapped)  -> {'OK' if c_ok else 'FAIL'}")

    ok = a_ok and b_ok and c_ok
    print(f"\n  INCREMENT (2) {'PASS' if ok else 'FAIL'} — 128-bit carrier is a clean swap (same body); exact")
    print(f"  where u64 wraps; overflow past 128 bits DETECTED and escalated, never silently truncated.")
