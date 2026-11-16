#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Bounded CPU benchmark for the clause-audit hot path.

⚑ CPU, NEVER WALL.  This box is busy by design (concurrent agda compiles, IDE
background typecheck), so a wall figure here would be a fact about co-tenancy.
Contention delays a process; it does not inflate the cycles it consumes.

⚑ BOUNDED BY CONSTRUCTION.  A full `clause_audit()` run was measured at 5.4-7.0
HOURS of CPU and three prior attempts died as backgrounded processes.  This never
calls it: it drives `_clause_scan` over the FIRST N files of the same sorted glob,
with the same four indexes, and reports per-file CPU so a projection to 3598 files
is arithmetic rather than a wait.

Modes:
    bench_clause_audit.py --baseline [N]   # provides() as shipped (no cache)
    bench_clause_audit.py --cached   [N]   # provides() over a memoised def_index
    bench_clause_audit.py --both     [N]   # both, against ONE index build, + ratio
    bench_clause_audit.py --agree    [N]   # do the two paths return IDENTICAL rows?

⚑ `--agree` IS NOT OPTIONAL DECORATION.  A cache that changes an answer is not a
speedup, and the only honest way to claim equivalence is to compare the row sets.
"""
import os, sys, time, glob, resource

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agda_defs
import agda_lex

AG = agda_defs.AG
DEFAULT_N = 40
FULL = None          # filled in by _files(): the real denominator, never guessed


def _cpu():
    """User+sys CPU seconds for this process. ⚑ NOT time.monotonic()."""
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def _files():
    global FULL
    fs = sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True))
    FULL = len(fs)
    return fs


def _indexes():
    """The four index builds, timed individually. Shared by BOTH arms.

    ⚑ BUILT ONCE AND HANDED TO BOTH ARMS so the comparison isolates the variable
    under test (`prov_of`) rather than re-measuring a constant either way.
    """
    out, t = {}, _cpu()
    known = agda_defs.def_index_modules();      out["def_index_modules"] = _cpu() - t
    t = _cpu()
    reex = {r[0] for r in agda_defs.reexport_index()}; out["reexport_index"] = _cpu() - t
    t = _cpu()
    di = agda_defs.def_index();                 out["def_index"] = _cpu() - t
    t = _cpu()
    mixfix = agda_lex.mixfix_delims(di);        out["mixfix_delims"] = _cpu() - t
    return known, reex, di, mixfix, out


def _partial(files):
    """The `mask` phase — same predicate as `clause_audit`, timed."""
    part = set()
    for p in files:
        try:
            s = agda_lex.mask_comments(open(p, encoding="utf-8",
                                            errors="replace").read())
        except OSError:
            continue
        import re
        if re.search(r"^\s*(mutual|abstract)\b", s, re.M) or \
           re.search(r"^\s*record\b", s, re.M):
            part.add(agda_defs.module_path(p, AG))
    return part


def _scan(files, known, prov_of, opaque, mixfix):
    rows = []
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        rows.extend(agda_defs._clause_scan(src, agda_defs.module_path(p, AG),
                                           known, prov_of, opaque, mixfix))
    return rows


def _cached_provides(di):
    """`provides` over an ALREADY-BUILT index — the whole of approach (A).

    ⚑ THE CACHE IS STILL O(index) PER CALL without the inversion: `provides` is a
    scan of every (name, modules) pair.  Memoising `def_index` alone removes the
    REBUILD but keeps that scan, so the inverted map is what actually collapses it
    — measured separately below as `--both` prints both arms.
    """
    inv = {}
    for n, mods in di.items():
        for m in mods:
            inv.setdefault(m, set()).add(n)
    return lambda m: inv.get(m, set())


def _uncached_provides():
    """`provides` EXACTLY as shipped — a fresh `def_index()` walk per call."""
    return agda_defs.provides


def _run(n, arm, files, known, reex, di, mixfix, part):
    prov = _uncached_provides() if arm == "baseline" else _cached_provides(di)
    sample = files[:n]
    t = _cpu()
    rows = _scan(sample, known, prov, reex | part, mixfix)
    dt = _cpu() - t
    return rows, dt


def main(argv):
    mode = next((a for a in argv[1:] if a.startswith("--")), None)
    nums = [a for a in argv[1:] if not a.startswith("--")]
    n = int(nums[0]) if nums else DEFAULT_N
    if mode not in {"--baseline", "--cached", "--both", "--agree"}:
        print(__doc__)
        return 2

    files = _files()
    print(f"corpus: {FULL} file(s) under {AG}/Substrate/**; sample n={n}")

    known, reex, di, mixfix, idx_t = _indexes()
    for k, v in idx_t.items():
        print(f"  index {k:20s} {v:7.3f}s CPU")
    print(f"  index {'TOTAL':20s} {sum(idx_t.values()):7.3f}s CPU")

    t = _cpu()
    part = _partial(files[:n])
    mask_dt = _cpu() - t
    print(f"  mask  {'(n files)':20s} {mask_dt:7.3f}s CPU  "
          f"-> ~{mask_dt / max(n, 1) * FULL:.1f}s full")

    if mode == "--agree":
        # ⚑ THE PARTIAL SET MUST MATCH THE ARM, so use the sample's own mask for both.
        a, _ = _run(n, "baseline", files, known, reex, di, mixfix, part)
        b, _ = _run(n, "cached", files, known, reex, di, mixfix, part)
        same = sorted(a) == sorted(b)
        print(f"rows: baseline={len(a)} cached={len(b)} IDENTICAL={same}")
        if not same:
            only_a = [r for r in a if r not in b][:10]
            only_b = [r for r in b if r not in a][:10]
            for r in only_a:
                print(f"  ONLY-baseline {r}")
            for r in only_b:
                print(f"  ONLY-cached   {r}")
        return 0 if same else 1

    arms = ["baseline", "cached"] if mode == "--both" else [mode[2:]]
    res = {}
    for arm in arms:
        rows, dt = _run(n, arm, files, known, reex, di, mixfix, part)
        per = dt / max(n, 1)
        proj = per * FULL
        res[arm] = (dt, per, proj, len(rows))
        print(f"scan [{arm:8s}] {dt:8.3f}s CPU over {n} file(s) "
              f"= {per:7.4f}s/file -> FULL {proj:9.1f}s CPU "
              f"({proj/3600:.2f}h), {len(rows)} row(s)")

    if len(res) == 2:
        b, c = res["baseline"][2], res["cached"][2]
        print(f"speedup: {b/c:.1f}x on the scan phase "
              f"({b:.0f}s -> {c:.0f}s CPU projected)")
        total_c = c + sum(idx_t.values()) + mask_dt / max(n, 1) * FULL
        print(f"projected FULL GATE (cached): {total_c:.1f}s CPU "
              f"= {total_c/60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
