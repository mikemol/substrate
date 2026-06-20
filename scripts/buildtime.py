#!/usr/bin/env python3
"""buildtime.py — genlop-style build-time history + ETA for the Agda build.

Per-module typecheck times live in a ledger PARALLEL TO THE RECURSIVE-MAKE STRUCTURE: each source
dir gets a `.agda-times.tsv` ALONGSIDE its Makefile (gitignored — timing is hardware/cache-specific,
not a shared fact), holding `module<TAB>seconds[<TAB>peak_mb]` rows (append-only; small lines append
atomically, so parallel `make -j` writers don't corrupt it). The membudget wrapper (the agda shim's
universal choke point) appends one row per compile; full_build_check.py appends its run + shows a live
ETA. This module reads them all and estimates genlop-style:

  buildtime.py --predict            # genlop -p: estimated total for the full build, from history
  buildtime.py --predict A B …      # estimate a specific module list (relpaths from agda/)
  buildtime.py --top [N]            # the N slowest modules (build hot-spots; default 20)
  buildtime.py --module PATH        # genlop -t: one module's recorded history
  buildtime.py --stats              # coverage + global median
  buildtime.py --compact            # trim every per-dir ledger to the last K rows per module

Estimate per module = MEDIAN of its last K runs (robust to the cold/warm-.agdai bimodality); an unseen
module falls back to the global median. Wall ≈ Σ CPU / J for J-way parallelism.
"""
import os, sys, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
AGDA = os.path.join(ROOT, "agda")
LEDGER = ".agda-times.tsv"        # per-dir, alongside each Makefile
KEEP = 5                          # last-K rows kept per module


# ---------------------------------------------------------------- storage (per-dir, parallel to make)
def _dir_of(module_rel: str) -> str:
    return os.path.join(AGDA, os.path.dirname(module_rel))


def append(module_rel: str, seconds: float, peak_mb=None) -> None:
    """Append one timing row to the module's per-dir ledger (atomic small append; best-effort)."""
    row = f"{os.path.basename(module_rel)}\t{round(seconds, 2)}"
    if peak_mb:
        row += f"\t{int(peak_mb)}"
    try:
        with open(os.path.join(_dir_of(module_rel), LEDGER), "a") as f:
            f.write(row + "\n")
    except OSError:
        pass


def read_all() -> dict:
    """Walk agda/ for per-dir ledgers; return {module_rel: [seconds, …]} (last-K per module)."""
    hist: dict = {}
    for dp, _, fns in os.walk(AGDA):
        if LEDGER not in fns:
            continue
        reldir = os.path.relpath(dp, AGDA)
        try:
            with open(os.path.join(dp, LEDGER)) as f:
                for ln in f:
                    parts = ln.rstrip("\n").split("\t")
                    if len(parts) < 2:
                        continue
                    try:
                        sec = float(parts[1])
                    except ValueError:
                        continue
                    hist.setdefault(os.path.join(reldir, parts[0]), []).append(sec)
        except OSError:
            continue
    return {m: ts[-KEEP:] for m, ts in hist.items()}


def compact() -> int:
    """Rewrite every per-dir ledger keeping only the last K rows per module. Returns files compacted."""
    n = 0
    for dp, _, fns in os.walk(AGDA):
        if LEDGER not in fns:
            continue
        path = os.path.join(dp, LEDGER)
        per: dict = {}
        try:
            with open(path) as f:
                for ln in f:
                    p = ln.rstrip("\n").split("\t")
                    if len(p) >= 2:
                        per.setdefault(p[0], []).append(ln.rstrip("\n"))
        except OSError:
            continue
        out = [r for rows in per.values() for r in rows[-KEEP:]]
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            f.write("\n".join(out) + ("\n" if out else ""))
        os.replace(tmp, path); n += 1
    return n


# ---------------------------------------------------------------- estimation
def global_median(hist: dict) -> float:
    allt = [t for ts in hist.values() for t in ts]
    return statistics.median(allt) if allt else 1.0


def est(hist: dict, module_rel: str, fallback: float) -> float:
    ts = hist.get(module_rel)
    return statistics.median(ts) if ts else fallback


def predict(hist: dict, modules) -> dict:
    fb = global_median(hist)
    return {"total_cpu": sum(est(hist, m, fb) for m in modules),
            "known": sum(1 for m in modules if hist.get(m)),
            "n": len(modules), "fallback": fb}


def fmt(sec: float) -> str:
    sec = int(round(sec)); h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}h{m:02d}m{s:02d}s" if h else (f"{m}m{s:02d}s" if m else f"{s}s")


# ---------------------------------------------------------------- CLI
def _all_modules() -> list:
    sub = os.path.join(AGDA, "Substrate")
    out = []
    for dp, _, fns in os.walk(sub):
        for fn in fns:
            if fn.endswith(".agda"):
                rel = os.path.relpath(os.path.join(dp, fn), AGDA)
                if rel != os.path.join("Substrate", "All.agda"):
                    out.append(rel)
    return sorted(out)


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    hist = read_all(); cmd = argv[0]
    if cmd in ("--predict", "-p"):
        mods = argv[1:] or _all_modules()
        p = predict(hist, mods); J = 6
        print(f"genlop -p: ~{fmt(p['total_cpu'])} CPU  (~{fmt(p['total_cpu'] / J)} wall at -j{J})  for "
              f"{p['n']} modules; {p['known']} have history, {p['n'] - p['known']} use global median "
              f"{p['fallback']:.1f}s.")
    elif cmd in ("--top", "-T"):
        n = int(argv[1]) if len(argv) > 1 else 20
        ranked = sorted(((statistics.median(ts), m) for m, ts in hist.items() if ts), reverse=True)
        if not ranked:
            print("no history yet — run a build first."); return 0
        print(f"slowest {min(n, len(ranked))} modules (median typecheck):")
        for t, m in ranked[:n]:
            print(f"  {fmt(t):>9}  {m}")
    elif cmd in ("--module", "-t"):
        if len(argv) < 2:
            print("usage: --module PATH"); return 2
        ts = hist.get(argv[1])
        print(f"{argv[1]}: last {len(ts)} runs {ts}  median {fmt(statistics.median(ts))}" if ts
              else f"no history for {argv[1]}")
    elif cmd == "--stats":
        mods = _all_modules(); known = sum(1 for m in mods if hist.get(m))
        print(f"ledger: {len(hist)} modules timed; {known}/{len(mods)} current modules have history; "
              f"global median {global_median(hist):.2f}s")
    elif cmd == "--compact":
        print(f"compacted {compact()} per-dir ledgers (kept last {KEEP}/module)")
    else:
        print(f"unknown command {cmd!r}"); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
