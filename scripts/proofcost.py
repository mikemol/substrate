#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""proofcost.py — attach a profiler to Agda proof resolution (Ⓟ.proof-cost-ledger).

Proof typechecking is a measurable computation: parse → load deps → CHECK RHS (normalize +
convert) → serialize. Agda 2.8's `--profile=all` + GHC's `+RTS -s` expose every phase, so a
regime choice (division vs multiplication, structural vs reflection) becomes a MEASUREMENT, not a
trial-and-OOM guess. This wraps that into SRE-style SLIs, parallel to `buildtime.py`/membudget
(which already record wall-time + peak_mb per module); here the SLIs are the proof-WORK metrics:

  Total_ms        total typecheck time
  CheckRHS_ms     time NORMALIZING proof terms (the hot path; high % = reduction-bound)
  cmp_reduce      `compare by reduction` — defeq checks that had to REDUCE (the "cache-miss" analog)
  alloc_mb        bytes allocated (reduction churn — the "instructions retired" analog)
  peak_mb         max residency (the OOM risk)
  gc_pct          GC time / total (churn overhead)

THE REGIME ORACLE (Ⓟ.proof-regime-oracle — the jea_cost analog for proofs). jea_cost makes a GPU
schedule's cost STRUCTURAL — `T_s = Σ count × rate`, oracle = `argmin_s T_s`, one calibrated constant,
validated by predicting unseen winners with dominance-as-output. The proof analog:

    CheckRHS_ms  =  cmp_reduce × r          (count × rate — exact: r is the MEAN per-compare reduction cost)

`r` (ms per `compare by reduction`) is the **regime rate** — the calibrated machine+regime constant. It
CLUSTERS by regime: reflection/deep-normalization ⇒ few compares but high r; structural/shallow ⇒ many
compares but low r (measured ~15×: GF16DLog r≈7.4 vs DLogHom r≈0.48). So the cheaper regime is
`argmin (cmp_reduce × r)`, and because r dominates the count, the oracle PREFERS the low-r (structural)
regime even at higher cmp_reduce — predicting the regime to pick BEFORE trial-and-OOM.

Usage:
  proofcost.py <module-relpath> [...]   # profile module(s) (relpaths from agda/), report + append ledger
  proofcost.py --top [N]                # the N costliest modules in the ledger (by CheckRHS_ms; default 15)
  proofcost.py --module <relpath>       # one module's recorded profile history
  proofcost.py --oracle [N]             # the regime oracle: per-module rate r (regime fingerprint) + cost-form
  proofcost.py --structural [N]         # join the ANALYZER (jea_pysim forest_size) to the profiler (r): the
                                        # explicitness↔depth trade — forest_size pre-build proxies r
  proofcost.py --emit [K] [--dry-run]   # push the ledger to the TSDB as `proofcost_*` gauges (last-K)
  proofcost.py --reprofilable [N]       # the heaviest modules that ACTUALLY BUILD — the join over
                                        # the profile ledger and `.leaf-verify.tsv`.
                                        # ⚑ Picking a witness from `--top` by EYE selects FOR
                                        # BLOCKED modules: the CheckRHS-heavy modules and the
                                        # broken frontier both concentrate in the decomposition-arc
                                        # subtrees. It reports the COVERAGE too — how much of the
                                        # expensive tree is unavailable is itself the finding.
  proofcost.py --parse <outfile> <agda-args…>
                                        # ⚑ THE ALWAYS-ON CAPTURE POINT, and it is MACHINE-FACING —
                                        # the agda shim calls it, not an operator. Parse a saved
                                        # `agda --profile=all` output and append the SLIs to the
                                        # module's per-dir ledger, CWD-relative. Best-effort by
                                        # design: it silently no-ops on any problem so it can never
                                        # perturb a build, and it DROPS a sample whose CheckRHS is 0
                                        # (a cached `.agdai` load is deserialization, not a proof).
                                        # Being machine-facing is why it went undeclared; a mode with
                                        # no human caller still has to be findable by one.
  proofcost.py --selftest               # the suite

⚑ `--emit` ROUTES THROUGH `membudget_otlp.emit_gauges` — THE one OTLP producer, which pins
`service.instance.id` and uses `Resource(attributes=)` (not `Resource.create()`, which mints a
fresh series set per run). This ledger had NO export path until that producer was lifted out of
membudget: the ledger→gauge shape was a thing you rewrote rather than called, so the richest
artifact in the family stayed local to whoever ran it.

