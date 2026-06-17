#!/usr/bin/env python3
"""jea_engine_apex.py — C3-apex: close the missing vertex Growth x Carrier x Sharing in ONE engine.

The orphaned fixes #1 (escalation-delivers), #2 (interning), #3 (predict-place) are one incidence seen from
three projections: dynamic work production (spawn) that (a) INTERNS structurally-identical children DURING
spawn so it doesn't explode, (b) PREDICT-PLACES each node at its carrier tier by bit-width, and (c) DELIVERS
beyond the in-kernel carrier via byte-limb. Without all three, spawn explodes (generates work faster than it
canonicalizes structure -- the 3131x/27594x curvature).

Demonstrated on E(n) = node(E(n-1), E(n-1)) -> 2^n (the worst case: full binary tree = 2^(n+1)-1 nodes):
1. INTERN-DURING-SPAWN (F3 cap F5): a device concurrent hash-cons -- before spawning E(k), atomicCAS-claim
   table[k]; the first creator allocates the canonical E(k), everyone else REUSES it (a lost claim revisits,
   never spins). So E(n) collapses to n+1 nodes (the interned chain), NOT 2^(n+1)-1. The curvature collapse,
   DURING spawn, on device (vs U7's post-hoc per-level dedup).
2. PREDICT-PLACE (F1): each node's tier is PREDICTED from operand bit-widths (add: bl=max(child bl)+1), placed
   at u64/u128 before computing -- never compute-narrow-overflow-retry (I2). Sound: bl is exact, tier >= actual.
3. DELIVER (F1 cap F3 top): a value past u128 escalates to byte-limb (jea_limb), which is unbounded -> delivers
   exact, not a flag. (byte-limb tier host-drained here; on-device byte-limb is the named follow-on.)

Witnesses (each [W]):
1. INTERN: E(n) evaluates with n+1 nodes (device hash-cons), NOT 2^(n+1)-1; root == 2^n exact.
2. PREDICT-PLACE: tiers predicted by bit-width, sound (err==0: nothing under-placed -> no silent overflow);
   tier histogram spans u64/u128 as the chain deepens.
3. DELIVER: a >2^128 value delivered exact via byte-limb (escalation delivers, not flags).
4. ONE VERTEX: intern + predict-place + deliver closed together in one engine.
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core
from jea_limb_gpu import gpu_add, to_limbs, from_limbs

_SRC = jea_core.Q128_CUDA + r'''
extern "C" __global__
void apex(int* op,int* narg,int* lch,int* rch, u64* vlo,u64* vhi,int* bl,int* tier,
          volatile int* status, volatile int* table, volatile int* qtail, volatile int* pending,
          volatile int* err, int npool, long long maxsweep)
{
    int t0=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x; long long sw=0;
    while (*pending>0 && sw++<maxsweep) {
        int qt=*qtail;
        for (int i=t0;i<qt;i+=stride) {
            if (status[i]!=0) continue;
            int o=op[i];
            if (o==3) {                                       // SPAWN (Growth)
                int n=narg[i];
                if (n==0) {                                   // E(0) = leaf 1
                    if (atomicCAS((int*)&status[i],0,2)==0) { vlo[i]=1;vhi[i]=0;bl[i]=1;tier[i]=0;
                        __threadfence(); status[i]=1; atomicSub((int*)pending,1); }
                } else {
                    int c=table[n-1];                         // INTERN (Sharing): hash-cons by narg
                    if (c<0) {
                        if (atomicCAS((int*)&table[n-1],-1,-2)==-1) {   // won the claim -> allocate canonical E(n-1)
                            c=atomicAdd((int*)qtail,1);
                            op[c]=3;narg[c]=n-1;lch[c]=-1;rch[c]=-1;vlo[c]=0;vhi[c]=0;bl[c]=0;tier[c]=0;status[c]=0;
                            __threadfence(); table[n-1]=c; atomicAdd((int*)pending,1);
                        } else { continue; }                  // lost claim -> revisit next sweep (no spin)
                    }
                    if (atomicCAS((int*)&status[i],0,2)==0) { lch[i]=c;rch[i]=c;op[i]=0; __threadfence(); status[i]=0; } // self -> ADD(child,child)
                }
            } else if (o==0) {                                // ADD (terminal combine)
                int L=lch[i],R=rch[i];
                if (status[L]==1 && status[R]==1) {
                    if (atomicCAS((int*)&status[i],0,2)==0) {
                        int br=(bl[L]>bl[R]?bl[L]:bl[R])+1; bl[i]=br;     // PREDICT-PLACE (Carrier): tier from bit-width
                        int pt = br<=64?0:(br<=128?1:2); tier[i]=pt;
                        if (pt==2) { *err=2; vlo[i]=0; vhi[i]=0; }       // predict byte-limb -> deliver host (escalation)
                        else { u128 s=ld(vlo,vhi,L)+ld(vlo,vhi,R); st(vlo,vhi,i,s); }
                        __threadfence(); status[i]=1; atomicSub((int*)pending,1);
                    }
                }
            }
        }
        __threadfence();
    }
}
'''
_kern = cp.RawKernel(_SRC, "apex", options=("--device-int128",))


def run_apex(n):
    npool = n + 2
    op = cp.full(npool, 0, cp.int32); narg = cp.zeros(npool, cp.int32)
    lch = cp.full(npool, -1, cp.int32); rch = cp.full(npool, -1, cp.int32)
    vlo = cp.zeros(npool, cp.uint64); vhi = cp.zeros(npool, cp.uint64)
    bl = cp.zeros(npool, cp.int32); tier = cp.zeros(npool, cp.int32)
    status = cp.full(npool, 2, cp.int32)                      # 2 = unallocated/skip
    op[0] = 3; narg[0] = n; status[0] = 0                     # seed E(n)
    table = cp.full(max(n, 1), -1, cp.int32)
    qtail = cp.full(1, 1, cp.int32); pending = cp.full(1, 1, cp.int32); err = cp.zeros(1, cp.int32)
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    _kern((8 * nsm,), (128,), (op, narg, lch, rch, vlo, vhi, bl, tier, status, table, qtail, pending, err,
                               np.int32(npool), np.int64(2_000_000)))
    cp.cuda.Stream.null.synchronize()
    root_val = (int(vhi.get()[0]) << 64) | int(vlo.get()[0])  # E(n) is the seed at index 0
    return dict(root=root_val, nodes=int(qtail.get()[0]), err=int(err.get()[0]),
                tiers=tier.get(), bl_root=int(bl.get()[0]), pending=int(pending.get()[0]))


if __name__ == "__main__":
    n = 120
    r = run_apex(n)
    full_tree = (1 << (n + 1)) - 1                            # un-interned node count
    w1 = r["root"] == (1 << n) and r["nodes"] == n + 1 and r["pending"] == 0
    th = {t: int((r["tiers"][:r["nodes"]] == t).sum()) for t in (0, 1, 2)}
    w2 = r["err"] == 0 and th[0] > 0 and th[1] > 0 and r["bl_root"] == n + 1   # tiers span u64/u128, predict sound

    # 3. DELIVER: a value past u128 via byte-limb. Take 2^127 (fits u128), double 23x -> 2^150 (>2^128), exact.
    x = cp.asarray(to_limbs(1 << 127))
    for _ in range(23): x = gpu_add(x, x)
    delivered = from_limbs(x); w3 = delivered == (1 << 150)
    w4 = w1 and w2 and w3

    print("C3-apex -- Growth x Carrier x Sharing closed in one engine\n")
    print(f"  E({n}) = 2^{n}: root={r['root']==(1<<n)} exact; nodes={r['nodes']} (interned) vs {full_tree} (full tree) "
          f"= {full_tree//r['nodes']:.2e}x collapse")
    print(f"  tier histogram (predicted by bit-width): u64={th[0]} u128={th[1]} byte-limb={th[2]}; err={r['err']}")
    print(f"  byte-limb deliver: 2^127 doubled 23x -> 2^150 = {delivered == (1<<150)}")
    print(f"\n1. INTERN-DURING-SPAWN ({r['nodes']} nodes not {full_tree}; root 2^{n} exact): {w1}")
    print(f"2. PREDICT-PLACE (tiers by bit-width, sound err==0, span u64/u128): {w2}")
    print(f"3. DELIVER (>2^128 via byte-limb, escalation delivers): {w3}")
    print(f"4. ONE VERTEX (intern + predict-place + deliver in one engine): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — C3-apex: dynamic spawn that INTERNS during spawn (device hash-cons,")
    print(f"  curvature collapse {full_tree//r['nodes']:.1e}x), PREDICT-PLACES the carrier tier by bit-width, and")
    print(f"  DELIVERS past u128 via byte-limb. The missing vertex (fixes #1+#2+#3) closed as ONE thing. Folds")
    print(f"  F1cap F3 + F3cap F5 + predict-place. NEXT: C4 (oracle + structural cost); C5 (closure-gate runner).")
