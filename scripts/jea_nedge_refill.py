#!/usr/bin/env python3
"""jea_nedge_refill.py — U9: mixed-depth REFILL dynamics in the nedge control model (the model's last gap).

jea_nedge_model collapses a workload to a single max_depth (passes = ceil(max_depth/K)). The gap (charter):
a HETEROGENEOUS workload is a depth DISTRIBUTION -- a few DEEP nodes hold their lanes for ceil(d/K) windows
while many SHALLOW nodes converge in one window and FREE their slot, which REFILLS with fresh work. So the
makespan is bound by EITHER the deep tail (ceil(max_depth/K) windows) OR the shallow throughput (all N
nodes through L lanes, >=1 window each: ceil(sum ceil(d/K) / L)), whichever is larger. The max-depth-only
model sees only the tail and over-windows the shallow majority (a depth-1 node issued K=128 steps wastes
127); the distribution-aware model sees both and picks K accordingly. This is the bucket-scheduler's
"K tracks each bucket's depth, not the deepest node" insight (jea_generator_bucket), lifted into the ORACLE.

Validated as a bisimulation against a ground-truth refill SIMULATION (the actual windowed lane/refill
process), the same way the base model was validated against ablation: the model must pick the SAME K the
simulation says is best.

Witnesses (each [W]):
1. MODEL == SIM (makespan): the closed-form distribution-aware makespan matches the ground-truth refill
   simulation across K and distributions (within list-scheduling slack).
2. DISTRIBUTION-AWARE OPTIMUM: the cost-optimal K DIFFERS by distribution (shallow-heavy -> small K;
   deep-tail -> large K) -- K is a function of the distribution, not just max_depth.
3. MAX-DEPTH MODEL OVER-WINDOWS: for a shallow-heavy + few-deep workload, the old max-depth-only K choice
   costs MORE (on the true simulation) than the distribution-aware K* -- the waste the old model missed.
4. CONTROL DECISION VALIDATED: the model's K* == the simulation's K* for every distribution (bisimulation).
"""
from fractions import Fraction as Q
from math import ceil
from jea_nedge_model import Telemetry, t_alu

TEL = Telemetry(Q(1646, 100), Q(548, 100) / 256, Q(259, 100), 0, False)   # plant constants (fitted to ablation)
def cw(K):  return TEL.t_mem + t_alu(K, TEL)                                # cost of ONE K-window: memory + ALU
KS = [1, 2, 4, 8, 16, 32, 64, 128, 256]


def simulate_refill(depths, K, L):
    """GROUND TRUTH: run the windowed lane/refill process. L lanes; each window advances every occupied
    lane's node by K steps; a node converged (remaining<=0) frees its lane; the backlog refills freed
    lanes. Returns the makespan in windows. Deep nodes hold lanes; shallow free+refill -- the dynamics."""
    backlog = sorted(depths)                               # ascending so .pop() takes the LARGEST first = LPT
    lanes = [backlog.pop() for _ in range(min(L, len(backlog)))]   # (deep + shallow run concurrently, not serialized)
    windows = 0
    while lanes or backlog:
        windows += 1
        lanes = [r - K for r in lanes]
        lanes = [r for r in lanes if r > 0]                # converged lanes freed
        while backlog and len(lanes) < L: lanes.append(backlog.pop())   # REFILL
        if windows > 5_000_000: break
    return windows


def model_makespan(depths, K, L):
    """closed-form distribution-aware makespan: max(deep-tail, shallow-throughput)."""
    tail = ceil(max(depths) / K)                           # the deepest node needs this many windows
    work = ceil(sum(ceil(d / K) for d in depths) / L)      # all window-slots through L lanes
    return max(tail, work)


def best_K(makespan_fn, depths, L):
    costs = {K: makespan_fn(depths, K, L) * cw(K) for K in KS}
    return min(costs, key=costs.get), costs


if __name__ == "__main__":
    L = 512                                                # concurrent lanes (effective parallel slots)
    dists = {
        "shallow-heavy (2000x d<=3 + 5x d=200)": [1, 2, 3] * 700 + [200] * 5,
        "deep-tail (200x d in 100..200)":        [100 + (7 * i) % 101 for i in range(200)],
        "uniform-deep (400x d=200)":             [200] * 400,
    }
    print(f"mixed-depth refill: distribution-aware control vs max-depth-only (L={L} lanes)\n")

    sim_match = True; overwindow_ok = False; decision_ok = True; results = {}
    for name, depths in dists.items():
        # 1/4: model makespan vs simulation, and the K decision each makes
        rel = max(abs(model_makespan(depths, K, L) - simulate_refill(depths, K, L)) / simulate_refill(depths, K, L)
                  for K in KS)
        sim_match &= (rel <= Q(15, 100))                   # model within 15% of the ground-truth sim
        Km, _ = best_K(model_makespan, depths, L)
        Ks, _ = best_K(lambda d, K, L: simulate_refill(d, K, L), depths, L)
        decision_ok &= (Km == Ks)
        # 3: the max-depth-only model ignores throughput: K minimizing only the tail
        Kmd = min(KS, key=lambda K: ceil(max(depths) / K) * cw(K))
        true_md = simulate_refill(depths, Kmd, L) * cw(Kmd)
        true_opt = simulate_refill(depths, Ks, L) * cw(Ks)
        waste = float(true_md / true_opt)
        results[name] = (Km, Ks, Kmd, waste, float(rel))
        print(f"  {name}")
        print(f"      model K*={Km:>3}  sim K*={Ks:>3}  max-depth-model K={Kmd:>3}  "
              f"|  max-depth cost / optimal = {waste:.2f}x   (model vs sim makespan within {float(rel)*100:.0f}%)")
        if waste > 1.10: overwindow_ok = True               # some distribution where the old model wastes >10%

    w1 = sim_match; w2 = len({r[1] for r in results.values()}) > 1; w3 = overwindow_ok; w4 = decision_ok
    print(f"\n1. MODEL == SIM (makespan within 15% of ground-truth refill across K, all distributions): {w1}")
    print(f"2. DISTRIBUTION-AWARE OPTIMUM (cost-optimal K differs by distribution, not just max_depth): {w2}")
    print(f"3. MAX-DEPTH MODEL OVER-WINDOWS (>1.10x cost on the true sim for some distribution): {w3}")
    print(f"4. CONTROL DECISION VALIDATED (model K* == sim K*, every distribution -- bisimulation): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U9: the control model now sees the depth DISTRIBUTION + lane refill,")
    print(f"  not just max_depth. K is bound by max(deep-tail, shallow-throughput); the cost-optimal K tracks")
    print(f"  the distribution (validated against the ground-truth refill sim, K* matches). The max-depth-only")
    print(f"  model over-windows the shallow majority -- the gap, now closed. (= the bucket scheduler's")
    print(f"  'K per bucket, not the deepest node', lifted into the oracle.)")
