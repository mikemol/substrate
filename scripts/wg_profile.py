#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""wg_profile.py — the ITERATION-CYCLE instrument: where a target spends time and memory.

⚑ THIS IS A SEAM, NOT A NEW LAYER.  Split out of `worklist_gate.py` (1,458 code
lines, over the 1200 threshold) on 2026-08-11.  This is the CLEANEST seam in the
file and the one that justifies the split on its own: `profile_order` is 306
source lines whose only tie to the rest of the module is the TARGET it runs.  It
imports cProfile, pstats, tracemalloc and gc — none of which any other group
needs — and every other def in the file was paying to sit beside it.

⚑ AND THE SPLIT DID NOT MOVE THE FOOTPRINT, WHICH THIS MODULE IS THE INSTRUMENT
FOR SAYING (measured 2026-08-11).  `worklist_gate.py --selftest` peaks at
~190 MB against a 192 MB membudget lease; importing the WHOLE 1,458-line module
costs 3.1 MB.  The peak is the witness roster `order()` runs — twice, once via
`_drain` for openness and once via `reads()` for the footprint — not the line
count of any file.  Decomposition was owed by the size rule; it was never going
to pay the lease, and `--profile=<target>` is what says so with a number instead
of a story.  That is this module's entire reason for existing: I wrote it as a
throwaway profiler twice, and both times the answer evaporated with the turn.