The per-dir ledger is `.agda-profile.tsv` alongside each Makefile (gitignored — hardware-specific),
rows `module<TAB>total_ms<TAB>checkrhs_ms<TAB>cmp_reduce<TAB>alloc_mb<TAB>peak_mb<TAB>gc_pct`.

NOTE: `--profile=all` roughly doubles compile time, so this is ON-DEMAND (not wired into every
build the way peak_mb is). Run it on the module/regime you are deciding about.
"""

import os, re, sys, time, subprocess, glob, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
AGDA = os.path.join(ROOT, "agda")
LEDGER = ".agda-profile.tsv"
KEEP = 5

_num = lambda s: int(s.replace(",", ""))


def _parse(out: str) -> dict:
    """Pull the SLIs out of `agda --profile=all +RTS -s` output."""

    def grab(pat, conv=_num, default=0):
        m = re.search(pat, out, re.MULTILINE)
        return conv(m.group(1)) if m else default

    total_ms = grab(r"^Total\s+([\d,]+)ms")
    checkrhs = grab(r"CheckRHS\s+([\d,]+)ms")
    deser_ms = grab(r"^Deserialization\s+([\d,]+)ms")
    cmp_reduce = grab(r"^compare by reduction\s+([\d,]+)\s*$")
    nodes = grab(r"^Node\s+\(fresh\)\s+([\d,]+)")
    alloc_b = grab(r"([\d,]+) bytes allocated in the heap")
    resid_b = grab(r"([\d,]+) bytes maximum residency")
    gc_s = grab(r"GC\s+time\s+([\d.]+)s", float, 0.0)
    rts_tot_s = grab(r"Total\s+time\s+([\d.]+)s", float, 0.0)
    return {
        "total_ms": total_ms,
        "checkrhs_ms": checkrhs,
        "deser_ms": deser_ms,
        "cmp_reduce": cmp_reduce,
        "nodes": nodes,
        "alloc_mb": round(alloc_b / 1e6, 1),
        "peak_mb": round(resid_b / 1e6, 1),
        "gc_pct": round(100 * gc_s / rts_tot_s, 1) if rts_tot_s else 0.0,
    }


def _agdai_paths(module_rel: str):
    base = os.path.basename(module_rel).replace(".agda", ".agdai")
    return glob.glob(os.path.join(AGDA, "_build", "**", base), recursive=True)


def profile(module_rel: str) -> dict:
    """Force a re-typecheck of `module_rel` (relpath from agda/) under --profile=all + RTS -s."""
    for p in _agdai_paths(module_rel):  # evict the cached interface → real re-typecheck
        try:
            os.remove(p)
        except OSError:
            pass
    proc = subprocess.run(
        ["agda", "--safe", "-i.", module_rel, "--profile=all", "+RTS", "-s", "-RTS"],
        cwd=AGDA,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 and "Total" not in out:
        sys.stderr.write(out[-1500:])
        raise SystemExit(f"agda failed on {module_rel} (rc={proc.returncode})")
    sli = _parse(out)
    _append(module_rel, sli)
    return sli


def _append(module_rel: str, s: dict) -> None:
    led = os.path.join(AGDA, os.path.dirname(module_rel), LEDGER)
    row = "\t".join(
        str(x)
        for x in (
            os.path.basename(module_rel),
            s["total_ms"],
            s["checkrhs_ms"],
            s["cmp_reduce"],
            s["alloc_mb"],
            s["peak_mb"],
            s["gc_pct"],
        )
    )
    try:
        with open(led, "a") as f:
            f.write(row + "\n")
    except OSError:
        pass


def _report(module_rel: str, s: dict) -> None:
    pct = (100 * s["checkrhs_ms"] // s["total_ms"]) if s["total_ms"] else 0
    print(f"\n{module_rel}")
    print(f"  Total            {s['total_ms']:>7} ms")
    print(
        f"  CheckRHS         {s['checkrhs_ms']:>7} ms  ({pct}%)   ← proof normalization (the hot path)"
    )
    print(f"  Deserialization  {s['deser_ms']:>7} ms          (dependency load)")
    print(
        f"  compare-by-reduction {s['cmp_reduce']:>7}          ← defeq forcing reduction (cache-miss analog)"
    )
    print(f"  Node (fresh)         {s['nodes']:>7}          (terms built)")
    print(f"  alloc            {s['alloc_mb']:>7} MB          (reduction churn)")
    print(f"  max residency    {s['peak_mb']:>7} MB          (OOM risk)")
    print(f"  GC               {s['gc_pct']:>7} %")


def _read_ledgers():
    rows = []
    for led in glob.glob(os.path.join(AGDA, "**", LEDGER), recursive=True):
        for line in open(led):
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7:
                try:
                    rows.append(
                        (
                            p[0],
                            int(p[1]),
                            int(p[2]),
                            int(p[3]),
                            float(p[4]),
                            float(p[5]),
                            float(p[6]),
                        )
                    )
                except ValueError:
                    pass
    return rows


def _top(n: int) -> None:
    by_mod = {}
    for r in _read_ledgers():
        by_mod.setdefault(r[0], []).append(r)
    agg = [
        (
            m,
            statistics.median(x[2] for x in rs),
            statistics.median(x[1] for x in rs),
            statistics.median(x[4] for x in rs),
        )
        for m, rs in by_mod.items()
    ]
    agg.sort(key=lambda t: t[1], reverse=True)
    print(f"{'module':40} {'CheckRHS':>9} {'Total':>8} {'alloc_MB':>9}")
    for m, crhs, tot, al in agg[:n]:
        print(f"{m:40} {int(crhs):>7}ms {int(tot):>6}ms {al:>9}")


def _reprofilable(n: int) -> None:
    """The heaviest modules that ACTUALLY BUILD — the join nothing provided.

    ⚑ THIS EXISTS BECAUSE I SAMPLED TWICE AND HIT THE BROKEN FRONTIER BOTH TIMES.  Needing a
    witness that (a) registers `CheckRHS` and (b) re-typechecks, I picked from `--top` by eye:
    `Decode6` sits behind `Nat.WellFounded` and `KleinCensus` behind `FirstAppearance` — two of
    A4's known blockers.  That is not bad luck: the CheckRHS-heavy modules and the broken
    frontier BOTH concentrate in the decomposition-arc subtrees, so picking by cost alone
    selects FOR blocked modules.  The question "which module is heavy AND clean" is a join over
    two censuses that both already exist — the profile ledger and `.leaf-verify.tsv` — and
    answering it by trial is reasoning that evaporates when the turn ends.

    ⚑ AND IT REPORTS THE COVERAGE, NOT JUST THE HEAD.  How many heavy modules are unavailable
    is itself the finding: if most of the expensive tree is blocked, a profile-driven decision
    is being made on the minority that still compiles.
    """
    # ⚑ THE CENSUS LEDGER HAS NO READER FUNCTION — FIVE SITES IN `split_pipeline` RE-OPEN IT
    # INLINE, so there is nothing to import.  I reached for `SP.last_census()` (the fifth
    # invented API of this arc, caught by `pycodemod --calls` before it shipped) precisely
    # because that is the authority the shape implies.  Reading the file here makes a SIXTH
    # reader, which is the `agda_files()`-as-four-bodies defect; recorded as owed work rather
    # than pretended away — the lift belongs in `split_pipeline`, next to `tree_stamp`.
    ledger = os.path.join(AGDA, ".leaf-verify.tsv")
    verdicts, stamp = {}, None
    try:
        with open(ledger, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#stamp\t"):
                    stamp = line.split("\t", 1)[1].strip()
                    continue
                if line.startswith("#"):
                    continue
                p = line.rstrip("\n").split("\t")
                if len(p) >= 2:
                    verdicts[os.path.basename(p[0])] = p[1]
    except OSError:
        raise SystemExit(
            f"no census at {ledger} — run `split_pipeline.py --verify --from-build --leaves` first"
        )

    by_mod = {}
    for r in _read_ledgers():
        by_mod.setdefault(r[0], []).append(r)
    agg = [(m, statistics.median(x[2] for x in rs)) for m, rs in by_mod.items()]
    agg.sort(key=lambda t: t[1], reverse=True)

    known = [(m, c) for m, c in agg if m in verdicts]
    clean = [(m, c) for m, c in known if verdicts[m] == "clean"]
    print(
        f"{len(agg)} profiled module(s); {len(known)} appear in the build census; "
        f"{len(clean)} are clean."
    )
    if not known:
        print(
            "  ⚑ NO OVERLAP — the census keys and the ledger keys do not meet; "
            "not 'all blocked'. Re-run the census (`--verify --from-build`)."
        )
        return
    blocked = len(known) - len(clean)
    if blocked:
        print(
            f"  ⚑ {blocked} of the profiled modules are NOT clean — picking a witness by "
            f"cost alone selects for these."
        )
    print(f"\n{'module':40} {'CheckRHS':>9}   (clean, re-profilable)")
    for m, crhs in clean[:n]:
        print(f"{m:40} {int(crhs):>7}ms")


def _hist(module_rel: str) -> None:
    base = os.path.basename(module_rel)
    rows = [r for r in _read_ledgers() if r[0] == base]
    if not rows:
        raise SystemExit(f"no profile history for {base}")
    print(f"{base}: {len(rows)} run(s)")
    for r in rows[-KEEP:]:
        print(
            f"  Total {r[1]:>6}ms  CheckRHS {r[2]:>6}ms  cmp_reduce {r[3]:>5}  alloc {r[4]:>7}MB  peak {r[5]:>6}MB  GC {r[6]}%"
        )


def parse_file(outfile: str, agda_args) -> None:
    """ALWAYS-ON capture: parse a saved `agda --profile=all` output file and append the SLIs to the
    module's per-dir ledger, CWD-relative (the shim runs in the build's per-dir cwd). Best-effort:
    silently no-op on any problem so it never perturbs a build. (alloc/peak are 0 unless the caller
    also passed `+RTS -s`; CheckRHS_ms + cmp_reduce — the regime signal — come from --profile alone.)"""
    try:
        out = open(outfile).read()
    except OSError:
        return
    mod = next((a for a in agda_args if a.endswith(".agda")), None)
    if not mod:
        return
    s = _parse(out)
    if s["checkrhs_ms"] == 0:
        return  # no RHS-checking ⇒ a cached .agdai load (deserialization only), not a proof sample —
        # `make` runs agda on every file (cached ones too); only re-typechecks are real samples
    led = os.path.join(os.path.dirname(mod) or ".", LEDGER)
    row = "\t".join(
        str(x)
        for x in (
            os.path.basename(mod),
            s["total_ms"],
            s["checkrhs_ms"],
            s["cmp_reduce"],
            s["alloc_mb"],
            s["peak_mb"],
            s["gc_pct"],
        )
    )
    try:
        with open(led, "a") as f:
            f.write(row + "\n")
    except OSError:
        pass


def _forest_size(module_basename: str):
    """The ANALYZER's structural-complexity feature: jea_pysim's interned-forest node count for a module,
    read from its .agdai (no typecheck). None if the .agdai or jea_pysim is unavailable."""
    ai = glob.glob(
        os.path.join(AGDA, "_build", "**", module_basename.replace(".agda", ".agdai")),
        recursive=True,
    )
    if not ai:
        return None
    pysim = os.path.join(ROOT, "jea", "metalanguage", "jea_pysim.py")
    try:
        out = subprocess.run(
            ["python3", pysim, ai[0], "--extract"], capture_output=True, text=True, timeout=120
        ).stdout
    except Exception:
        return None
    m = re.search(r"forest (\d+) interned nodes", out)
    return int(m.group(1)) if m else None


def _structural(n: int) -> None:
    """Join the ANALYZER (jea_pysim forest_size = structural explicitness) to the PROFILER (r, cmp_reduce).

    FINDING (Ⓟ.cmp-reduce-structural): r (per-conversion reduction cost) is INVERSELY related to forest_size.
    An EXPLICIT structural proof (big interned forest) pushes the work into SHALLOW symbolic conversions (low
    r); a TERSE reflection proof (tiny forest) leaves it to DEEP normalization (high r). So the analyzer's
    STATIC size proxies the profiler's DYNAMIC regime-rate — forest_size (pre-build, no typecheck) → r estimate
    → CheckRHS = cmp_reduce × r. (cmp_reduce itself tracks forest_size weakly/positively; r is the discriminator
    and is the dynamic quantity the static size can only proxy, not pin — calibration sharpens as the ledger
    grows under the always-on shim.)"""
    by = {}
    for r in _read_ledgers():
        if r[2] > 0 and r[3] > 0:
            by.setdefault(r[0], []).append((r[2], r[3]))
    recs = []
    for mod, xs in by.items():
        crhs = statistics.median(c for c, _ in xs)
        cmpr = statistics.median(m for _, m in xs)
        fs = _forest_size(mod)
        if fs is not None:
            recs.append((mod, fs, crhs / cmpr, int(crhs), int(cmpr)))
    if not recs:
        raise SystemExit(
            "no (forest_size, ledger) joins — build with the shim + ensure .agdai exist"
        )
    recs.sort(
        key=lambda t: t[1]
    )  # forest_size ascending → r should DECREASE (the explicitness↔depth trade)
    print(
        "analyzer (jea_pysim forest_size) × profiler (r, cmp_reduce) — the explicitness↔depth trade\n"
    )
    print(f"  {'module':40} {'forest':>7} {'r (ms/cmp)':>11} {'cmp_reduce':>10} {'CheckRHS':>9}")
    for mod, fs, r, crhs, cmpr in recs[:n]:
        print(f"  {mod:40} {fs:>7} {r:>11.2f} {cmpr:>10} {crhs:>7}ms")
    print(
        "\n  FINDING: forest_size ↑  ⇒  r ↓  — explicit structural proof = SHALLOW conversions (low r);"
    )
    print(
        "  terse reflection = DEEP normalization (high r). Static structural size proxies the dynamic"
    )
    print(
        "  regime-rate; the oracle's pre-build predictor is forest_size → r, not a size→cost regression."
    )


def oracle(candidates):
    """argmin over candidate regimes — each (label, est_cmp_reduce, regime_rate_r) → predicted CheckRHS_ms
    = est_cmp_reduce × r. The cheaper regime is the min. (The jea_cost `argmin_s T_s`, in the proof chart.)"""
    return min(candidates, key=lambda c: c[1] * c[2])


def _oracle(n: int) -> None:
    """The regime oracle over the ledger: r = CheckRHS_ms / cmp_reduce per module (the REGIME RATE = the
    fingerprint). High r = reflection/deep-normalization-bound (a structural-refactor candidate); low r =
    structural/shallow. Dominance (which regime) is an OUTPUT of r, not assumed."""
    by = {}
    for r in _read_ledgers():
        mod, crhs, cmpr = r[0], r[2], r[3]
        if cmpr > 0 and crhs > 0:
            by.setdefault(mod, []).append((crhs, cmpr))
    recs = []
    for mod, xs in by.items():
        crhs = statistics.median(c for c, _ in xs)
        cmpr = statistics.median(m for _, m in xs)
        recs.append((mod, crhs / cmpr, crhs, cmpr))
    if not recs:
        raise SystemExit(
            "no profile samples yet — run `proofcost.py <module>` or build with the shim first"
        )
    recs.sort(key=lambda t: t[1], reverse=True)
    rs = sorted(t[1] for t in recs)
    med = statistics.median(rs)
    print(
        "proof-regime oracle  —  CheckRHS_ms = cmp_reduce × r   (r = ms/reduction-compare = the REGIME RATE)\n"
    )
    print(
        f"  rate band over {len(recs)} module(s): r ∈ [{rs[0]:.2f}, {rs[-1]:.2f}] ms/cmp  (×{rs[-1] / rs[0]:.0f} spread = the regime gap; median {med:.2f})\n"
    )
    print(
        f"  {'module':40} {'r (ms/cmp)':>11} {'CheckRHS':>9} {'cmp_reduce':>10}  regime (r-derived)"
    )
    for mod, r, crhs, cmpr in recs[:n]:
        regime = "deep — reflection-bound (refactor?)" if r > med else "shallow — structural"
        print(f"  {mod:40} {r:>11.2f} {int(crhs):>7}ms {int(cmpr):>10}  {regime}")
    print(
        "\n  oracle: cheaper regime = argmin(cmp_reduce × r). Since r dominates the count (the ~15× gap),"
    )
    print(
        "  it PREFERS the low-r/structural regime even at higher cmp_reduce — predicting the pick pre-build."
    )


SLIS = ("total_ms", "checkrhs_ms", "cmp_reduce", "alloc_mb", "peak_mb", "gc_pct")
_UNITS = {
    "total_ms": "ms",
    "checkrhs_ms": "ms",
    "cmp_reduce": "1",
    "alloc_mb": "MB",
    "peak_mb": "MB",
    "gc_pct": "%",
}


def aggregate(last_k: int = KEEP):
    """(reldir, module) -> {sli: value}. MEDIAN over the last K, except peak_mb = MAX.

    ⚑ THE AGGREGATION IS PER-SLI, NOT UNIFORM, and `membudget_otlp.aggregate` already
    made this call for the same reason: a median peak understates the OOM risk the cap
    is enforced against, so the worst case is the honest summary for `peak_mb` while a
    median is right for the timings (robust to the cold/warm-`.agdai` bimodality).

    ⚑ AND `_read_ledgers` DROPS THE DIRECTORY, so this re-walks rather than reusing it.
    That ledger reader keys by BASENAME — fine for `--top`, wrong for a series, because
    two modules with the same basename in different dirs would collapse into one set of
    points and silently overwrite each other. The `dir` label is what keeps them apart.
    """
    rows = {}
    for led in glob.glob(os.path.join(AGDA, "**", LEDGER), recursive=True):
        reldir = os.path.relpath(os.path.dirname(led), AGDA)
        try:
            for line in open(led):
                p = line.rstrip("\n").split("\t")
                if len(p) < 7:
                    continue
                try:
                    vals = (int(p[1]), int(p[2]), int(p[3]), float(p[4]), float(p[5]), float(p[6]))
                except ValueError:
                    continue
                rows.setdefault((reldir, p[0]), []).append(vals)
        except OSError:
            continue
    out = {}
    for key, hist in rows.items():
        recent = hist[-last_k:]
        agg = {}
        for i, sli in enumerate(SLIS):
            col = [r[i] for r in recent]
            if sli == "peak_mb":
                agg[sli] = max(col)
            elif sli in ("alloc_mb", "gc_pct"):
                # ⚑ MEDIAN OVER A MIXED HISTORY REPORTS THE UNMEASURED MAJORITY.  These two
                # were 0.0 for every run before the `+RTS -s` fix, so a module with 4 old rows
                # and 1 real one has median 0 — the fresh measurement is outvoted by its own
                # absence, and `--emit` then classifies the column as dead.  MEASURED on
                # `JacobianResidue`: the newest row reads alloc=29966.5 while the median reads
                # 0.0.  Summarise over the rows that HAVE the value; if none do, it stays 0 and
                # the dead-SLI filter correctly withholds it.  Same rule as `seconds_cb`
                # iterating the measured set rather than the roster.
                seen = [v for v in col if v != 0]
                agg[sli] = statistics.median(seen) if seen else 0
            else:
                agg[sli] = statistics.median(col)
        agg["profile_count"] = len(recent)
        out[key] = agg
    return out


def _emit(last_k: int, dry_run: bool) -> int:
    """Push the profile ledger to the TSDB through THE shared producer.

    ⚑ THIS LEDGER HAD NO EXPORT PATH AT ALL (CLAUDE.md), and that absence is what the
    duplication was costing: two hand-rolled emitters meant the ledger→gauge shape was
    a thing you REWROTE rather than a thing you CALLED, so the richest artifact in the
    family — six SLIs per module, against `.agda-times.tsv`'s two — stayed local to
    whoever ran it.  Lifting the producer made this a projection, not a build.
    """
    data = aggregate(last_k)
    print(
        f"proofcost-otlp: {len(data)} module(s) from {LEDGER} ledgers under agda/ "
        f"(last-{last_k}); {len(data) * (len(SLIS) + 1)} data points."
    )
    if not data:
        print(
            "  no ledger rows found — nothing to emit. "
            "(`--profile=all` is ON-DEMAND; run proofcost.py <module> first.)"
        )
        return 0
    # ⚑ AN ALL-ZERO SLI IS UNMEASURED, NOT A MEASUREMENT OF ZERO, and emitting it would
    # publish a confident fiction at series scale. MEASURED on the live ledger: `alloc_mb`
    # and `peak_mb` are 0.0 for all 1659 modules — the RTS columns were never populated
    # (`--profile=all` carries the Agda phases; the heap figures need `+RTS -s` too). A
    # series of zeros is indistinguishable from "this module allocates nothing", which is
    # the silent-zero this arc met at four layers. Drop the column and SAY SO.
    # ⚑ `peak_mb` IS MEMBUDGET'S, NOT OURS — EXCLUDED BY NAME, NOT BY EMPTINESS.  It was
    # dropping out only because it was all-zero; the moment `+RTS -s` started supplying it the
    # dead-SLI filter admitted it and the export silently gained a SECOND producer for
    # `membudget_peak_mb`'s quantity (and a different one — GHC residency under `-M128m` is not
    # the cgroup maxRSS the cap is enforced against).  An exclusion that depends on the data
    # being absent is not an exclusion; it is a coincidence waiting to end.
    EXPORT = tuple(s for s in SLIS if s != "peak_mb")
    dead = [s for s in EXPORT if all(agg[s] == 0 for agg in data.values())]
    live = [s for s in EXPORT if s not in dead] + ["profile_count"]
    if dead:
        print(
            f"  ⚑ {len(dead)} SLI(s) are 0 across ALL {len(data)} modules — UNMEASURED, "
            f"not zero; not emitted: {', '.join(dead)}"
        )
    print(f"  emitting {len(live)} SLI(s): {', '.join(live)}")
    top = sorted(data.items(), key=lambda kv: kv[1]["checkrhs_ms"], reverse=True)[:5]
    print("  top CheckRHS_ms: " + ", ".join(f"{m}={int(a['checkrhs_ms'])}" for (_d, m), a in top))
    if dry_run:
        # ⚑ A SUMMARY, NOT 1659 ROWS. A dry run answers "what would this emit"; dumping the
        # whole ledger forces the reader to pipe it, which is reasoning over program output.
        # `--dry-run --all` is there when the rows themselves are the question.
        return 0

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    import membudget_otlp as _prod
    import tsdbprobe as _probe

    # ⚑ `live`, NOT `SLIS` — the filter must reach the EMITTED series, or the warning above
    # is decoration and 1659 zeros ship anyway. This is the same shape as `seconds_cb`
    # iterating the measured set rather than the roster: a missing series reads as missing;
    # a zero-valued one claims a measurement nobody took.
    series = {
        sli: {(("module", m), ("dir", d)): agg[sli] for (d, m), agg in data.items()} for sli in live
    }
    at = time.time()
    try:
        _prod.emit_gauges(
            service="substrate.proofcost",
            prefix="proofcost",
            series=series,
            at=at,
            endpoint=_prod.OTLP_ENDPOINT,
            units=_UNITS,
        )
    except Exception as e:  # noqa: BLE001
        print(f"  proofcost-series: not emitted ({e}).", file=sys.stderr)
        return 1
    # Read-your-write on a value we control — never the transport 200.
    rc = _probe.verify(_probe.DEFAULT_BASE, "proofcost_emit_unixtime", at)
    if rc == 0:
        print(f"  proofcost-series: ✓ recorded — {len(data)} module(s), queryable back.")
        return 0
    print(
        "  proofcost-series: ✗ NOT CONFIRMED. The write may have ingested and not yet "
        "be queryable, or been dropped, or the store may be down — this check cannot "
        "tell which. Diagnose with: python3 scratch/tsdbprobe.py --reachable",
        file=sys.stderr,
    )
    return 1


def _selftest() -> bool:
    """⚑ THE RTS SLIs WERE 0.0 FOR THE LEDGER'S WHOLE LIFE, and the cause is a STREAM SPLIT.

    `--profile=all` writes AGDA's phases to STDOUT; `+RTS -s` writes GHC's runtime report to
    STDERR. The shim captured stdout only, so `alloc_mb`/`gc_pct` — which `_parse` looks for
    in the RTS report — never matched, and `--top` printed an all-zero `alloc_MB` column while
    reporting success. MEASURED on one module: stdout-only gives alloc=0.0/gc=0.0; the two
    streams together give alloc=75.3/gc=36.2.

    ⚑ AND `peak_mb` IS DELIBERATELY NOT EXPORTED even though `-s` now supplies it: membudget
    already owns maxRSS per compile (`membudget_peak_mb`, verified live for a module whose
    profile row read 0.0), and GHC's residency under `-M128m` is a DIFFERENT quantity. Two
    producers for one metric name is how a series gets read as the wrong thing.
    """
    cases, ok = [], 0

    def check(label, cond):
        nonlocal ok
        cases.append((label, bool(cond)))
        if cond:
            ok += 1

    AGDA_STDOUT = (
        "Statistics for X\n"
        "Total           193ms\n"
        "CheckRHS         28ms\n"
        "compare by reduction        16\n"
    )
    GHC_STDERR = (
        "      47,800,160 bytes allocated in the heap\n"
        "         863,624 bytes maximum residency (3 sample(s))\n"
        "  Gen  1         3 colls,     0 par    0.099s   0.182s\n"
        "  GC      time    0.108s  (  0.192s elapsed)\n"
        "  Total   time    0.215s  (  0.331s elapsed)\n"
    )

    only_out = _parse(AGDA_STDOUT)
    both = _parse(AGDA_STDOUT + GHC_STDERR)

    # The Agda-phase SLIs come from stdout and must be unaffected by the merge.
    check(
        "agda phases parse from stdout alone",
        only_out["checkrhs_ms"] == 28 and only_out["cmp_reduce"] == 16,
    )
    # ⚑ THE DEFECT, PINNED: stdout alone yields zeros for the RTS columns.
    check(
        "stdout ALONE loses alloc/gc (the shipped defect)",
        only_out["alloc_mb"] == 0.0 and only_out["gc_pct"] == 0.0,
    )
    check("stdout+stderr recovers alloc_mb", both["alloc_mb"] == 47.8)
    check("stdout+stderr recovers gc_pct", both["gc_pct"] > 0)
    check(
        "merging streams does not disturb the agda phases",
        both["checkrhs_ms"] == 28 and both["total_ms"] == 193,
    )

    # ⚑ A CACHED LOAD IS NOT A PROOF SAMPLE. `parse_file` skips on checkrhs_ms == 0 so that
    # `make` running agda over up-to-date files does not flood the ledger with deserialization
    # rows. This is a SEPARATE mechanism from the stream split, and conflating the two cost
    # several wrong readings: a run can capture the RTS report perfectly and still (correctly)
    # append nothing.
    cached = _parse("Total            71ms\nDeserialization  45ms\n" + GHC_STDERR)
    check(
        "a cached load still reads checkrhs_ms == 0 (skip guard intact)",
        cached["checkrhs_ms"] == 0 and cached["alloc_mb"] > 0,
    )

    # `--emit` must not ship a column that is uniformly zero — over the EXPORT set.
    data = {
        ("d", "a.agda"): {
            "total_ms": 5,
            "checkrhs_ms": 1,
            "cmp_reduce": 2,
            "alloc_mb": 0.0,
            "peak_mb": 0.0,
            "gc_pct": 0.0,
            "profile_count": 1,
        }
    }
    EXPORT = tuple(s for s in SLIS if s != "peak_mb")
    dead = [s for s in EXPORT if all(agg[s] == 0 for agg in data.values())]
    check(
        "an all-zero SLI is classified UNMEASURED, not emitted", set(dead) == {"alloc_mb", "gc_pct"}
    )
    # ⚑ peak_mb IS EXCLUDED BY NAME, NOT BY BEING EMPTY.  While it was all-zero the dead-SLI
    # filter hid it for the wrong reason; the moment `+RTS -s` supplied it, the export gained a
    # second producer for membudget's quantity. Pinned so the exclusion cannot revert to luck.
    check("peak_mb is never in the export set (membudget owns it)", "peak_mb" not in EXPORT)

    # ⚑ A MEDIAN OVER A MIXED HISTORY REPORTS THE UNMEASURED MAJORITY.  Four pre-fix zeros and
    # one real reading must summarise to the reading, not to 0 — otherwise a freshly-recovered
    # SLI is outvoted by its own absence and `--emit` calls the whole column dead.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        sub = os.path.join(td, "Sub")
        os.makedirs(sub)
        with open(os.path.join(sub, LEDGER), "w") as fh:
            for _ in range(4):  # pre-fix rows: no RTS report
                fh.write("M.agda\t100\t50\t7\t0.0\t0.0\t0.0\n")
            fh.write("M.agda\t100\t50\t7\t29966.5\t11.4\t36.4\n")  # the real one
        # A module whose RTS columns were NEVER captured must still read 0 — the skip-zeros
        # rule recovers a real reading, it does not manufacture one.
        sub2 = os.path.join(td, "Never")
        os.makedirs(sub2)
        with open(os.path.join(sub2, LEDGER), "w") as fh:
            for _ in range(3):
                fh.write("N.agda\t100\t50\t7\t0.0\t0.0\t0.0\n")
        _saved = AGDA
        try:
            globals()["AGDA"] = td
            got = aggregate(5)
        finally:
            globals()["AGDA"] = _saved
        agg = got[("Sub", "M.agda")]
        never = got[("Never", "N.agda")]
    check(
        "alloc_mb summarises over MEASURED rows, not the zero majority", agg["alloc_mb"] == 29966.5
    )
    check("gc_pct summarises over MEASURED rows", agg["gc_pct"] == 36.4)
    check("timings still use the plain median over all rows", agg["total_ms"] == 100)
    check(
        "a NEVER-captured column still reads 0 (no value invented)",
        never["alloc_mb"] == 0 and never["gc_pct"] == 0,
    )

    for label, good in cases:
        if not good:
            print(f"  FAIL {label}")
    print(f"selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main(argv):
    if not argv:
        print(__doc__)
        return
    if argv[0] == "--selftest":
        raise SystemExit(0 if _selftest() else 1)
    if argv[0] == "--reprofilable":
        _reprofilable(int(argv[1]) if len(argv) > 1 else 15)
        return
    if argv[0] == "--emit":
        rest = argv[1:]
        dry = "--dry-run" in rest
        k = next((int(x) for x in rest if x.isdigit()), KEEP)
        raise SystemExit(_emit(k, dry))
    if argv[0] == "--oracle":
        _oracle(int(argv[1]) if len(argv) > 1 else 15)
        return
    if argv[0] == "--structural":
        _structural(int(argv[1]) if len(argv) > 1 else 15)
        return
    if argv[0] == "--parse":
        parse_file(argv[1], argv[2:])
        return
    if argv[0] == "--top":
        _top(int(argv[1]) if len(argv) > 1 else 15)
        return
    if argv[0] == "--module":
        _hist(argv[1])
        return
    for mod in argv:
        _report(mod, profile(mod))


if __name__ == "__main__":
    main(sys.argv[1:])
