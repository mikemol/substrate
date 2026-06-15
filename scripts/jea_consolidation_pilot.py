#!/usr/bin/env python3
"""jea_consolidation_pilot.py — validate the unification has no MISSED consolidations, via the nedge
knobs+measures model. A "knob" is a genuine degree of freedom ONLY if its winner FLIPS across the config
space (a Pareto frontier / bridge null). If one setting wins under ALL modeled circumstances, it is NOT a
knob -- it is a DOMINATED axis, and keeping it as a parameter is a missed consolidation (collapse it). This
is the SWB-pilot pattern (a coeff-independent boundary with zero verdict-diff is not a real boundary).

Method (per axis): settings S, a swept workload-config space W, a cost measure cost[s][w]. A setting s is
DOMINATED if some other s' has cost[s'] <= cost[s] for ALL w (and < for some) -- s never uniquely wins, so
it is removable. An axis is a GENUINE KNOB iff >=2 non-dominated settings whose argmin FLIPS across W.

HONEST BOUND (charter discipline): dominance is over the MODELED config space + these cost models, not a
universal claim. The cost models are grounded in measured findings (cited); widen the space to retest.

Output: per axis a verdict {KEEP (genuine knob), COLLAPSE (dominated setting found), DERIVED (data-driven,
not a free knob)} and the list of MISSED CONSOLIDATIONS (dominated settings we are keeping as knobs).
"""
EPS = 1e-9


def classify(name, settings, configs, cost):
    """cost(s, w) -> float. Return (verdict, dominated[], flips)."""
    grid = {s: [cost(s, w) for w in configs] for s in settings}
    dominated = []
    for s in settings:
        for s2 in settings:
            if s2 == s: continue
            if all(grid[s2][i] <= grid[s][i] + EPS for i in range(len(configs))) and \
               any(grid[s2][i] < grid[s][i] - EPS for i in range(len(configs))):
                dominated.append(s); break
    live = [s for s in settings if s not in dominated]
    winners = {min(live, key=lambda s: grid[s][i]) for i in range(len(configs))}
    flips = len(winners) > 1
    return dominated, flips, winners, grid


AXES = []

# mode: eager (gcd-work, canonical) vs lazy (no gcd, non-canonical -> pay C to reduce on demand).
# grounded: U2/I1 (eager gwork~216 fixed; lazy 0 gwork + 84 non-canonical). config = canonicality-demand C.
AXES.append(("mode (eager/lazy)", ["eager", "lazy"], [c/10 for c in range(11)],
             lambda s, C: 216.0 if s == "eager" else 84.0 * C * 3))

# repr: value-window (cheap arith, dear canonical) vs trace-window (dear arith, free canonical).
# grounded: jea_trace_window rep_pareto_bridge (va,vc)=(1,8),(ta,tc)=(8,1). config = arithmetic fraction f.
AXES.append(("repr (value/trace)", ["value", "trace"], [f/10 for f in range(11)],
             lambda s, f: (f*1+(1-f)*8) if s == "value" else (f*8+(1-f)*1)))

# K (gcd window): grounded U9 -- K* depends on the depth distribution (shallow-heavy vs deep-tail).
# config = workload kind; cost = a stand-in makespan*window proportional to U9's result.
AXES.append(("K window (small/large)", ["K-small", "K-large"], ["shallow-heavy", "deep-tail"],
             lambda s, w: ({("K-small","shallow-heavy"):1.0, ("K-small","deep-tail"):3.0,
                            ("K-large","shallow-heavy"):2.5, ("K-large","deep-tail"):1.0})[(s, w)]))

# schedule: coop (persistent 1-thread/block, residency gamble) / strat (full-occupancy, deadlock-free,
# static only) / pool (general, handles dynamic spawn). grounded: charter (coop DEADLOCKED past ~3/SM;
# strat = "the merge done right", 847M nodes/s; pool = the spawn-general engine). config = workload.
# INF = cannot do this workload. coop static = high (residency gamble); strat dynamic = INF (no pre-stratify).
AXES.append(("schedule (coop/strat/pool)", ["coop", "strat", "pool"], ["static-DAG", "dynamic-spawn"],
             lambda s, w: {("coop","static-DAG"):10.0, ("coop","dynamic-spawn"):1e9,
                           ("strat","static-DAG"):1.0, ("strat","dynamic-spawn"):1e9,
                           ("pool","static-DAG"):2.0, ("pool","dynamic-spawn"):1.0}[(s, w)]))

# layout: flat (one lane width = max) vs bucket-packed (lane = MSB+1, + tiny re-bucket overhead).
# grounded: U1 (2.46x denser on skewed-small); uniform-large -> bucket==flat + epsilon overhead.
AXES.append(("layout (flat/bucket)", ["flat", "bucket"], ["skewed-small", "uniform-large"],
             lambda s, w: {("flat","skewed-small"):64.0, ("flat","uniform-large"):64.0,
                           ("bucket","skewed-small"):26.0, ("bucket","uniform-large"):64.5}[(s, w)]))


if __name__ == "__main__":
    print("CONSOLIDATION AUDIT (nedge knobs+measures): genuine knob (winner flips) vs dominated (collapse)\n")
    missed = []
    for name, settings, configs, cost in AXES:
        dom, flips, winners, grid = classify(name, settings, configs, cost)
        if dom:
            verdict = f"COLLAPSE -- dominated: {dom} (missed consolidation)"
            missed.append((name, dom))
        elif flips:
            verdict = f"KEEP -- genuine knob (winner flips: {winners})"
        else:
            verdict = f"DERIVED/collapsible -- single winner {winners} across all configs"
        print(f"  {name:28s}: {verdict}")
        for s in settings:
            print(f"        {s:8s} cost over {configs}: {[round(c,1) for c in grid[s]]}")
    # carrier is not in the sweep: it is DERIVED (predicted tier by magnitude, C3) -- not a free knob.
    print(f"\n  carrier (u64/u128/byte-limb): DERIVED -- placement predicted from magnitude (C3), not a free knob.\n")

    print("MISSED CONSOLIDATIONS (dominated settings kept as knobs -> collapse):")
    if missed:
        for name, dom in missed: print(f"  - {name}: collapse {dom}")
    else:
        print("  (none)")
    print("\n  reading: mode / repr / K / layout are GENUINE Pareto knobs (winner FLIPS -> the oracle steers them).")
    print("  - layout: NOT dominated (corrected a pre-baked assumption -- I'd guessed bucket dominates). flat wins")
    print("    uniform-large-magnitude (no density gain, no re-bucket overhead); bucket wins skewed-small. A knob")
    print("    iff bucket carries nonzero overhead on uniform-large -- model-sensitive; measure the overhead to be sure.")
    print("  - schedule's 'coop' is the ONE clear DOMINATED setting (strat wins static, pool wins dynamic; coop")
    print("    wins nothing -- grounded: coop DEADLOCKED past ~3/SM, strat is full-occupancy deadlock-free). DROP coop;")
    print("    the scheduler is {strat for static, pool for dynamic} = a DERIVED data choice, not a 3-way knob.")
    print("  - carrier is DERIVED (predicted by magnitude, C3). So: REAL knobs = mode/repr/K/layout (oracle-steered);")
    print("    carrier+schedule are data-derived; only COOP was a false knob = the one missed consolidation.")
    print("  BOUND: dominance is over THIS modeled config space + cost models (grounded in U1/U2/U9/trace-window/")
    print("  charter), not universal; widen the space (esp. the layout overhead) to retest.")
