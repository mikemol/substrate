#!/usr/bin/env python3
"""jea_generator_kernel.py — increment (1) of the on-device generator primitive: the
PERSISTENT-MEGAKERNEL SKELETON. Proves the loop MECHANICS in isolation, before any real
fold or ℚ controller:

  * PERSISTENT residency — one kernel launch; blocks LOOP (don't return per work-item).
    Launched ≤ 1 block/SM so every block is co-resident → forward progress guaranteed
    (the deadlock hazard: a worker spinning on a controller that was never scheduled).
  * INTER-BLOCK SYNC WITHOUT grid.sync — a per-tick BARRIER (rendezvous): controller
    publishes K + releases the tick; workers observe + publish telemetry + ack; controller
    waits all acks. Hand-built release/acquire via `volatile` + `__threadfence()` + one
    `atomicAdd`. NO cooperative groups. (HONEST NAMING: this is a BARRIER, not fully-async
    progress — every tick has a global rendezvous. Relaxing that is a later increment.)
  * The ONE primitive (generator_step = observe→step→publish→carry) with step_fn = IDENTITY
    (controller echoes observed max-telemetry as K). Increment (2) swaps in the ℚ relaxation;
    (3) makes the worker step a real gcd-window. Same loop, different step_fn.

SAFETY: every spin loop has a hard `maxspin` cap that sets an error flag and exits — a logic
bug terminates the kernel instead of hanging the GPU. Verified by: err==0 (no deadlock/cap),
all workers logged an IDENTICAL K trajectory (async cross-block visibility is coherent), and
that trajectory transports the injected telemetry schedule (one-tick observe→act lag).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core                                  # the strict shared structure (control law, ASCII gate)

# step_fn = identity (incr 1) / exact-rational relaxation (incr 2). The control law numK/relax_q
# is jea_core.CTRL_CUDA (shared by every variant); this file is ONLY the persistent handshake body.
_SRC = jea_core.CTRL_CUDA + r'''
extern "C" __global__
void generator_skeleton(
    volatile int* K,          // controller PUBLISHES; workers OBSERVE
    volatile int* tick,       // controller PUBLISHES the released tick
    volatile int* acked,      // workers PUBLISH ack; controller OBSERVES
    volatile int* telem,      // [num_workers] workers PUBLISH telemetry; controller OBSERVES
    const int* depth_sched,   // [T] injected synthetic per-tick workload depth
    int* worker_log,          // [num_workers*T] each worker logs the K it saw per tick
    volatile int* err,        // safety flag: set if a spin cap is hit
    int num_workers, int T, long long maxspin, int step_mode)
{
    if (threadIdx.x != 0) return;             // one lead thread/block (demo = INTER-block comms)
    int blk = blockIdx.x;

    if (blk == 0) {
        // ---- CONTROLLER generator: observe telem -> STEP(step_mode) -> publish K -> release tick
        for (int t = 1; t <= T; t++) {
            int mx = 0;                                   // OBSERVE workers' published residue
            for (int w = 0; w < num_workers; w++) { int v = telem[w]; mx = v > mx ? v : mx; }
            if (step_mode == 0) {                         // STEP 0: identity echo (increment 1)
                *K = (t == 1) ? depth_sched[0] : mx;
            } else {                                      // STEP 1: exact-rational relaxation (incr 2)
                if (t > 1) *K = relax_q(*K, mx);          // warm-started from carried *K; t==1 = seed K0
            }
            __threadfence();                              // PUBLISH K
            *acked = 0;   __threadfence();
            *tick = t;    __threadfence();                // RELEASE workers for tick t
            long long spins = 0;
            while (*acked < num_workers) {                // wait all workers observed+acked
                if (++spins > maxspin) { *err = 1; return; }
            }
        }
        *tick = T + 1; __threadfence();                   // done sentinel
    } else {
        // ---- WORKER generator: observe K -> log -> publish telemetry -> ack
        int w = blk - 1, last = 0; long long spins = 0;
        while (true) {
            int t = *tick;                                // OBSERVE current tick
            if (t > T) break;                             // done
            if (t >= 1 && t != last) {
                worker_log[w * T + (t - 1)] = *K;         // OBSERVE published K, log it
                telem[w] = depth_sched[t - 1];            // PUBLISH this tick's workload depth
                __threadfence();
                atomicAdd((int*)acked, 1);                // ACK tick t
                last = t; spins = 0;
            } else if (++spins > maxspin) { *err = 2; break; }
        }
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_skeleton")


def run(depth_sched, step_mode=0, K0=64, maxspin=100_000_000):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = min(20, nsm)                    # ≤ 1 block/SM ⇒ all co-resident, no deadlock
    num_workers = nblocks - 1
    T = len(depth_sched)
    K     = cp.full(1, K0, cp.int32)          # host-seed the carried iterate
    tick  = cp.zeros(1, cp.int32)
    acked = cp.zeros(1, cp.int32)
    telem = cp.zeros(num_workers, cp.int32)
    log   = cp.full(num_workers * T, -1, cp.int32)
    err   = cp.zeros(1, cp.int32)
    sched = cp.asarray(depth_sched, cp.int32)
    _kern((nblocks,), (32,),
          (K, tick, acked, telem, sched, log, err,
           np.int32(num_workers), np.int32(T), np.int64(maxspin), np.int32(step_mode)))
    cp.cuda.Stream.null.synchronize()
    return num_workers, T, log.get().reshape(num_workers, T), int(err.get()[0])


def _oracle_trajectory(sched, K0=64):
    """Replicate the device controller's loop in the oracle's exact-ℚ relaxation, with the
    device's seed+1-tick-lag timing. If the device matches THIS, the on-device ℚ relaxation
    is bit-identical to jea_nedge_model's bridge — same exact ℚ, same decisions."""
    import jea_nedge_model as O
    def relax(K, md):
        tel = O.Telemetry(O.Q(1646,100), O.Q(548,100)/256, O.Q(259,100), md, False)
        down, up = max(1, K//2), min(256, K*2)
        return down if O.bridge(down,K,tel) > 0 else up if O.bridge(up,K,tel) > 0 else K
    K = K0; traj = []
    for t in range(1, len(sched)+1):
        if t > 1: K = relax(K, sched[t-2])    # observed telem from the previous tick (device lag)
        traj.append(K)
    return traj


if __name__ == "__main__":
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    sched = [3, 3, 3, 200, 200, 200, 200, 3, 3, 3, 3, 3]   # shallow → deep burst → shallow

    # ---- INCREMENT (1): identity step_fn — the loop mechanics ----
    nw, T, log, err = run(sched, step_mode=0)
    row0 = list(map(int, log[0]))
    coherent = all(list(map(int, log[w])) == row0 for w in range(nw))
    expect1 = [sched[0]] + [sched[t-1] for t in range(1, T)]      # identity + 1-tick lag
    ok1 = (err == 0 and coherent and row0 == expect1)
    print(f"persistent megakernel: {nw} workers + 1 controller, {T} ticks, {nsm} SMs\n")
    print(f"INCREMENT (1) identity step — loop mechanics:")
    print(f"   K trajectory : {row0}")
    print(f"   err={err}, coherent-across-blocks={coherent}, transports-telemetry={row0==expect1}")
    print(f"   {'PASS' if ok1 else 'FAIL'} — persistent + async observe/publish, no grid.sync, no deadlock\n")

    # ---- INCREMENT (2): exact-ℚ relaxation step_fn — the controller brain, ON-DEVICE ----
    nw, T, log, err = run(sched, step_mode=1, K0=64)
    row0 = list(map(int, log[0]))
    coherent = all(list(map(int, log[w])) == row0 for w in range(nw))
    oracle = _oracle_trajectory(sched, K0=64)
    ok2 = (err == 0 and coherent and row0 == oracle)
    print(f"INCREMENT (2) exact-ℚ relaxation step — the controller brain on-device:")
    print(f"   injected depth   : {sched}")
    print(f"   device K (on-GPU): {row0}")
    print(f"   oracle  K (ℚ ref): {oracle}")
    print(f"   err={err}, coherent={coherent}, device==oracle (bit-identical ℚ decisions)={row0==oracle}")
    print(f"   {'PASS' if ok2 else 'FAIL'} — the scheduler brain runs ON-DEVICE in exact ℚ, async,")
    print(f"   capped; its K-decisions match the oracle exactly (no float, no tolerance).")
