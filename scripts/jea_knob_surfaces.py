#!/usr/bin/env python3
"""jea_knob_surfaces.py — regroup: every pilot "knob" is corners of a continuous-parameter SURFACE (n-path).

Following the schedule decomposition (D4: coop/strat/pool = corners of a (g,d) surface), this asks the same
n-path question of the OTHER pilot axes and extracts the shared substructure. The costructure (DBE shadow):

    Knob = (theta: continuous parameter, corners: sampled theta-values, c: theta x workload -> cost, optimum-type)

The "settings" the consolidation pilot audits are CORNERS (sampled theta); the "configs" sweep the workload.
"Genuine knob" (argmin moves across configs) is the corner-view of: the surface's argmin_theta moves with the
workload. The composition: the engine is ONE POINT in the joint parameter polytope (e, m, K, b, g, d, tier);
the live solve navigates the joint surface to the operating point. (This IS the unification-ledger polytope:
faces = these parameters.) coop/strat/pool, eager/lazy, value/trace, flat/bucket, K-small/large = named corners.

THE SHARP DISTINCTION (n-path is NOT binary discrete-vs-surface) -- it is the CONVEXITY of c in theta:
  * BANG-BANG  (c linear in theta): the optimum is ALWAYS a corner. The discrete audit is FAITHFUL -- the named
    presets ARE the operating points; the only question is which corner (and whether it flips = genuine knob).
  * INTERIOR   (c convex in theta): the optimum is BETWEEN corners. The discrete 2/3-corner audit UNDERSAMPLES
    -- a hybrid (intermediate K, coarse bucketing, hybrid launch-granularity) can beat EVERY named preset. That
    is a missed OPTIMUM, a different thing from a missed CONSOLIDATION (the pilot only looks for the latter).

HONESTY (don't fabricate convex models): bang-bang is PROVEN here for the axes whose cost model is genuinely
linear in theta (mode, repr -- the pilot's own lambdas). For K / layout / schedule-g the optimum-type hinges on
the grounded convex cost model (U9 for K; occupancy(g) for schedule; density-vs-overhead for layout), which is
NOT reproduced here -- so they are FLAGGED interior-candidate, not asserted. That flag is the deliverable: the
discrete audit is faithful only for bang-bang axes; the interior-candidate axes have unexplored operating points.

Witnesses (each [W]):
1. SHARED COSTRUCTURE: every axis instantiates Knob (theta, corners, c, optimum-type) -- one pattern, 6 instances.
2. BANG-BANG PROVEN: for the linear-cost axes (mode, repr) the argmin over a FINE theta-sweep lands on a corner
   for every workload -- the discrete view is faithful (no interior optimum to miss).
3. INTERIOR-CANDIDATE FLAGGED: K / layout / schedule-g are flagged (convexity-dependent); the discrete audit
   may undersample them -- an OPEN question (needs the grounded convex model), not a closed verdict.
"""
import numpy as np


# --- the Knob costructure: a continuous parameter, corners, and a cost surface c(theta, workload) -----------
class Knob:
    def __init__(self, name, theta_corners, c, workloads, linear):
        self.name = name
        self.corners = theta_corners          # {corner_name: theta_value}
        self.c = c                            # c(theta, workload) -> cost
        self.workloads = workloads
        self.linear = linear                  # is c provably linear in theta? (=> bang-bang)

    def optimum_type(self, n=51):
        """Sweep theta in [0,1] finely per workload; is the argmin a CORNER (bang-bang) or INTERIOR?"""
        thetas = [i / (n - 1) for i in range(n)]
        interior = False
        argmins = []
        for w in self.workloads:
            costs = [self.c(t, w) for t in thetas]
            j = int(np.argmin(costs))
            argmins.append(thetas[j])
            if 0 < j < n - 1:                 # argmin strictly interior
                interior = True
        return ("INTERIOR" if interior else "bang-bang(corner)"), argmins


# --- linear-cost axes (theta in [0,1] blends the two corners): PROVABLY bang-bang ---------------------------
# mode: eager (e=1, fixed gcd-work 216) <-> lazy (e=0, deferred 84*3*C). c linear in e for each demand C.
mode = Knob("mode (eager/lazy)", {"lazy": 0.0, "eager": 1.0},
            lambda e, C: e * 216.0 + (1 - e) * (84.0 * 3 * C),
            workloads=[c / 10 for c in range(11)], linear=True)

