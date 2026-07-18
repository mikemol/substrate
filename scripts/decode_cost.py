#!/usr/bin/env python3
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
LEDGER = os.environ.get("DECODE_COST_LEDGER", os.path.join(_HERE, ".decode-cost.tsv"))  # gitignored; hw-specific
NPROC = os.cpu_count() or 1
K = 5                       # median of last-K per core (buildtime shape; robust to the cold/warm bimodality)
T_LAUNCH = 0.030            # s — fixed shim-spawn + fixed decode overhead (the measured intercept)
RATE = 0.62e-6             # s/byte — the measured per-byte work slope


def load_hist():
    """{core_id: [(bytes, seconds, load), … last-K]} — the state-stamped decode-cost ledger (best-effort)."""
    hist = {}
    try:
        with open(LEDGER) as f:
            for line in f:
                cid, b, s, ld = line.rstrip("\n").split("\t")
                hist.setdefault(cid, []).append((int(b), float(s), float(ld)))
    except (FileNotFoundError, ValueError):
        pass
    except Exception:
        pass
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
    work = sum(estimate(c, sizes.get(c, 0), hist) for c in window)   # intrinsic serial work (this epoch)
    ls = live["live_state"]
    p_star = max(1, min(live["P_effective"], len(window)))
    cost_serial = work * ls                                          # P=1: full serial work × contention
    cost_parallel = (work / p_star) * ls                            # pool of P*: launch+work both parallelize
    parallel = p_star > 1 and cost_parallel < cost_serial
    return {**live, "n": len(window), "work": work, "P_star": p_star if parallel else 1,
            "parallel": parallel, "cost_serial": cost_serial, "cost_parallel": cost_parallel}


if __name__ == "__main__":
    import sys, tempfile
    if "--selftest" in sys.argv:
        d = tempfile.mkdtemp(); os.environ["DECODE_COST_LEDGER"] = os.path.join(d, "c.tsv")
        globals()["LEDGER"] = os.environ["DECODE_COST_LEDGER"]
        ok = []
        # unseen core → structural fallback estimate
        h = load_hist()
        e = estimate("cX", 100000, h)
        ok.append(("fallback estimate = t_launch+rate·bytes", abs(e - (T_LAUNCH + RATE*100000)) < 1e-9))
        # record → ledger → median-of-K estimate
        for s in (0.05, 0.06, 0.055, 0.05, 0.07, 0.052):
            record("cA", 100000, s, 1.0)
        h = load_hist()
        ok.append(("ledger keeps last-K", len(h["cA"]) == K))
        ok.append(("estimate = median-of-K", abs(estimate("cA", 100000, h) - statistics.median([0.06,0.055,0.05,0.07,0.052])) < 1e-9))
        # package: idle epoch (P_eff=nproc) → parallel for a multi-core window; serial for 1 core
        idle = {"load1": 0.0, "P_effective": NPROC, "live_state": 1.0, "nproc": NPROC}
        pk = package(["a","b","c","d"], {"a":1e5,"b":1e5,"c":1e5,"d":1e5}, {}, live=idle)
        ok.append(("idle multi-core → parallel", pk["parallel"] and pk["P_star"] == min(NPROC,4)))
        pk1 = package(["a"], {"a":1e5}, {}, live=idle)
        ok.append(("single core → serial", not pk1["parallel"] and pk1["P_star"] == 1))
        # package: fully-loaded epoch (P_eff=1) → serial even for a big window (contention-adaptive)
        busy = {"load1": float(NPROC), "P_effective": 1, "live_state": float(NPROC), "nproc": NPROC}
        pkb = package(["a","b","c","d"], {"a":1e5,"b":1e5,"c":1e5,"d":1e5}, {}, live=busy)
        ok.append(("loaded box → serial (P_eff=1)", not pkb["parallel"] and pkb["P_star"] == 1))
        # dominance is an OUTPUT: cost_parallel < cost_serial exactly when parallel chosen
        ok.append(("dominance output consistent", (pk["cost_parallel"] < pk["cost_serial"]) == pk["parallel"]))
        for name, p in ok:
            print(f"  [{'PASS' if p else 'FAIL'}] {name}")
        print("ALL PASS" if all(p for _, p in ok) else "SOME FAILED")
        sys.exit(0 if all(p for _, p in ok) else 1)
    print(f"decode_cost: nproc={NPROC} ledger={LEDGER}")
    print(f"  live_state now: {poll_live_state()}")
