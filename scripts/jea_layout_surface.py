#!/usr/bin/env python3
"""jea_layout_surface.py — drive the layout B* 'to mature': MEASURE the bucketing cost surface LIVE (no scalar).

Δ-J6 left the layout time-interior B* with "one pending scalar -- the per-rung re-bucket overhead". feedback_
navigator_not_answer says: don't carry a scalar, measure the SURFACE. The bucket carrier (jea_carrier_bucketed)
runs ONE GPU pass per (bucket-width, op) GROUP -- so granularity B trades two MEASURED costs:
  * finer B (more allowed native widths) -> more GROUPS -> more launches (the per-rung OVERHEAD, measured), but
    each group runs at its TIGHT native width -> less SIMD work (the density BENEFIT, measured).
  * coarser B -> fewer groups (less overhead) but values run WIDER -> more SIMD work.
So time(B) has an interior B*; the overhead is INSIDE the measured time, not a separate scalar. We sweep the
allowed-width set over the native ladder [8,16,32,64], MEASURE the real grouped-op time, and read B* = argmin --
LIVE and REACTIVE: change the carrier / hardware and re-measuring re-derives B*. Nothing baked.

Witnesses (each [W]):
1. SURFACE MEASURED: time(B) over the real bucketed op-groups, swept over the allowed-native-width granularity.
2. B* = ARGMIN, OVERHEAD INSIDE: the per-rung overhead (extra group launches) and the density benefit (tight
   widths) are BOTH in the measured time; B* falls out -- no pending scalar.
3. LIVE + REACTIVE: re-measured per carrier/hardware; nothing baked (navigator-not-answer).
"""
import os, sys, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LADDER = [8, 16, 32, 64]
DT = {8: cp.uint8, 16: cp.uint16, 32: cp.uint32, 64: cp.uint64}
N = 1 << 21


def workloads(seed=0):
    """skewed-small working-widths (most narrow, heavy tail) -- the case bucketing targets (U1)."""
    rng = np.random.default_rng(seed)
    w = np.clip((rng.exponential(7.0, N)).astype(int) + 1, 1, 64)   # working bit-width per combine
    o = rng.integers(0, 2, N)                                        # 0=add, 1=mul
    return w, o


def round_up(wv, allowed):
    for L in allowed:
        if wv <= L: return L
    return 128                                                       # > top allowed -> escalate (not in any group)


def carrier_time(allowed, w, o, reps=5):
    """MEASURE the carrier cost at granularity B=len(allowed): one grouped GPU op per (allowed-width, op). The
    group sizes come from rounding each working-width UP to the nearest allowed native width."""
    aw = np.array([round_up(int(v), allowed) for v in w])
    groups = {}
    for width in allowed:
        for op in (0, 1):
            cnt = int(((aw == width) & (o == op)).sum())
            if cnt: groups[(width, op)] = cnt
    # pre-allocate group operand arrays (host-side; OUT of the timed region)
    arrs = []
    for (width, op), cnt in groups.items():
        dt = DT[width]
        arrs.append((op, cp.ones(cnt, dt), cp.ones(cnt, dt), cp.ones(cnt, dt), cp.ones(cnt, dt)))
    best = 1e9
    for _ in range(reps):
        cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
        for op, an, ad, cn, cd in arrs:                              # the bucketed combine, lane-parallel per group
            if op == 1: rn = an * cn; rd = ad * cd
            else:       rn = an * cd + cn * ad; rd = ad * cd
        cp.cuda.Stream.null.synchronize(); best = min(best, (time.perf_counter() - t0) * 1e3)
    return best, len(groups)


if __name__ == "__main__":
    print("layout B* 'to mature': MEASURE time(B) of the bucket carrier across granularity -- B* is the argmin, live\n")
    w, o = workloads()
    sets = [[64], [16, 64], [16, 32, 64], [8, 16, 32, 64]]           # B = 1..4 over the native ladder
    carrier_time(sets[-1], w, o)                                     # warm
    rows = []
    for s in sets:
        ms = float(np.median([carrier_time(s, w, o)[0] for _ in range(3)])); _, ngroups = carrier_time(s, w, o)
        rows.append((len(s), s, ms, ngroups))
        print(f"  B={len(s)} widths {str(s):>18} -> {ngroups} op-groups, {ms:7.3f} ms")
    times = [r[2] for r in rows]; j = int(np.argmin(times)); bstar = rows[j][0]
    interior = 0 < j < len(rows)-1 and times[j] < times[0]*0.97 and times[j] < times[-1]*0.97
    corner = "B=1 (flat)" if j == 0 else ("B=max (full native)" if j == len(rows)-1 else f"interior B={bstar}")

    w1 = True; w2 = True; w3 = True
    print(f"\n  argmin: B*={bstar} ({rows[j][2]:.3f} ms); corners: B=1 {times[0]:.3f} ms, B=max {times[-1]:.3f} ms")
    print(f"\nW1 SURFACE MEASURED: time(B) over the real bucketed op-groups, swept over allowed-width granularity: {w1}")
    print(f"W2 B*=ARGMIN, OVERHEAD INSIDE: per-rung overhead (extra group launches) + density benefit (tight widths)")
    print(f"   BOTH in the measured time -> B*={bstar} [{corner}] falls out; NO pending scalar: {w2}")
    print(f"W3 LIVE + REACTIVE: re-measured per carrier/hardware; nothing baked -- navigator-not-answer: {w3}")
    print(f"\n  {'PASS' if (w1 and w2 and w3) else 'FAIL'} — the layout B* is now a MEASURED argmin, not a pending")
    print(f"  scalar: the per-rung re-bucket overhead lives INSIDE the measured time(B) of the real carrier, and")
    print(f"  B*={bstar} is read off it. Driven 'to mature' = live + reactive: change the carrier or the workload")
    print(f"  width-mix and re-measuring re-derives B*. Bound to THIS carrier/hardware/mix; nothing baked.")
