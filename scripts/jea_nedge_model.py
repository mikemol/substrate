#!/usr/bin/env python3
"""jea_nedge_model.py — the on-device scheduler's CONTROL LAW, in exact ℚ, validated as a
closed loop. NOT a client-side analysis you run once: this is the design-time ORACLE for the
controller that will live in the persistent megakernel — the exact-ℚ math the device code is
checked against (as the el-atlas pilots spec the Agda tier). The deployed thing is a feedback
loop resident on the GPU:

   workers (async): fold a window of K steps; emit converged (free slot), CARRY residue
      (resident — charter #2); stream telemetry: depth seen, ALU vs stall  ── sensors ──┐
                                                                                        ▼
   controller (async, NEVER halts): ONE relaxation step of the ℚ conductance network
      per iteration, warm-started from its own current iterate (the equilibrium estimate
      IS its carried residue); the current K / resident-rail is ALWAYS live in the control
      buffer — an ANYTIME estimate, not a periodic solve. Workers read it whenever, no
      barrier. The equilibrium is a MOVING target (telemetry drifts) the iteration chases;
      it never "completes" — taking the converged value would be the unbounded-decision LEM
      trap; the bounded current iterate is the answer (Tarski tower walked, never halted).
   SELF-SIMILAR: the controller is itself a suspended generator continuously forced —
   observe a datum, advance one step, carry the iterate — the same shape as the gcd window
   and the node fold. The scheduler's brain is the same object it schedules.

THE PLANT MODEL (fitted to scripts/jea_roofline.py --ablate; the controller's internal model
of the kernel it steers). Carrier = suspended generator; dual rail E⁺=forced value,
E⁺=suspended continuation (carried residue). Topology: dependent gcd chain SERIES with memory
(starves MLP); independent ALU (mul/ovf) hides by ILP = tropical MAX; windows SERIES, each
re-pays t_mem iff residue NON-resident (global) but only the cheap ALU max iff RESIDENT.
  total(K) = passes(K) · [ t_mem·(resident? once : per-pass) + max(t_gcd(K), t_ovf) ]

THE CONTROL LAW. Each tick the controller reads live telemetry (observed max-depth, measured
t_mem / per-step ALU cost — these DRIFT as the workload changes), evaluates K and its
multiplicative neighbors against the plant model, and the Wheatstone bridge (signed
comparison-of-comparisons) nudges K one step toward the higher conductance. ONE relaxation
step per tick, warm-started from the current iterate — a continuous anytime iteration (the
current K is always the answer), never a wake-solve-sleep cadence. Stability is the property
we validate below: the iterate must TRACK a shifting workload without oscillating.
"""
from fractions import Fraction as Q

# ---- telemetry: what the workers measure and report (drifts over time) ------
class Telemetry:
    def __init__(self, t_mem, c_step, t_ovf, max_depth, resident):
        self.t_mem = Q(t_mem); self.c_step = Q(c_step); self.t_ovf = Q(t_ovf)
        self.max_depth = max_depth; self.resident = resident      # live-measured / live-chosen

