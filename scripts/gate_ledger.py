#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Gate outcome ledger — measured pass/fail rates, and the fail-fast order.

WHY: the pre-commit runs its blocking gates in a HAND-CHOSEN order. When a
commit fails, you learn it at whatever position that gate happens to sit — so a
gate that fails half the time can sit behind five that never do, and you pay
their runtime before every failure. Ordering by MEASURED failure frequency
makes the loop fail fast: the gate most likely to reject you runs first, you
fix, you retry.

THE CAPTURE POINT is the hook's own `run()` helper — every gate flows through
it, so one instrumentation point covers all of them (the same reason
`membudget` is where build times are captured: instrument the funnel, not each
caller).

⚑ THIS LEDGER REPORTS THE OBSERVED POPULATION, NEVER THE DECLARED ONE, AND THE
DIFFERENCE HAS BEEN MEASURED. A gate that has never run — or ran only outside the
rows retained here — is INVISIBLE to every mode below, so `--order` and `--report`
rank a SUBSET while reading as complete. That is the census-keyed-on-one-spelling
shape: a fact about the METHOD (which rows exist) presented as a fact about the
SUBSTRATE (which gates exist). The docstring above used to assert "~18 blocking
gates", a third number agreeing with neither.

The DECLARED population is the hook's own `run "..."` call sites, and
`scripts/build_census.py --gates` is the reader for it — partitioned by phase.
Cross-check against it before concluding anything about coverage. Two named
missing modes here, both WORK rather than findings: `--coverage` (which declared
gates have no rows?) and `--staleness` (how old is the newest row? — nothing
below prints recency, so a stale ledger reads as a current ranking).

The ledger is append-only TSV, one row per gate invocation:

    iso8601 <TAB> gate <TAB> status <TAB> seconds

`status` is `pass` or `fail`. Rates are computed over the last K runs of each
gate, so a gate that has been fixed stops being ranked first once its recent
history is clean — the ordering tracks the CURRENT tree, not all history.

  gate_ledger.py --record <gate> <status> <seconds>   # append (called by run())
  gate_ledger.py --order                              # gate names, worst first
  gate_ledger.py --report                             # rates + timings
"""

import os, sys, time, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "scripts", ".gate-outcomes.tsv")
K = 20  # window: rate over each gate's last K invocations


def record(gate, status, seconds):
    """Append one outcome. Never raises: a ledger failure must not break the
    gate it is measuring (the instrument must not become a new failure mode)."""
    try:
        with open(LEDGER, "a") as fh:
            fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{gate}\t{status}\t{seconds}\n")
    except OSError:
        pass


def _read():
    """gate -> [(status, seconds)] in file order (oldest first)."""
    hist = collections.defaultdict(list)
    try:
        with open(LEDGER) as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) < 4:
                    continue
                try:
                    secs = float(p[3])
                except ValueError:
                    secs = 0.0
                hist[p[1]].append((p[2], secs))
    except OSError:
        pass
    return hist


def _stats(hist):
    """gate -> (fail_rate, n, median_seconds) over the last K invocations."""
    out = {}
    for gate, rows in hist.items():
        recent = rows[-K:]
        n = len(recent)
        fails = sum(1 for s, _ in recent if s == "fail")
        secs = sorted(s for _, s in recent)
        med = secs[len(secs) // 2] if secs else 0.0
        out[gate] = (fails / n if n else 0.0, n, med)
    return out


def order():
    """Gate names worst-first: highest failure rate, then CHEAPEST first.

    ⚑ The tiebreak is deliberate. Among gates that fail equally often, running
    the cheap one first costs less per rejected attempt — fail-fast is about
    time-to-rejection, not just position. A gate with no history sorts last: it
    has never rejected anything, so there is no evidence it should preempt one
    that has."""
    st = _stats(_read())
    return [g for g, _ in sorted(st.items(), key=lambda kv: (-kv[1][0], kv[1][2]))]


def report():
    st = _stats(_read())
    if not st:
        print(
            f"gate-ledger: no outcomes recorded yet (expected at {os.path.relpath(LEDGER, ROOT)})"
        )
        return 0
    print(f"{'gate':<34} {'fail%':>6} {'n':>4} {'med_s':>7}")
    print("-" * 54)
    for g, (rate, n, med) in sorted(st.items(), key=lambda kv: (-kv[1][0], kv[1][2])):
        print(f"{g:<34} {rate * 100:>5.0f}% {n:>4} {med:>7.1f}")
    worst = [g for g, (r, _, _) in st.items() if r > 0]
    print(f"\n{len(worst)} of {len(st)} gates have failed in the last {K} runs each.")
    print("Fail-fast order = this listing, top to bottom.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--record" and len(a) >= 4:
        record(a[1], a[2], a[3])
        sys.exit(0)
    if a and a[0] == "--order":
        print("\n".join(order()))
        sys.exit(0)
    # ⚑ `--report` IS DISPATCHED, not merely the fallthrough. It was documented in the
    # banner above while the code only ever fell through to `report()`, so ANY unknown
    # flag — a typo included — printed the report and exited 0. The divergence census
    # read that as UNBACKED (a usage line naming a flag no literal backs) and was right:
    # a mode nothing branches on cannot be distinguished from a mode that does not exist.
    # Bare invocation keeps the report as its default; a MISSPELLED flag now refuses.
    if a and a[0] != "--report":
        print(
            f"gate_ledger: unknown mode {a[0]!r} — "
            f"expected --record / --order / --report (or no argument)",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(report())