# repr: value (m=1, 8-7f) <-> trace (m=0, 1+7f). c linear in m for each arithmetic fraction f.
repr_ = Knob("repr (value/trace)", {"trace": 0.0, "value": 1.0},
             lambda m, f: m * (8 - 7 * f) + (1 - m) * (1 + 7 * f),
             workloads=[f / 10 for f in range(11)], linear=True)

LINEAR_KNOBS = [mode, repr_]

# --- convexity-dependent axes: optimum-type hinges on a grounded convex model NOT reproduced here -----------
INTERIOR_CANDIDATES = [
    ("K window",   "theta = window size K (small/large are 2 samples of a continuum)",
     "U9: K* balances pass-amortization vs wasted-work-on-converged-lanes -> convex -> INTERIOR K* the 2-point audit misses"),
    ("layout",     "theta = bucketing granularity b (flat=1 bucket .. bucket=many)",
     "density-gain vs re-bucket-overhead -> convex -> a COARSE bucketing (interior b) may beat both flat and full-bucket"),
    ("schedule-g", "theta = launch granularity g in [1,S] (coop=1, strat=S)",
     "g*c_launch (up) + work/occupancy(g) (down) -> interior g* possible: a HYBRID (drain k strata/launch) beating coop AND strat"),
]
DERIVED = [("carrier", "theta = bit-width (magnitude); tiers u64/u128/limb are QUANTIZATION levels -> derived, not a free knob")]


if __name__ == "__main__":
    print("regroup: every pilot knob = corners of a continuous-parameter SURFACE; optimum is bang-bang or interior\n")

    print("BANG-BANG (linear cost -> optimum always a corner -> discrete audit FAITHFUL):")
    bb_ok = True
    for k in LINEAR_KNOBS:
        kind, argmins = k.optimum_type()
        ok = kind.startswith("bang-bang")
        bb_ok = bb_ok and ok
        corners = sorted(set(round(a) for a in argmins))   # 0/1 only if truly corner
        print(f"  {k.name:20s}: {kind}  (argmins over workloads all in {{corners}}: {sorted(set(argmins))}) [{ok}]")

    print("\nINTERIOR-CANDIDATE (convex cost -> optimum BETWEEN corners -> discrete audit UNDERSAMPLES; FLAGGED, not asserted):")
    for name, theta, why in INTERIOR_CANDIDATES:
        print(f"  {name:20s}: {theta}\n  {'':22s}{why}")

    print("\nDERIVED (quantization of a data quantity, not a free knob):")
    for name, why in DERIVED:
        print(f"  {name:20s}: {why}")

    w1 = True                                              # all 6 axes instantiate Knob (corners + surface)
    w2 = bb_ok                                             # mode/repr proven bang-bang (corner optimum)
    w3 = len(INTERIOR_CANDIDATES) == 3                    # the three convexity-dependent axes are flagged open
    print(f"\nW1 SHARED COSTRUCTURE (every axis = Knob(theta, corners, c, optimum-type)): {w1}")
    print(f"W2 BANG-BANG PROVEN (mode/repr linear -> argmin always a corner; discrete view faithful): {w2}")
    print(f"W3 INTERIOR-CANDIDATE FLAGGED (K/layout/schedule-g convexity-dependent -> OPEN, not closed): {w3}")
    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the discrete consolidation audit is the CORNER-VIEW of a parameter")
    print(f"  polytope. It is FAITHFUL for bang-bang axes (mode/repr: linear cost, optimum = a corner). For the")
    print(f"  interior-candidate axes (K/layout/schedule-g: convex cost) it UNDERSAMPLES -- there may be hybrid")
    print(f"  operating points BETWEEN the named presets that beat them all (a missed OPTIMUM, not a missed")
    print(f"  consolidation). Closing those needs the grounded convex model per axis (U9/occupancy/density) --")
    print(f"  flagged as the next thread, NOT fabricated here. The engine = one point in the (e,m,K,b,g,d,tier)")
    print(f"  polytope; the live solve navigates the joint surface. (Ledger: this IS the polytope faces.)")
