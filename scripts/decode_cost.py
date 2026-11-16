#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""decode_cost.py — ⟡gqs-catalog-engine: the CONTROLLER/ACTUATOR decode-cost model for the batched catalog
build. Rides the roofline the GPU-JEA way (jea_cost / jea_navigator / jea_telemetry), NOT a hardcoded
crossover:

  SURFACES (host models the topology ONCE)  — per-core STRUCTURAL bound = .agdai bytes (stat-able BEFORE
      deciding to decode) + a fixed t_launch; per-core INTRINSIC decode estimate from a STATE-STAMPED ledger
      (median-of-last-K; the buildtime.py shape). Read once per run/box; adapts to hardware for free.
  PACKAGE  (host refreshes an EPOCH-COHERENT stat package per window) — `package()` CO-READS the live_state in
      ONE poll (getloadavg → available CPU → P_effective), and COMPOSES the achieved cost + the operating point
      P* WITHIN that one epoch. The consumer reads a WHOLE package; it never poll-here-multiplies-there, so the
      Δ-F6 eff×state double-count / TOCTOU window is closed BY CONSTRUCTION (jea_telemetry). [[reread-meters-toctou]]
  CONSUME  (the decode loop = actuator) — reads the package, decodes the window serial or via a ThreadPool of
      P*; records each decode's (bytes, seconds, load@measure) back to the ledger. NEVER re-reads meters itself.

