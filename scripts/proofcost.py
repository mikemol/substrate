#!/usr/bin/env python3
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

The per-dir ledger is `.agda-profile.tsv` alongside each Makefile (gitignored — hardware-specific),
rows `module<TAB>total_ms<TAB>checkrhs_ms<TAB>cmp_reduce<TAB>alloc_mb<TAB>peak_mb<TAB>gc_pct`.

NOTE: `--profile=all` roughly doubles compile time, so this is ON-DEMAND (not wired into every
build the way peak_mb is). Run it on the module/regime you are deciding about.
"""
import os, re, sys, subprocess, glob, statistics

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
    total_ms   = grab(r"^Total\s+([\d,]+)ms")
    checkrhs   = grab(r"CheckRHS\s+([\d,]+)ms")
    deser_ms   = grab(r"^Deserialization\s+([\d,]+)ms")
    cmp_reduce = grab(r"^compare by reduction\s+([\d,]+)\s*$")
    nodes      = grab(r"^Node\s+\(fresh\)\s+([\d,]+)")
    alloc_b    = grab(r"([\d,]+) bytes allocated in the heap")
    resid_b    = grab(r"([\d,]+) bytes maximum residency")
    gc_s       = grab(r"GC\s+time\s+([\d.]+)s", float, 0.0)
    rts_tot_s  = grab(r"Total\s+time\s+([\d.]+)s", float, 0.0)
    return {
        "total_ms": total_ms, "checkrhs_ms": checkrhs, "deser_ms": deser_ms,
        "cmp_reduce": cmp_reduce, "nodes": nodes,
        "alloc_mb": round(alloc_b / 1e6, 1), "peak_mb": round(resid_b / 1e6, 1),
        "gc_pct": round(100 * gc_s / rts_tot_s, 1) if rts_tot_s else 0.0,
    }


def _agdai_paths(module_rel: str):
    base = os.path.basename(module_rel).replace(".agda", ".agdai")
    return glob.glob(os.path.join(AGDA, "_build", "**", base), recursive=True)


def profile(module_rel: str) -> dict:
    """Force a re-typecheck of `module_rel` (relpath from agda/) under --profile=all + RTS -s."""
    for p in _agdai_paths(module_rel):           # evict the cached interface → real re-typecheck
        try: os.remove(p)
        except OSError: pass
    proc = subprocess.run(
        ["agda", "--safe", "-i.", module_rel, "--profile=all", "+RTS", "-s", "-RTS"],
        cwd=AGDA, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 and "Total" not in out:
        sys.stderr.write(out[-1500:]); raise SystemExit(f"agda failed on {module_rel} (rc={proc.returncode})")
    sli = _parse(out)
    _append(module_rel, sli)
    return sli


def _append(module_rel: str, s: dict) -> None:
    led = os.path.join(AGDA, os.path.dirname(module_rel), LEDGER)
    row = "\t".join(str(x) for x in (os.path.basename(module_rel), s["total_ms"], s["checkrhs_ms"],
                                     s["cmp_reduce"], s["alloc_mb"], s["peak_mb"], s["gc_pct"]))
    try:
        with open(led, "a") as f: f.write(row + "\n")
    except OSError: pass


def _report(module_rel: str, s: dict) -> None:
    pct = (100 * s["checkrhs_ms"] // s["total_ms"]) if s["total_ms"] else 0
    print(f"\n{module_rel}")
    print(f"  Total            {s['total_ms']:>7} ms")
    print(f"  CheckRHS         {s['checkrhs_ms']:>7} ms  ({pct}%)   ← proof normalization (the hot path)")
    print(f"  Deserialization  {s['deser_ms']:>7} ms          (dependency load)")
    print(f"  compare-by-reduction {s['cmp_reduce']:>7}          ← defeq forcing reduction (cache-miss analog)")
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
                try: rows.append((p[0], int(p[1]), int(p[2]), int(p[3]), float(p[4]), float(p[5]), float(p[6])))
                except ValueError: pass
    return rows


def _top(n: int) -> None:
    by_mod = {}
    for r in _read_ledgers(): by_mod.setdefault(r[0], []).append(r)
    agg = [(m, statistics.median(x[2] for x in rs), statistics.median(x[1] for x in rs),
            statistics.median(x[4] for x in rs)) for m, rs in by_mod.items()]
    agg.sort(key=lambda t: t[1], reverse=True)
    print(f"{'module':40} {'CheckRHS':>9} {'Total':>8} {'alloc_MB':>9}")
    for m, crhs, tot, al in agg[:n]:
        print(f"{m:40} {int(crhs):>7}ms {int(tot):>6}ms {al:>9}")


def _hist(module_rel: str) -> None:
    base = os.path.basename(module_rel)
    rows = [r for r in _read_ledgers() if r[0] == base]
    if not rows: raise SystemExit(f"no profile history for {base}")
    print(f"{base}: {len(rows)} run(s)")
    for r in rows[-KEEP:]:
        print(f"  Total {r[1]:>6}ms  CheckRHS {r[2]:>6}ms  cmp_reduce {r[3]:>5}  alloc {r[4]:>7}MB  peak {r[5]:>6}MB  GC {r[6]}%")


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
    row = "\t".join(str(x) for x in (os.path.basename(mod), s["total_ms"], s["checkrhs_ms"],
                                     s["cmp_reduce"], s["alloc_mb"], s["peak_mb"], s["gc_pct"]))
    try:
        with open(led, "a") as f: f.write(row + "\n")
    except OSError:
        pass


def _forest_size(module_basename: str):
    """The ANALYZER's structural-complexity feature: jea_pysim's interned-forest node count for a module,
    read from its .agdai (no typecheck). None if the .agdai or jea_pysim is unavailable."""
    ai = glob.glob(os.path.join(AGDA, "_build", "**", module_basename.replace(".agda", ".agdai")), recursive=True)
    if not ai:
        return None
    pysim = os.path.join(ROOT, "jea", "metalanguage", "jea_pysim.py")
    try:
        out = subprocess.run(["python3", pysim, ai[0], "--extract"],
                             capture_output=True, text=True, timeout=120).stdout
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
        raise SystemExit("no (forest_size, ledger) joins — build with the shim + ensure .agdai exist")
    recs.sort(key=lambda t: t[1])  # forest_size ascending → r should DECREASE (the explicitness↔depth trade)
    print("analyzer (jea_pysim forest_size) × profiler (r, cmp_reduce) — the explicitness↔depth trade\n")
    print(f"  {'module':40} {'forest':>7} {'r (ms/cmp)':>11} {'cmp_reduce':>10} {'CheckRHS':>9}")
    for mod, fs, r, crhs, cmpr in recs[:n]:
        print(f"  {mod:40} {fs:>7} {r:>11.2f} {cmpr:>10} {crhs:>7}ms")
    print("\n  FINDING: forest_size ↑  ⇒  r ↓  — explicit structural proof = SHALLOW conversions (low r);")
    print("  terse reflection = DEEP normalization (high r). Static structural size proxies the dynamic")
    print("  regime-rate; the oracle's pre-build predictor is forest_size → r, not a size→cost regression.")


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
        raise SystemExit("no profile samples yet — run `proofcost.py <module>` or build with the shim first")
    recs.sort(key=lambda t: t[1], reverse=True)
    rs = sorted(t[1] for t in recs)
    med = statistics.median(rs)
    print("proof-regime oracle  —  CheckRHS_ms = cmp_reduce × r   (r = ms/reduction-compare = the REGIME RATE)\n")
    print(f"  rate band over {len(recs)} module(s): r ∈ [{rs[0]:.2f}, {rs[-1]:.2f}] ms/cmp  (×{rs[-1]/rs[0]:.0f} spread = the regime gap; median {med:.2f})\n")
    print(f"  {'module':40} {'r (ms/cmp)':>11} {'CheckRHS':>9} {'cmp_reduce':>10}  regime (r-derived)")
    for mod, r, crhs, cmpr in recs[:n]:
        regime = "deep — reflection-bound (refactor?)" if r > med else "shallow — structural"
        print(f"  {mod:40} {r:>11.2f} {int(crhs):>7}ms {int(cmpr):>10}  {regime}")
    print("\n  oracle: cheaper regime = argmin(cmp_reduce × r). Since r dominates the count (the ~15× gap),")
    print("  it PREFERS the low-r/structural regime even at higher cmp_reduce — predicting the pick pre-build.")


def main(argv):
    if not argv:
        print(__doc__); return
    if argv[0] == "--oracle":
        _oracle(int(argv[1]) if len(argv) > 1 else 15); return
    if argv[0] == "--structural":
        _structural(int(argv[1]) if len(argv) > 1 else 15); return
    if argv[0] == "--parse":
        parse_file(argv[1], argv[2:]); return
    if argv[0] == "--top":
        _top(int(argv[1]) if len(argv) > 1 else 15); return
    if argv[0] == "--module":
        _hist(argv[1]); return
    for mod in argv:
        _report(mod, profile(mod))


if __name__ == "__main__":
    main(sys.argv[1:])
