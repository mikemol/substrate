#!/usr/bin/env python3
"""jea_regression_gate.py — Δ-G2: the jea-regression PRE-COMMIT gate. Runs the jea modules' __main__ and asserts each
prints PASS (and never FAIL). Fired from .githooks/pre-commit when any scripts/jea_*.py is staged -- converting "run
the jea suite" from a discipline I must REMEMBER into a NON-SKIPPABLE gate (the G9 escalation: a recurring class --
cross-path correctness regressions -- moved to a layer the loop can't skip).

It would have caught both regressions this arc surfaced: the Δ-Ψ-dag leaf-code collision (jea_eval FAILed) and the
eval_aligned_planes non-contiguous-slice bug (jea_resident W11 FAILed).

--check (default): the FAST correctness subset (no timing-heavy modules; the regression-catchers). --full: all jea
modules. Needs the GPU (cupy); on a box without it the gate SKIPS (exit 0) -- jea can't run there anyway, and whoever
stages jea changes has a GPU. A module is PASS iff it exits 0, prints '  PASS', and never prints '  FAIL'.
"""
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))

# FAST: correctness-critical, no [numbers] timing loops -- the cross-path regression catchers (< ~30s total).
FAST = ["jea_branchless", "jea_graded", "jea_divstr", "jea_carrier", "jea_dag_gen", "jea_mega_eval", "jea_eval"]
# SLOW: timing-heavy / hardware-discovery / Agda-driving -- run under --full (or CI), not every commit.
SLOW = ["jea_carrier_solve", "jea_resident", "jea_onegraph", "jea_bitkernel", "jea_navigator", "jea_agda_apex"]


def run_one(mod, timeout=180):
    t0 = time.perf_counter()
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, mod + ".py")],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return mod, "TIMEOUT", time.perf_counter() - t0
    out = r.stdout + r.stderr
    ok = (r.returncode == 0) and ("\n  PASS" in out) and ("\n  FAIL" not in out)
    return mod, ("PASS" if ok else "FAIL"), time.perf_counter() - t0


def main():
    try:
        import cupy; cupy.cuda.Device(0).compute_capability                 # GPU present?
    except Exception as e:
        print(f"jea-gate: SKIP (no GPU/cupy: {type(e).__name__}) -- jea requires it; nothing to check here")
        return 0
    mods = FAST + (SLOW if "--full" in sys.argv else [])
    fails = []
    for m in mods:
        mod, st, dt = run_one(m)
        print(f"  jea-gate {m:<18} {st:<8} {dt:5.1f}s")
        if st != "PASS":
            fails.append((m, st))
    if fails:
        print(f"jea-gate: FAILED -- {', '.join(f'{m}({s})' for m, s in fails)} (a jea module regressed)")
        return 1
    print(f"jea-gate: OK ({len(mods)} modules{' [full]' if '--full' in sys.argv else ' [fast]'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