def passes(K, max_depth):  return -(-max_depth // K)               # ceil(max_depth / K)
def t_alu(K, tel):         return max(K * tel.c_step, tel.t_ovf)   # ILP co-issue = tropical max

def total(K, tel):
    p = passes(K, tel.max_depth); alu = t_alu(K, tel)
    return (tel.t_mem + p * alu) if tel.resident else p * (tel.t_mem + alu)

def bridge(K_a, K_b, tel):
    """signed comparison-of-comparisons: det>0 ⇒ K_a faster (more conductance)."""
    return Q(1) / total(K_a, tel) - Q(1) / total(K_b, tel)

# ============================================================================
# THE ONE PRIMITIVE. A generator is state ↦ (emit, state′): OBSERVE a bounded window
# (of its own residue + the shared store), STEP once, PUBLISH the emit (into the store),
# CARRY the residue (=state′). Controller and workers are this SAME primitive with
# different step_fn; "async comms" is not a third thing — it is COMPOSITION: one
# generator's publish is another's observe, through the shared STORE. RECURSIVE: a
# step_fn is itself a generator (worker's gcd-window over Euclidean steps; controller's
# relaxation over iterates). Generators all the way down. The on-device build is ONE
# persistent block running this loop, instantiated per role; the store is global memory.
# ============================================================================

def generator_step(state, step_fn, store):
    """observe → step → publish → carry — the single loop body every role runs."""
    emit, state2 = step_fn(state, store)        # step_fn observes (state, store), publishes into store
    return emit, state2                         # returns (emit, residue=state′)

def worker_step(state, store):
    """WORKER instance: observe K from the store, advance ONE gcd-window over its nodes —
    those converging within K emit (freed slots); deeper ones CARRY their residue; publish
    the observed depth as telemetry. (step_fn here is itself the gcd generator, windowed.)"""
    K = store['K']                                              # OBSERVE controller's published residue
    pending = state['pending']
    converged = [n for n in pending if n['depth'] <= K]         # EMIT (freed slots)
    residue   = [n for n in pending if n['depth'] >  K]         # CARRY (suspended generators)
    store['telemetry'] = max((n['depth'] for n in pending), default=0)   # PUBLISH (controller observes)
    return converged, {'pending': residue}

def worker_step_relax(state, store):
    """CONTROLLER instance: observe telemetry from the store, advance ONE warm-started
    relaxation step (the bridge nudge — same shape as a gcd step), publish K, carry the
    iterate. IDENTICAL primitive to worker_step; only the step differs."""
    K = state['K']
    tel = Telemetry(state['t_mem'], state['c_step'], state['t_ovf'],
                    store['telemetry'], state['resident'])      # OBSERVE workers' published residue
    down, up = max(1, K // 2), min(256, K * 2)                  # one relaxation step toward higher conductance
    Knew = down if bridge(down, K, tel) > 0 else up if bridge(up, K, tel) > 0 else K
    store['K'] = Knew                                           # PUBLISH (workers observe)
    return Knew, {**state, 'K': Knew}                           # CARRY the iterate

# ---- the composed loop: two generators, one primitive, sharing the store ----
def run_loop(schedule, K0=64, resident=False):
    """Closed loop: each tick the WORKER generator and the CONTROLLER generator each take
    one generator_step against the SAME store — worker publishes telemetry the controller
    observes, controller publishes K the worker observes. Same primitive, composed."""
    store = {'K': K0, 'telemetry': 0}
    cstate = {'K': K0, 't_mem': Q(1646,100), 'c_step': Q(548,100)/256,
              't_ovf': Q(259,100), 'resident': resident}
    trace = []
    for label, depth, ticks in schedule:
        for _ in range(ticks):
            wstate = {'pending': [{'depth': depth}]}            # this regime's workload arrives
            generator_step(wstate, worker_step, store)          # worker: observe K, publish telemetry
            K, cstate = generator_step(cstate, worker_step_relax, store)  # controller: observe telemetry, publish K
            trace.append((label, depth, K))
    return trace

def f(x): return float(x)

if __name__ == "__main__":
    print("CONTROLLER PLANT-MODEL VALIDATION — reproduce measured ablation (global, K=window):")
    tel256 = Telemetry(Q(1646,100), Q(548,100)/256, Q(259,100), 3, False)
    for K, meas in ((256, "21.70"), (4, "19.55")):
        print(f"   K={K:3d}: model {f(total(K, tel256)):5.2f} ms  (measured {meas} ms)")

    # the ovf-divisions flatten total for any K with K·c_step < t_ovf and passes==1, so the
    # optimum is a PLATEAU [max_depth, ovf_cross]; K only becomes the active lever when
    # max_depth exceeds the current K (forcing extra memory-re-paying passes).
    ovf_cross = int(Q(259,100) / (Q(548,100)/256))     # K where K·c_step = t_ovf
    print(f"\n  (plateau: any K in [max_depth, {ovf_cross}] is cost-equal — ovf dominates;")
    print("   K is the active lever only when max_depth > K. The loop fiddles K only when it matters.)")

    print("\nCLOSED LOOP (worker ∥ controller — ONE primitive, composed via the store):")
    print("  depths CROSS K; the controller (observing worker telemetry) must climb K, then relax:")
    schedule = [("shallow (max_d=3)",     3, 5),
                ("DEEP burst (d=200)",  200, 7),     # exceeds K ⇒ multi-pass memory re-pay; K must climb
                ("DEEPER (d=500)",      500, 7),
                ("back to shallow (3)",   3, 7)]
    trace = run_loop(schedule, K0=64)
    last = None; line = []
    for i, (label, d, K) in enumerate(trace):
        if label != last:
            if line: print("   " + last + ": " + " → ".join(map(str, line)))
            last = label; line = [K]
        else:
            line.append(K)
    print("   " + last + ": " + " → ".join(map(str, line)))
    print("\n  reading: K climbs (64→…→256) when a deep burst would force multi-pass memory re-pay,")
    print("  holds high while deep, relaxes back onto the plateau when shallow returns — TRACKS,")
    print("  monotone within a regime, no oscillation. This control law is what the persistent-")
    print("  megakernel controller block runs ON-DEVICE in exact ℚ CONTINUOUSLY — one warm-started")
    print("  relaxation step per iteration, current K always live for the workers (anytime, no cadence);")
    print("  the resident rail choice (recompute-from-residue) shifts the optimum — same law.")
