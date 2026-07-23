#!/usr/bin/env python3
"""buildtime.py — genlop-style build-time history + ETA for the Agda build.

Per-module typecheck times live in a ledger PARALLEL TO THE RECURSIVE-MAKE STRUCTURE: each source
dir gets a `.agda-times.tsv` ALONGSIDE its Makefile (gitignored — timing is hardware/cache-specific,
not a shared fact), holding `module<TAB>seconds[<TAB>peak_mb]` rows (append-only; small lines append
atomically, so parallel `make -j` writers don't corrupt it). The membudget wrapper (the agda shim's
universal choke point) appends one row per compile — including the pre-commit `make -C agda -j` full build
(⟡cap-384, the single build path). This module reads them all and estimates genlop-style:

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


def _read(col: int) -> dict:
    """Walk agda/ for per-dir ledgers; return {module_rel: [value, …]} (last-K) from column `col`
    (1 = seconds, 2 = peak_mb). Rows missing/blank in that column are skipped."""
    out: dict = {}
    for dp, _, fns in os.walk(AGDA):
        if LEDGER not in fns:
            continue
        reldir = os.path.relpath(dp, AGDA)
        try:
            with open(os.path.join(dp, LEDGER)) as f:
                for ln in f:
                    parts = ln.rstrip("\n").split("\t")
                    if len(parts) <= col or parts[col] == "":
                        continue
                    try:
                        v = float(parts[col])
                    except ValueError:
                        continue
                    out.setdefault(os.path.join(reldir, parts[0]), []).append(v)
        except OSError:
            continue
    return {m: vs[-KEEP:] for m, vs in out.items()}


def read_all() -> dict:
    """{module_rel: [seconds, …]} (last-K per module)."""
    return _read(1)


def read_mem() -> dict:
    """{module_rel: [peak_mb, …]} (last-K per module) — the membudget peak-mem capture."""
    return _read(2)


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


def autobudget(peak_mb: float, default: int = 192, cap: int = 384) -> int:
    """The membudget _auto_mb rule (mirrors AGDA_MB_DEFAULT=192 / AGDA_MB_MAX=384): round peak UP to the
    next POWER OF TWO (floor 64, cap). The pow2 step IS the safety margin — it sits 2^n ± 2^(n-1) around
    the need (up to a 2^(n-1) headroom band), so no extra fudge and no over-rounding (peak 65 → 128, not
    256). A lease is a hard kill cap, so rounding UP keeps cap ≥ peak; a too-tight first guess self-corrects
    via membudget's retry-on-OOM ladder (192→384).

    Ceiling = 384MiB (⟡cap-384): the full build runs every module at `+RTS -M256m` (256MB heap) and
    passes, so worst-case maxRSS ≈ 256MB heap + ~0.1GB RTS overhead ≈ 356MB < 384. cap is NOT a power of
    two: a peak that rounds to 512 is clamped down to 384 (still ≥ any real peak by the -M256m invariant).
    The 384 ceiling is a FORCING FUNCTION — a module that would exceed it must SEAL its heavy neutrals
    `opaque` or import a cheaper proof, not grow the cap."""
    if peak_mb <= 0:
        return default
    v = 64
    while v < peak_mb:
        v *= 2
    return min(cap, v)


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
    elif cmd in ("--mem", "-M"):
        mem = read_mem(); n = int(argv[1]) if len(argv) > 1 else 20
        ranked = sorted(((max(v), m) for m, v in mem.items() if v), reverse=True)
        if not ranked:
            print("no peak-mem history yet (needs /usr/bin/time + a shimmed build)."); return 0
        print(f"heaviest {min(n, len(ranked))} modules (max peak-mem) — drives the autobudget lease:")
        for mb, m in ranked[:n]:
            print(f"  {autobudget(mb):>6}MB lease  (peak {int(mb)}MB)  {m}")
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