⚑ `worklist_gate.py` RE-EXPORTS `profile_order`.  The public surface did not move.
"""

import os
import sys

import wg_engine
from wg_order import order


def profile_order(top=25, target=None):
    """Where a TARGET spends its time and memory — the ITERATION-CYCLE instrument.

    ⚑ THE TARGET IS AN ARGUMENT, AND THE REPORT NAMES IT (user, 2026-08-04:
    *"`--profile targets order()` ... sounds like a denominator problem to me."*).
    It was hardcoded to `order()`, with the name `profile_order` baking that in —
    so a reader chasing `items.py --selftest`'s 192MB overrun got a measurement
    of a DIFFERENT PROGRAM with nothing in the output saying so.  I had to state
    the limitation in PROSE, which is the reasoning-in-the-turn the standing rule
    forbids: it evaporates, and the next reader reads the table as covering
    whatever they were thinking about.

    ⚑ SAME CLASS AS `--key` REPORTING `0 file(s)` FROM MATCHED ROWS.  A report
    with an implicit population cannot distinguish "measured, nothing found"
    from "measured the wrong thing" — and both look like an answer.  `n of m`
    for a profiler is: say what was run.

    ⚑ I WROTE THIS AS A THROWAWAY SCRIPT TWICE (user, 2026-08-03: *"not great to
    keep writing one-off python profilers"*).  Both times the question was the
    same — *this tool takes two minutes, where does it go* — and both times the
    answer evaporated with the turn, so the next reader re-derives it and gets a
    different story.  That is the standing rule's exact target: a judgement
    happening in the turn instead of in a program.

    ⚑ AND THE THROWAWAY GOT THE ANSWER WRONG BEFORE IT GOT IT RIGHT.  I assumed
    the 57s -> 117s jump was the artifact scan I had just added; it does not
    appear in the top 28 at all.  The real weight is `sizes_of`/`force` (70s of
    157s) and `mask_comments` (27s over 58,689 calls).  A story about a
    regression, told without the profile, blamed the most recent edit — which is
    the attribution error §39/§41 already record for compile failures.

    Reports CUMULATIVE time (what a phase costs including its callees) beside
    CALL COUNT, because those two together are what distinguish the two fixes:
    a big cumtime with few calls wants a faster algorithm; a modest cost over
    tens of thousands of calls is REPEATED WORK and wants memoisation at the
    owner — §55's 300s -> 2.7s, which was not a parallelism problem."""
    import cProfile
    import pstats
    import io as _io

    # ⚑ MEMORY IS A HEATMAP, NOT A LEASE BISECTION (user, 2026-08-04: *"You
    # haven't even tried to get a memory heatmap of the thing yet."*).  Faced
    # with a suite OOM-killed at 192MB I bisected the LEASE — 192 fails, 256
    # fails, 512 passes — which yields one scalar and names nothing.  I then
    # attributed the peak to three different mechanisms in sequence (repetition,
    # retention, an unfired L2) without measuring any of them.
    #
    # ⚑ THE SCALAR CANNOT DISTINGUISH THE CASES THAT WANT OPPOSITE FIXES.
    # Repeated work that is collected between calls and a cache that RETAINS
    # produce the same maxRSS; only per-allocation-site attribution separates
    # them, and `tracemalloc` gives exactly that.  This is the same argument the
    # `REPEATED-WORK CANDIDATES` block above makes for time.
    #
    # ⚑ AND IT MEASURES THE SAME TARGET AS THE TIME PROFILE, so the two tables
    # are comparable rather than merely both present — a site that is hot in one
    # and absent from the other is the finding.
    import gc
    import tracemalloc

    # ⚑ THE TARGET IS RESOLVED AND NAMED BEFORE ANYTHING RUNS, so the label in
    # the report cannot drift from what was executed.  Default stays `order()` —
    # the question this was built for — but it is now a stated default rather
    # than an invisible one.
    _tname, _tfn = ("order", order) if target is None else target

    def _rss():
        """Resident set in bytes, or 0 — the figure a cgroup cap actually kills on.

        ⚑ EVERY MEMORY NUMBER IN THIS REPORT WAS TRACED-ONLY UNTIL NOW, and I
        spent four attributions on the gap between traced and resident without
        ever reading the resident half.  `VmRSS` is one line of
        `/proc/self/status`; the delta against `tracemalloc` is what says whether
        a footprint is Python objects at all."""
        try:
            with open("/proc/self/status", encoding="utf-8") as fh:
                for ln in fh:
                    if ln.startswith("VmRSS:"):
                        return int(ln.split()[1]) * 1024
        except OSError:
            pass
        return 0

    # ⚑ THE PROFILER IS A PARTICIPANT, AND I HAD IT INSIDE ITS OWN MEASUREMENT
    # (user, 2026-08-04: *"Are we actually using cProfile properly?"*).
    # `cProfile.Profile()` RETAINS a stats entry per profiled frame for the whole
    # run — 2,090,974 `visit` calls in the selftest pass — and `tracemalloc` was
    # started BEFORE `pr.enable()`, so every figure I reported counted the
    # profiler's own bookkeeping as the program's footprint.  Same class as
    # `reads()` spying `open()`: measuring through a lens that is itself part of
    # what is measured.
    #
    # Baselines are taken at each layer so the report can SUBTRACT rather than
    # caveat: `_rss_base` before anything, `_traced_base` after the profiler is
    # armed, so the traced figure excludes cProfile's setup.
    _rss_base = _rss()
    pr = cProfile.Profile()
    pr.enable()
    tracemalloc.start(1)
    _traced_base = tracemalloc.get_traced_memory()[0]
    # ⚑ COUNT CYCLIC GARBAGE, because it is the mechanism that explains a small
    # traced figure beside a large RSS (user: *"Sounds like a garbage collection
    # problem to me?"*).  An object in an unreachable CYCLE is dead to the
    # program and still held by the allocator until a collection runs — and
    # libcst nodes are parent/child linked, so a 2M-node walk is exactly the
    # shape that produces them.  `gc.collect()` returns what it reclaimed, which
    # is a measurement rather than a theory.
    #
    # ⚑ NO `gc.get_count()` BASELINE — I took one and never read it.  The
    # generational counters say how many allocations are PENDING inspection, not
    # how much garbage exists; the answerable question is what a collection
    # RECLAIMS, and that is measured at the end.  A recorded number nothing
    # consumes is the dead-field shape this repo censuses.
    try:
        _tfn()
    except SystemExit:
        pass
    finally:
        pr.disable()
        # ⚑ SNAPSHOT BEFORE `stop()`, PEAK BEFORE THE SNAPSHOT.  `get_traced_memory`
        # reports (current, peak); the peak is what a cgroup cap kills on, and it
        # is gone the moment tracing stops.  Taking the snapshot inside `finally`
        # means a witness that raises still reports what it allocated.
        _mem_cur, _mem_peak = tracemalloc.get_traced_memory()
        _mem_snap = tracemalloc.take_snapshot()
        tracemalloc.stop()
        # ⚑ RSS BEFORE THE COLLECTION, THEN THE COLLECTION, THEN RSS AGAIN.  The
        # three readings are what separate the two explanations a single figure
        # cannot: bytes that a `gc.collect()` RECLAIMS were cyclic garbage the
        # program had already abandoned; bytes that survive it are genuinely
        # live or are allocator arenas Python will not return to the OS.
        _rss_end = _rss()
        _gc_freed = gc.collect()
        _rss_gc = _rss()

    buf = _io.StringIO()
    st = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    st.print_stats(top)
    text = buf.getvalue()
    i = text.find("ncalls")
    print(text[i:] if i >= 0 else text)
    # ⚑ NAME THE REPEATED-WORK CANDIDATES EXPLICITLY.  The profile's own table
    # answers "what is slow"; the item is "what should I do about it", and the
    # discriminator is calls-per-distinct-question.  Surfacing the high-count
    # rows is what turns a table into a worklist.
    rows = []
    for (fn_file, fn_line, fn_name), (cc, nc, tt, ct, _cal) in st.stats.items():
        if nc >= 1000 and ct >= 1.0:
            rows.append(
                (
                    ct,
                    nc,
                    fn_name,
                    os.path.relpath(fn_file, wg_engine.ROOT)
                    if fn_file.startswith(wg_engine.ROOT)
                    else fn_file,
                    fn_line,
                )
            )
    # ⚑ TIME AND MEMORY ARE TWO PROJECTIONS OF ONE PROFILE RECORD (user,
    # 2026-08-04: *"You don't do 'time or memory'. Those are both different
    # projections of what SHOULD be the same profile record."*).  My first cut
    # printed a time table and then a SECOND memory table beside it — two reports
    # over one run, the same site appearing twice keyed differently, with a reader
    # left to join them by eye.  That is the derived-view defect in the instrument
    # built to find defects.
    #
    # ⚑ THEY JOIN ON `(file, line)`, WHICH BOTH ALREADY CARRY.  `pstats` keys
    # `(file, line, func)`; `tracemalloc.statistics("lineno")` keys `(file, line)`.
    # The join was available and I did not take it.
    #
    # ⚑ AND THE COMBINATION IS WHAT NAMES THE DEFECT — no single column does:
    #   hot time,  low bytes            -> compute-bound; memoise or do it once
    #   hot time,  high TRANSIENT bytes -> repeated work over large objects
    #   cold time, high LIVE bytes      -> RETENTION: a cache holding the corpus
    # The third is the one a lease bisection can never find, and it is the one I
    # failed to identify three times in a row today by looking at scalars.
    _alloc = {}
    for s in _mem_snap.statistics("lineno"):
        fr = s.traceback[0]
        _alloc[(fr.filename, fr.lineno)] = (s.size, s.count)
    # ⚑ THE TARGET IS THE DENOMINATOR — printed FIRST, because every number below
    # is scoped to it and a table read against the wrong program is worse than no
    # table.  Also states what `tracemalloc` can and cannot see: it counts PYTHON
    # allocations, so a cap exceeded while this reports a fraction of it means the
    # footprint is in C extensions or the interpreter, and more allocation detail
    # will not find it.
    _traced_live = (_mem_cur - _traced_base) / 1e6
    _rss_grew = (_rss_end - _rss_base) / 1e6
    print("PROFILE of %s()" % _tname)
    print(
        "  TRACED   peak %.1f MB, live at exit %.1f MB  (Python objects)"
        % (_mem_peak / 1e6, _traced_live)
    )
    print(
        "  RSS      %.1f -> %.1f MB, grew %.1f MB  (what a cgroup cap kills on)"
        % (_rss_base / 1e6, _rss_end / 1e6, _rss_grew)
    )
    print(
        "  GC       collect() freed %d object(s), RSS %.1f -> %.1f MB"
        % (_gc_freed, _rss_end / 1e6, _rss_gc / 1e6)
    )
    # ⚑ THE UNATTRIBUTED REMAINDER IS A NUMBER, NOT A CAVEAT.  Every memory
    # figure in this report was traced-only until now, and I spent four
    # attributions reasoning about the traced-vs-resident gap without ever
    # reading the resident half.  Printing the subtraction is what turns "not
    # attributable here" into "this much is not Python objects".
    _gap = _rss_grew - _traced_live
    print(
        "  ⚑ UNATTRIBUTED %.1f MB = RSS growth minus traced-live — interpreter,\n"
        "    C extensions (libcst, valkey), and allocator arenas Python holds\n"
        "    but does not return.  `tracemalloc` cannot see any of it." % _gap
    )
    print("  ⚑ peak-minus-live is TRANSIENT (collected); live is RETAINED.")
    print(
        "  ⚑ AND THE PROFILER IS A PARTICIPANT: cProfile retains a stats entry\n"
        "    per profiled frame, so these figures are measured with it ALREADY\n"
        "    ARMED (traced baseline taken after `enable()`) — its own retention\n"
        "    is excluded from `traced live`, NOT from RSS."
    )
    _joined = []
    for (fn_file, fn_line, fn_name), (cc, nc, tt, ct, _cal) in st.stats.items():
        size, blocks = _alloc.get((fn_file, fn_line), (0, 0))
        if ct < 0.5 and size < 1e6:
            continue
        _joined.append(
            (
                ct,
                size,
                nc,
                blocks,
                fn_name,
                os.path.relpath(fn_file, wg_engine.ROOT)
                if fn_file.startswith(wg_engine.ROOT)
                else fn_file,
                fn_line,
            )
        )
    _joined.sort(key=lambda r: -(r[0] + r[1] / 1e7))
    if _joined:
        print("  %8s %10s %8s %8s  %s" % ("cum s", "live MB", "calls", "blocks", "site"))
        for ct, size, nc, blocks, name, rel, line in _joined[:20]:
            print(
                "  %8.1f %10.2f %8d %8d  %s  %s:%d" % (ct, size / 1e6, nc, blocks, name, rel, line)
            )
    # ⚑ ALLOCATION SITES WITH NO PROFILE ROW ARE REPORTED SEPARATELY, NOT DROPPED.
    # A line that allocates but is not a FUNCTION (a comprehension, a literal, a
    # module-level table) has no `pstats` entry, so an inner join would silently
    # hide exactly the retained-corpus case this table exists to surface.
    _orphan = [
        (v[0], v[1], k)
        for k, v in _alloc.items()
        if not any(k == (f, l) for (f, l, _n) in st.stats) and v[0] >= 1e6
    ]
    _orphan.sort(reverse=True)
    if _orphan:
        print("  ALLOCATING SITES WITH NO CALL ROW (>=1MB live):")
        for size, blocks, (f, l) in _orphan[:10]:
            print(
                "  %8s %10.2f %8s %8d  %s  %s:%d"
                % (
                    "-",
                    size / 1e6,
                    "-",
                    blocks,
                    "(not a call)",
                    os.path.relpath(f, wg_engine.ROOT) if f.startswith(wg_engine.ROOT) else f,
                    l,
                )
            )
    rows.sort(reverse=True)
    if rows:
        print("REPEATED-WORK CANDIDATES (>=1000 calls, >=1s cumulative):")
        for ct, nc, name, rel, line in rows[:12]:
            print("  %7.1fs  %8d calls  %-22s %s:%d" % (ct, nc, name, rel, line))
        print(
            "   ⚑ a modest per-call cost over thousands of calls is REPEATED "
            "work — memoise at the\n     OWNER of the relation (§55: 300s → "
            "2.7s), not by parallelising the repetition."
        )
    # ⚑ AND A CACHE THAT EXISTS IS NOT A CACHE THAT WORKS.  `mask_comments` is
    # ALREADY memoised and still took 26s over 58,689 calls, which says nothing
    # about WHY: a thrashing cache (working set > cap) and redundant callers
    # (same source masked repeatedly in one walk) produce the same call count and
    # want OPPOSITE fixes.  The counters distinguish them, so the report asks.
    # ⚑ A FLAT TABLE CANNOT SHOW SETUP/TEARDOWN CHURN (user, 2026-08-04: *"I'll
    # wager we're doing setup/teardown work somewhere that should be getting
    # reused"*).  Sorting by cumulative time answers "what is expensive"; it
    # cannot answer "is this ONE connection reused, or N connections opened",
    # because both present as the same total.  `print_callers` on the socket and
    # connect paths is the discriminator: a reused connection has ONE caller of
    # `create_connection`, a churned one has thousands.
    _churn = [
        r
        for r in st.stats
        if r[2] in ("create_connection", "_connect", "makefile", "close", "_drop", "__init__")
    ]
    if _churn:
        _b2 = _io.StringIO()
        _st2 = pstats.Stats(pr, stream=_b2).sort_stats("cumulative")
        _st2.print_callers("create_connection|_connect$|makefile|_drop")
        _t2 = _b2.getvalue()
        _j = _t2.find("Function")
        print("\nSETUP/TEARDOWN — who opens connections, and how often:")
        print(_t2[_j:] if _j >= 0 else _t2)

    # ⚑ AND THE PER-CONSUMER CACHE COUNTERS EXIST AND WERE NEVER READ.  I built
    # `shared_cache.stats()` as the control-loop feedback and then reported
    # store-wide `INFO` numbers, which cannot attribute — so "which consumer is
    # paying for the round trips" stayed a guess across four profiling runs.
    try:
        import shared_cache as _sc

        _rows = _sc.stats()
        if _rows:
            print("SHARED CACHE, per consumer:")
            for _c in sorted(_rows):
                _r = _rows[_c]
                _keyed = _r["hits"] + _r["misses"]
                _rate = (100.0 * _r["hits"] / _keyed) if _keyed else 0.0
                print(
                    "  %-24s %6d hit  %6d miss (%.0f%%)  %5d unknown  "
                    "%5d stored"
                    % (_c, _r["hits"], _r["misses"], _rate, _r["unknown"], _r["stored"])
                )
    except Exception:
        pass

    try:
        sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
        import agda_lex as _al

        calls, hits, misses, evicted, live = _al.mask_stats()
        if calls:
            print(
                "MASK CACHE: %d calls, %d hits (%.0f%%), %d misses, "
                "%d evicted, %d live" % (calls, hits, 100.0 * hits / calls, misses, evicted, live)
            )
            # ⚑ THE VERDICT MUST TRACK WHAT THE COUNTER MEANS.  It read
            # "THRASHING — fix the eviction" on 4 mass-wipes AND on 10,720
            # single-entry evictions, which are opposite situations: the first
            # was a cliff discarding live entries, the second is a full cache
            # working correctly.  I renamed the counter in `agda_lex` and left
            # this sentence describing the old one — the derived-view split
            # (§6), in the reporting half of the instrument I built to avoid it.
            if evicted > live:
                print(
                    "   ⚑ THE WORKING SET EXCEEDS THE CAP (%d live, %d "
                    "evicted) — entries are recomputed\n     after eviction. "
                    "This is a real MEMORY bound, not a defect: raise "
                    "_MASK_CAP only if\n     the memory is affordable." % (live, evicted)
                )
            elif misses > live:
                print(
                    "   ⚑ REDUNDANT CALLERS — more misses than distinct "
                    "sources, with no eviction.\n     The same source is "
                    "re-masked; fix the CALL SITE, not the cache."
                )
    except Exception:
        pass
    return 0