The operating point tracks the LIVE contention (poll, don't benchmark) — so it adapts on a loaded box without
an idle-box measurement, and self-calibrates as the ledger fills. [[feedback_cost_is_structural_times_live]].

Fallback constants are MEASURED (⟡gce-model-confirm, 2026-07-18: 60 cores, decode CPU-time vs bytes R²=0.82):
cost ≈ t_launch(fixed ~30ms shim-spawn+overhead) + rate·bytes — a launch+work sum, dominance an OUTPUT.
"""

import os
import statistics

_HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.environ.get(
    "DECODE_COST_LEDGER", os.path.join(_HERE, ".decode-cost.tsv")
)  # gitignored; hw-specific
NPROC = os.cpu_count() or 1
K = 5  # median of last-K per core (buildtime shape; robust to the cold/warm bimodality)
T_LAUNCH = 0.030  # s — fixed shim-spawn + fixed decode overhead (the measured intercept)
RATE = 0.62e-6  # s/byte — the measured per-byte work slope


def load_hist():
    """{core_id: [(bytes, seconds, load), … last-K]} — the state-stamped decode-cost ledger (best-effort)."""
    hist = {}
    try:
        with open(LEDGER) as f:
            for line in f:
                cid, b, s, ld = line.rstrip("\n").split("\t")
                hist.setdefault(cid, []).append((int(b), float(s), float(ld)))
    except FileNotFoundError:
        pass  # no ledger yet — an honest empty history
    except Exception as e:
        # ⚑⚑ A PARTIAL READ USED TO RETURN AS A COMPLETE ONE.  This was TWO stacked
        # swallows — `except (FileNotFoundError, ValueError): pass` followed by a
        # redundant `except Exception: pass` — so a malformed line mid-file stopped the
        # loop and `hist` was returned holding only the rows read BEFORE it.  Every
        # estimate downstream is computed from that truncated history, and nothing said
        # so: the caller cannot distinguish "this core has three measurements" from
        # "this core has three measurements THAT PARSED".
        #
        # ⚑ THE READ STILL SUCCEEDS — a cost model must not fail because one row is
        # corrupt, and a raise here would make a best-effort learner into a hard
        # dependency.  What changes is that the truncation is REPORTED.  Found by
        # `pycodemod --swallows`, which flags a discard whose work feeds a returned
        # value; `decode_cost` returns `hist` directly.
        print(
            "decode_cost: ledger read stopped early at row %d (%s: %s) — history is "
            "TRUNCATED, estimates below are computed from a partial ledger"
            % (sum(len(v) for v in hist.values()) + 1, type(e).__name__, e),
            file=__import__("sys").stderr,
        )
    return {c: v[-K:] for c, v in hist.items()}


def record(core_id, nbytes, seconds, load):
    """Append ONE state-stamped decode measurement (best-effort; never raises — only learn from real runs)."""
    try:
        with open(LEDGER, "a") as f:
            f.write(f"{core_id}\t{int(nbytes)}\t{seconds:.4f}\t{load:.2f}\n")
    except Exception:
        pass


def estimate(core_id, nbytes, hist):
    """The per-core INTRINSIC decode-seconds estimate: median-of-last-K measured seconds (the buildtime shape),
    or the structural fallback t_launch + rate·bytes for an unseen core. (State-stamp `load` is carried in the
    ledger for a future normalize-by-load refinement — ⟡gce-normalize; the median is the buildtime baseline.)"""
    rows = hist.get(core_id)
    if rows:
        return statistics.median(s for _b, s, _ld in rows)
    return T_LAUNCH + RATE * max(0, nbytes)


def poll_live_state():
    """CO-READ the live contention in ONE epoch (the single meter read the host composes from): available CPU
    = nproc − load1 → P_effective ∈ [1, nproc]; live_state = nproc / P_effective (≥1 — the contention factor a
    decode would see NOW). One getloadavg() = the atomic co-read; the loop never calls this itself."""
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = 0.0
    p_eff = max(1, min(NPROC, round(NPROC - load1)))
    return {"load1": load1, "P_effective": p_eff, "live_state": NPROC / p_eff, "nproc": NPROC}


def package(window, sizes, hist, live=None):
    """HOST composes the EPOCH-COHERENT stat package for ONE window of core_ids. Co-reads live_state ONCE (or
    takes an injected epoch for testing), composes achieved cost (intrinsic × live_state) + the operating point
    P* = argmin(serial, parallel) — all WITHIN this one epoch. Returns the package the consume loop reads.
    Dominance (serial vs parallel) is an OUTPUT: parallel wins iff there is >1 core AND free CPU (P*>1)."""
    live = live or poll_live_state()
    work = sum(
        estimate(c, sizes.get(c, 0), hist) for c in window
    )  # intrinsic serial work (this epoch)
    ls = live["live_state"]
    p_star = max(1, min(live["P_effective"], len(window)))
    cost_serial = work * ls  # P=1: full serial work × contention
    cost_parallel = (work / p_star) * ls  # pool of P*: launch+work both parallelize
    parallel = p_star > 1 and cost_parallel < cost_serial
    return {
        **live,
        "n": len(window),
        "work": work,
        "P_star": p_star if parallel else 1,
        "parallel": parallel,
        "cost_serial": cost_serial,
        "cost_parallel": cost_parallel,
    }


def project_corpus(sizes, hist=None, live=None):
    """⒯ — PROJECT the ingest DECODE cost over a whole population of cores. `sizes` is
    `{core_id: bytes}`; returns the package plus the per-core mean, so a caller can size either
    a cold full-corpus catch-up (n = the corpus) or a warm steady-state build (n = the rebuild
    frontier) from ONE model.

    ⚑⚑ THIS MODE EXISTS BECAUSE WIRING INGESTION INTO `make` MAKES STORE WRITES A ROUTINE PART
    OF EVERY BUILD (⒯, 2026-08-14), and that turns the store's compute envelope from incidental
    into STRUCTURAL. A cost that shows up in every build is a cost someone will fix — which is
    an argument FOR the design — but it has to be said as a number before the build says it
    slowly. `package()` already composed this for ONE window; there was no way to ask it about
    a population, so the question was answerable only by running the thing being sized.

    ⚑ IT MODELS THE DECODE, AND NOT THE INSERT — stated because the gap is the load-bearing
    part. `T_LAUNCH`/`RATE` were fitted to shim decode (R²=0.82 over 60 cores) and the ledger
    records decode seconds; the postgres INSERT under the store's `CPUQuota` is in NEITHER. So
    this is a measured LOWER BOUND on the per-core cost, never an estimate of the total, and a
    reader who quotes it as the total will under-size exactly the half that is rate-limited.
    """
    hist = load_hist() if hist is None else hist
    pk = package(list(sizes), sizes, hist, live=live)
    n = max(1, pk["n"])
    return {**pk, "mean_s": pk["work"] / n}


def corpus_sizes(root, filt=""):
    """`{relpath: bytes}` for every `.agdai` under `root` whose path contains `filt` — the
    STRUCTURAL surface `estimate` keys on, stat-able without decoding anything."""
    import glob

    out = {}
    for p in sorted(glob.iglob(os.path.join(root, "**", "*.agdai"), recursive=True)):
        if filt and filt not in p:
            continue
        try:
            out[os.path.relpath(p, root)] = os.path.getsize(p)
        except OSError:
            continue
    return out


if __name__ == "__main__":
    import sys, tempfile

    if "--selftest" in sys.argv:
        # ⚑ THIS SUITE PASSED AND WAS UNREADABLE FOR AS LONG AS IT EXISTED.  It
        # printed `ALL PASS` — prose — and `run_selftests` learned every result
        # from `re.compile(r"selftest:\s*(\d+)\s*/\s*(\d+)")`, so seven real cases
        # reported SILENT.  Not broken; UNCOUNTED, which is worse: a shrinking
        # population reads as a smaller green total.
        #
        # ⚑ AND THE COUNT IS NOT A FORMAT-STRING EDIT.  `ok` was a list of
        # (name, bool) with the verdict folded by `all(...)` — the count existed
        # and was thrown away at the last line.  `rungs.Cases` is the shared
        # authority for exactly this (55 defs, 55 reimplementing, 0 delegating),
        # so the tail becomes a delegation rather than a 56th copy.
        sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "scratch"))
        import rungs

        check = rungs.Cases(key="scripts/decode_cost.py")
        d = tempfile.mkdtemp()
        os.environ["DECODE_COST_LEDGER"] = os.path.join(d, "c.tsv")
        globals()["LEDGER"] = os.environ["DECODE_COST_LEDGER"]
        # unseen core → structural fallback estimate
        h = load_hist()
        e = estimate("cX", 100000, h)
        check(
            "fallback estimate = t_launch+rate·bytes",
            abs(e - (T_LAUNCH + RATE * 100000)) < 1e-9,
            True,
        )
        # record → ledger → median-of-K estimate
        for s in (0.05, 0.06, 0.055, 0.05, 0.07, 0.052):
            record("cA", 100000, s, 1.0)
        h = load_hist()
        check("ledger keeps last-K", len(h["cA"]), K)
        check(
            "estimate = median-of-K",
            abs(estimate("cA", 100000, h) - statistics.median([0.06, 0.055, 0.05, 0.07, 0.052]))
            < 1e-9,
            True,
        )
        # package: idle epoch (P_eff=nproc) → parallel for a multi-core window; serial for 1 core
        idle = {"load1": 0.0, "P_effective": NPROC, "live_state": 1.0, "nproc": NPROC}
        pk = package(["a", "b", "c", "d"], {"a": 1e5, "b": 1e5, "c": 1e5, "d": 1e5}, {}, live=idle)
        check("idle multi-core → parallel", (pk["parallel"], pk["P_star"]), (True, min(NPROC, 4)))
        pk1 = package(["a"], {"a": 1e5}, {}, live=idle)
        check("single core → serial", (pk1["parallel"], pk1["P_star"]), (False, 1))
        # package: fully-loaded epoch (P_eff=1) → serial even for a big window (contention-adaptive)
        busy = {"load1": float(NPROC), "P_effective": 1, "live_state": float(NPROC), "nproc": NPROC}
        pkb = package(["a", "b", "c", "d"], {"a": 1e5, "b": 1e5, "c": 1e5, "d": 1e5}, {}, live=busy)
        check("loaded box → serial (P_eff=1)", (pkb["parallel"], pkb["P_star"]), (False, 1))
        # dominance is an OUTPUT: cost_parallel < cost_serial exactly when parallel chosen
        check(
            "dominance output consistent", (pk["cost_parallel"] < pk["cost_serial"]), pk["parallel"]
        )
        # ⒯ — the population projection. Driven on an INJECTED epoch and injected sizes, so the
        # case asserts the AGGREGATION rather than the box's current load.
        pj = project_corpus({"a": 1e5, "b": 1e5, "c": 1e5, "d": 1e5}, hist={}, live=idle)
        check(
            "project_corpus sums the per-core estimates",
            abs(pj["work"] - 4 * (T_LAUNCH + RATE * 1e5)) < 1e-9,
            True,
        )
        check(
            "...and reports the per-core MEAN, so a frontier of any size can be sized",
            abs(pj["mean_s"] - (T_LAUNCH + RATE * 1e5)) < 1e-9,
            True,
        )
        sys.exit(check.report())
    # ⒯ — `--project [FILTER]`: the corpus/frontier ingest-decode projection.  --control: the
    # CLI parse and the branch live HERE; `project_corpus`/`corpus_sizes` carry no argv.
    if "--project" in sys.argv:
        _root = os.path.join(os.path.dirname(_HERE), "agda", "_build")
        _f = [a for a in sys.argv[1:] if not a.startswith("--")]
        _sz = corpus_sizes(_root, _f[0] if _f else "")
        _pj = project_corpus(_sz)
        print(
            "decode-cost projection over %d core(s) under filter %r (root %s)"
            % (_pj["n"], _f[0] if _f else "", _root)
        )
        print(
            "  live epoch: load1=%.2f P_effective=%d live_state=%.2f (nproc=%d)"
            % (_pj["load1"], _pj["P_effective"], _pj["live_state"], _pj["nproc"])
        )
        print(
            "  intrinsic decode work: %.1f s serial (mean %.3f s/core)"
            % (_pj["work"], _pj["mean_s"])
        )
        print(
            "  achieved at THIS epoch: %.1f s serial │ %.1f s at P*=%d"
            % (_pj["cost_serial"], _pj["cost_parallel"], _pj["P_star"])
        )
        print("  ⚑ DECODE ONLY — the postgres INSERT under the store's CPUQuota is NOT modelled")
        print("    here (neither T_LAUNCH/RATE nor the ledger measure it). Read this as a")
        print("    measured LOWER BOUND per core, never as the total.")
        sys.exit(0)
    print(f"decode_cost: nproc={NPROC} ledger={LEDGER}")
    print(f"  live_state now: {poll_live_state()}")
    print("  --project [FILTER]   project the ingest-decode cost over a core population")
