#!/usr/bin/env python3
# SIDE-TRAIL (off the main spine) -- explored, then absorbed/superseded; not a rung of the linear ladder. See ../00_SYLLABUS.md
"""jea_generator_telemring.py — increment (3), honestly scoped. The "telemetry-ring as an
O(1)-observe optimization" is MOOT: (5)'s distributed atomicMax(obsmax) already made observe
O(1); the dedicated-controller scan that motivated a ring is gone. The ring's GENUINE remaining
value is that obsmax is MONOTONIC (only climbs) so K can never relax DOWN. A windowed telemetry
RING (recent-W samples, oldest overwritten) gives a RECENT-max, so the controller tracks a
TIME-VARYING workload in BOTH directions — needed for the persistent evaluator (many traces over
time), not a one-shot fold.

This demonstrates exactly that: a synthetic depth schedule (shallow -> deep -> shallow) is pushed
into an on-device telemetry ring by free-running cooperative generators; K is relaxed off the
ring's windowed-max. Side by side, a baseline K is relaxed off the monotonic obsmax. The ring K
climbs AND relaxes (tracks both ways); the monotonic K climbs and STAYS HIGH (cannot track down).
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core                                  # strict shared structure

_SRC = jea_core.CTRL_CUDA + r'''
extern "C" __global__
void telemring(
    volatile int* Kring, volatile int* Kmono, volatile int* obsmax,
    int* tr, volatile int* head, int RW,
    int* klog_ring, int* klog_mono, int Tlog,
    int P, long long total_pushes)
{
    if (threadIdx.x != 0) return;
    while (true) {
        int h = atomicAdd((int*)head, 1);          // global push index -> consistent phase
        if (h >= total_pushes) break;
        int phase = (h < P) ? 0 : (h < 2*P) ? 1 : 2;   // shallow -> DEEP -> shallow
        int depth = (phase==1) ? 200 : 3;
        // --- windowed telemetry RING: recent-W samples, oldest overwritten ---
        tr[h % RW] = depth; __threadfence();
        int rmax = 0; for (int i=0;i<RW;i++){ int v=tr[i]; rmax = v>rmax?v:rmax; }   // recent-max
        *Kring = relax_q(*Kring, rmax);
        // --- monotonic baseline: obsmax only climbs ---
        atomicMax((int*)obsmax, depth);
        *Kmono = relax_q(*Kmono, *obsmax);
        __threadfence();
        if (h < Tlog) { klog_ring[h] = *Kring; klog_mono[h] = *Kmono; }
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "telemring")


def run(P=3000, RW=64, K0=4):
    nblocks = min(20, cp.cuda.Device().attributes["MultiProcessorCount"])
    total = 3 * P
    Tlog = total
    Kring = cp.full(1, K0, cp.int32); Kmono = cp.full(1, K0, cp.int32); obsmax = cp.zeros(1, cp.int32)
    tr = cp.full(RW, 3, cp.int32); head = cp.zeros(1, cp.int32)
    klog_ring = cp.full(Tlog, -1, cp.int32); klog_mono = cp.full(Tlog, -1, cp.int32)
    _kern((nblocks,), (32,),
          (Kring, Kmono, obsmax, tr, head, np.int32(RW), klog_ring, klog_mono, np.int32(Tlog),
           np.int32(P), np.int64(total)))
    cp.cuda.Stream.null.synchronize()
    return P, klog_ring.get(), klog_mono.get(), int(Kring.get()[0]), int(Kmono.get()[0])


if __name__ == "__main__":
    P, lr, lm, kr_final, km_final = run(P=3000, RW=64)
    # sample the trajectory at phase-representative points (by global push index h)
    def at(frac):
        i = int(frac * 3 * P); i = min(i, len(lr)-1)
        return int(lr[i]), int(lm[i])
    pts = [(0.10, "shallow #1"), (0.45, "DEEP"), (0.65, "deep->shallow"), (0.90, "shallow #2")]
    print("increment (3) windowed telemetry RING vs monotonic obsmax (on-device, shifting workload)\n")
    print(f"  schedule by global push index: shallow(d=3) -> DEEP(d=200) -> shallow(d=3), {3*P} pushes, ring W=64\n")
    print(f"  {'phase':16s} {'K (ring, windowed)':>20s} {'K (mono, baseline)':>20s}")
    for frac, name in pts:
        kr, km = at(frac)
        print(f"  {name:16s} {kr:>20d} {km:>20d}")
    # the test: ring K must RELAX DOWN in the final shallow phase; mono K must stay high.
    kr_end, km_end = at(0.92)
    kr_deep, _ = at(0.45)
    tracks_up   = kr_deep >= 64
    ring_relaxes = kr_end < kr_deep
    mono_stuck   = km_end >= kr_deep
    ok = tracks_up and ring_relaxes and mono_stuck
    print(f"\n  ring climbed in DEEP ({kr_deep}) then RELAXED in shallow#2 ({kr_end}): up+down tracking = {ring_relaxes}")
    print(f"  monotonic stayed high in shallow#2 ({km_end}): cannot track down = {mono_stuck}")
    print(f"\n  INCREMENT (3) {'PASS' if ok else 'FAIL'} — the telemetry RING gives windowed (recent) observation,")
    print(f"  so K tracks a time-varying workload BOTH ways; monotonic obsmax can only climb. (O(1)-observe")
    print(f"  was already done by distributed atomicMax in (5); the ring's real contribution is the windowing.)")
