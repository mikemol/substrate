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

# schedule: coop (one persistent launch) / strat (full-occupancy, launch-per-stratum) / pool (dynamic).
# DEADLOCK-FIXED (revisit-readiness, no spin-wait -- the stale "coop deadlocks" grounding was wrong, user
# caught it). MEASURED (jea_engine.py, this machine): deep-narrow chain coop 3.2 ms vs strat 14.0 ms (coop
# 4.4x, launch-bound); wide DAG coop 3.1 vs strat 2.7 (strat wins on occupancy). pool handles dynamic (only).
# So coop WINS deep-narrow (launch axis), strat WINS wide (occupancy axis), pool WINS dynamic -> a genuine
# 3-way knob (the el-atlas launch<->occupancy Pareto). INF = cannot do this workload.
AXES.append(("schedule (coop/strat/pool)", ["coop", "strat", "pool"], ["wide-static", "deep-narrow", "dynamic-spawn"],
             lambda s, w: {("coop","wide-static"):3.1, ("coop","deep-narrow"):3.2, ("coop","dynamic-spawn"):1e9,
                           ("strat","wide-static"):2.7, ("strat","deep-narrow"):14.0, ("strat","dynamic-spawn"):1e9,
                           ("pool","wide-static"):4.0, ("pool","deep-narrow"):4.5, ("pool","dynamic-spawn"):1.0}[(s, w)]))

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
    print("\n  reading: mode / repr / K / layout / SCHEDULE are ALL GENUINE Pareto knobs (winner FLIPS -> oracle-steered).")
    print("  - schedule: a genuine 3-way knob (CORRECTED -- my first audit called coop 'dominated' on the STALE")
    print("    deadlock grounding; the deadlock was FIXED by revisit-readiness). MEASURED: coop WINS deep-narrow")
    print("    (one persistent launch, 3.2 ms vs strat 14.0 = 4.4x, launch-bound), strat WINS wide (occupancy),")
    print("    pool WINS dynamic. The launch<->occupancy<->dynamic Pareto -- a real knob, not a false one.")
    print("  - layout: genuine knob (flat wins uniform-large; bucket wins skewed-small).")
    print("  - carrier is DERIVED (predicted by magnitude, C3), a data choice not a free knob.")
    print("  CONCLUSION: NO missed consolidations -- every axis is a genuine knob (mode/repr/K/layout/schedule)")
    print("  or data-derived (carrier). The earlier 'coop dominated' was an audit built on a fixed bug (stale).")
    print("  BOUND: dominance over THIS modeled space + cost models (grounded in U1/U2/U9/trace-window + MEASURED")
    print("  coop/strat timings); widen to retest. LESSON: ground audits on MEASUREMENT, not remembered history.")
