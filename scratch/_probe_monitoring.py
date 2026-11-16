#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""_probe_monitoring.py — what does each COUNTING GRADE actually cost?

⚑ THE QUESTION THIS EXISTS TO SETTLE, AND WHY IT IS NOT A TASTE CALL. `pycost`'s
design reads a work-unit at several grades (call / line / instruction) and defines
the regime rate r = work_ms / count(grade). Which grades are affordable ALWAYS-ON
and which must be on-demand is therefore a MEASUREMENT, not a preference — and the
plan's first cost table had `~1x`, `2.9x`, `~3x`, `high` in one column where only
ONE was measured. A guess formatted like a measurement is the defect; this closes it.

⚑ `pycodemod --available sys.monitoring` REPORTS ABSENT, AND THAT IS A FACT ABOUT
THE QUESTION. It tests TOP-LEVEL importable names; `sys.monitoring` is a submodule
of an already-imported module. Reading that ABSENT as "the interpreter lacks it"
would be the method-vs-substrate confusion the struct-tools rule is about. Ask the
interpreter directly, which is what this does.

⚑ THE WORKLOAD IS DELIBERATELY CALL-HEAVY AND THAT BIASES THE RESULT. A tight loop
over a trivial leaf maximises events-per-unit-work, so these are UPPER bounds for
call/line grades on realistic code. Recorded here rather than left implicit: a
number without its workload is not transferable.

    _probe_monitoring.py            # measure every grade
    _probe_monitoring.py --selftest # the counts must be EXACT, or the grade is a lie
"""
import sys
import time

# The workload. Kept module-level and tiny so the counts are hand-derivable:
# work() makes N calls to _leaf, plus 1 call to work itself.
N = 200_000


def _leaf(i):
    return i * i


def work(n):
    t = 0
    for i in range(n):
        t += _leaf(i)
    return t


def _time(fn):
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


def measure(event_name):
    """(seconds, count) running the workload with one monitoring event armed."""
    mon = sys.monitoring
    count = [0]
    TOOL = mon.PROFILER_ID
    ev = getattr(mon.events, event_name)

    def bump(*_a):
        count[0] += 1

    mon.use_tool_id(TOOL, "probe")
    try:
        mon.register_callback(TOOL, ev, bump)
        mon.set_events(TOOL, ev)
        try:
            secs = _time(lambda: work(N))
        finally:
            mon.set_events(TOOL, 0)
            mon.register_callback(TOOL, ev, None)
    finally:
        mon.free_tool_id(TOOL)
    return secs, count[0]


def measure_cprofile():
    """(seconds, primitive-call count) under cProfile — grade 1 as pycost will run it."""
    import cProfile
    import pstats
    import io

    pr = cProfile.Profile()
    t0 = time.perf_counter()
    pr.enable()
    work(N)
    pr.disable()
    secs = time.perf_counter() - t0
    st = pstats.Stats(pr, stream=io.StringIO())
    return secs, st.total_calls


GRADES = [
    (1, "cProfile ncalls", None),
    (1, "PY_START", "PY_START"),
    (2, "LINE", "LINE"),
    (3, "INSTRUCTION", "INSTRUCTION"),
]


def main():
    print(f"python {sys.version.split()[0]}")
    mon = getattr(sys, "monitoring", None)
    print(f"sys.monitoring: {'PRESENT' if mon else 'ABSENT'}")
    if not mon:
        print("  (grades 2-3 unavailable; pycost must fall back to cProfile only)")
        return 0

    base = min(_time(lambda: work(N)) for _ in range(3))   # min = least-noisy baseline
    print(f"\nworkload: work({N:,}) — {N + 1:,} calls, call-heavy by construction")
    print(f"baseline: {base*1000:.1f} ms\n")
    print(f"  {'grade':>5}  {'counter':<16} {'ms':>9} {'overhead':>9} {'count':>12}")
    for grade, label, event in GRADES:
        try:
            secs, count = measure_cprofile() if event is None else measure(event)
        except Exception as e:                              # a grade that will not arm is a verdict
            print(f"  {grade:>5}  {label:<16} {'—':>9} {'UNAVAILABLE':>9}  {type(e).__name__}: {e}")
            continue
        print(f"  {grade:>5}  {label:<16} {secs*1000:>9.1f} {secs/base:>8.1f}× {count:>12,}")
    print("\n  ⚑ UPPER BOUNDS: a tight loop over a trivial leaf maximises events per unit")
    print("    work. Real code does more between events, so overhead there is lower.")
    return 0


def _selftest():
    """⚑ A COUNT THAT IS NOT EXACT MAKES THE RATE r A FICTION, so the counts —
    not the timings — are what this pins. Timings are machine-dependent and are
    deliberately NOT asserted."""
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    mon = getattr(sys, "monitoring", None)
    check("sys.monitoring is present", mon is not None, True)
    if mon is not None:
        _secs, n = measure("PY_START")
        # ⚑ THE HARNESS IS INSIDE ITS OWN MEASUREMENT, and the first draft of this
        # assertion forgot that: it wanted N+1 (work + N leaf calls) and got N+3,
        # because `_time`'s own frame and the `lambda` wrapping the workload are
        # Python calls too. The counter was EXACT; the expectation was wrong. Pin
        # the exact total including harness frames, and name them, so a real drift
        # in the counter still fails rather than being absorbed by a tolerance.
        HARNESS_FRAMES = 2                       # _time(...) + the lambda it calls
        check("PY_START counts every python frame", n, N + 1 + HARNESS_FRAMES)
        _secs, nl = measure("LINE")
        check("LINE counts strictly more than calls", nl > N + 1, True)

    _secs, nc = measure_cprofile()
    check("cProfile sees at least the leaf calls", nc >= N + 1, True)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}: got {got!r} want {want!r}")
    print(f"_probe_monitoring selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    sys.exit(main())
