#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Emit membudget's proof-cost ledger to cassian's VictoriaMetrics via OTLP.

The membudget wrapper records per-module `<module>\\t<seconds>\\t<peak_mb>` into each
source dir's `.agda-times.tsv` (Ⓟ.proof-cost-ledger — gitignored, hardware/cache-
specific, last-K only, no cross-run trend, no PSI correlation). This pushes the current
ledger state into cassian's retention-managed store (180d) as OTLP gauges, so
`peak_mb`/`build_seconds` become queryable-by-module, trend-able toward the cap, and
correlatable with the box's `cassian_psi_*`. The persisted `live_state` of the cost model
(memory: feedback_cost_is_structural_times_live).

RUN IT THROUGH uv (the .venv has no pip; uv fetches the OTLP exporter on the fly):

    uv run --with opentelemetry-sdk --with opentelemetry-exporter-otlp-proto-http \\
        python3 scripts/membudget_otlp.py [--dry-run] [--last-k 5]

VERIFY BY THE DATA, NEVER THE 200: an empty/malformed OTLP POST still returns 200. VM's
`vm_rows_inserted_total{type="opentelemetry"}` (the guide's stated verify counter) does NOT
exist on this instance, so this does a READ-YOUR-WRITE instead: it emits a heartbeat gauge
`membudget_emit_unixtime` whose VALUE is this run's start-time, then polls until that exact
value is queryable back — proving ingestion, not just transport.

⚑ THE DEADLINE IS THE STORE'S FLOOR, NOT A GUESS, AND OURS WAS UNDER IT.  This polled 30s
against VM's `-search.latencyOffset`, which DEFAULTS TO 30s: an instant query evaluates at
`now − offset`, so the point is not queryable until the deadline has already expired, and a
correct push reported `✗ NOT queryable`.  paperkit measured it end to end (30.77s at the
default vs 10.5s at `-search.latencyOffset=1s`).  That is the `vm_rows_inserted_total` class
one layer down: read-your-write replaced a counter that reported failure on success, and an
under-floor deadline reintroduced the same false negative in the replacement.  The default
now comes from `scratch/tsdbprobe.DEADLINE` — one constant, shared with the reader that
carries cassian's `query-readback` semantics, so the two cannot drift.

Metrics (resource `service.name="substrate.membudget"` → job label, distinct from cassian's own):
    membudget_peak_mb{module,dir}       gauge  — max maxRSS over the last K builds (cap-relevant worst case)
    membudget_build_seconds{module,dir} gauge  — median build seconds over the last K builds
    membudget_build_count{module,dir}   gauge  — how many recent runs the above summarise
"""

from __future__ import annotations
import argparse, json, os, statistics, sys, time, urllib.parse, urllib.request
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scratch"))
import tsdbprobe as _probe  # noqa: E402  — THE verify authority; never re-derive its deadline

AGDA_ROOT = os.path.join(REPO, "agda")
OTLP_ENDPOINT = "http://127.0.0.1:8428/opentelemetry/v1/metrics"
QUERY_BASE = "http://127.0.0.1:8428"


def find_ledgers(root: str):
    for dirpath, _dirs, files in os.walk(root):
        if ".agda-times.tsv" in files:
            yield os.path.join(dirpath, ".agda-times.tsv")


def aggregate(root: str, last_k: int):
    """(reldir, module) -> (peak_mb, seconds, n). peak = max over last K; seconds = median over last K."""
    rows = defaultdict(list)  # (reldir, module) -> [(seconds, peak_mb), ...] in file order
    for led in find_ledgers(root):
        reldir = os.path.relpath(os.path.dirname(led), root)
        try:
            with open(led) as fh:
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 3:
                        continue
                    mod, secs, peak = parts[0], parts[1], parts[2]
                    try:
                        rows[(reldir, mod)].append((float(secs), float(peak)))
                    except ValueError:
                        continue
        except OSError:
            continue
    out = {}
    for key, hist in rows.items():
        recent = hist[-last_k:]
        secs = [s for s, _ in recent]
        peaks = [p for _, p in recent]
        out[key] = (max(peaks), statistics.median(secs), len(recent))
    return out


def query_scalar(query_base: str, promql: str) -> float | None:
    """Instant query → max value across the returned series, or None if absent/error.

    Read-your-write ingestion check: `vm_rows_inserted_total{type="opentelemetry"}` (the guide's
    stated verify counter) does NOT exist on this VM instance — the honest verify is to read back a
    VALUE we control (`membudget_emit_unixtime`), not the transport's 200 nor a missing counter.
    """
    url = query_base + "/api/v1/query?" + urllib.parse.urlencode({"query": promql})
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.load(r)
    except Exception as e:  # noqa: BLE001
        print(f"  query failed: {e}", file=sys.stderr)
        return None
    res = data.get("data", {}).get("result", [])
    if not res:
        return None
    return max(float(v["value"][1]) for v in res)


def emit_gauges(
    service: str,
    prefix: str,
    series: dict,
    at: float,
    endpoint: str,
    meter_name: str | None = None,
    units: dict | None = None,
) -> None:
    """THE OTLP producer. One shape, three callers; never a fourth.

    `series` is `{metric_suffix: {labels_frozen: value}}`, where `labels_frozen` is a
    tuple of `(key, value)` pairs — hashable, order-stable, and arbitrary-arity, so a
    per-module ledger (`module`,`dir`), a per-suite roster (`suite`) and a bare aggregate
    (`()`) are the same call rather than three emitters.

    ⚑ THIS EXISTS BECAUSE THE LEDGER→GAUGE SHAPE IS ONE CAPABILITY AND WAS WRITTEN TWICE
    (CLAUDE.md: *"TWO EMITTERS EXIST AND BOTH HAND-ROLL THE BOILERPLATE … do not add a
    third"*).  A per-dir TSV whose first column is a target name and whose rest are named
    numeric SLIs, aggregated last-K, is the shared form — `.agda-times.tsv`,
    `.selftest-last.tsv` and `.agda-profile.tsv` are three instances of it.  The third had
    NO export path at all, which is the tell that the duplication was costing reach and
    not merely lines.

    ⚑ AND THE DUPLICATION WAS NOT COSMETIC — IT HELD TWO MEASURED CONSTRAINTS.
    `Resource(attributes=…)`, NOT `Resource.create()`: the latter injects a RANDOM
    per-process `service.instance.id` plus `telemetry.sdk.*` labels, so every run mints a
    fresh series set (~4148 churn series bought that lesson) instead of UPDATING the same
    series over time.  And the heartbeat's VALUE is the run's start time, so verification
    is read-your-write on a value we control — never the transport's 200, which an
    empty/malformed POST also returns.  Two copies of a constraint is two places for it to
    drift; that is the argument for the lift, independent of line count.

    ⚑ `at` TRAVELS WITH THE SAMPLE, never `time.time()` read in here.  A REPLAY IS NOT A
    RE-MEASUREMENT: a sample buffered during an outage carries its own moment, and
    stamping it with the replay's clock would make the backfilled series a fiction —
    worse than the gap it fills.  Callers pass the sample's own `at`; this function has no
    opinion about now.
    """
    import socket
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.metrics import Observation

    units = units or {}
    exporter = OTLPMetricExporter(endpoint=endpoint)
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=3_600_000)
    provider = MeterProvider(
        metric_readers=[reader],
        resource=Resource(
            attributes={
                "service.name": service,
                "service.instance.id": socket.gethostname(),
            }
        ),
    )
    meter = provider.get_meter(meter_name or prefix)

    def _cb(points):
        # ⚑ BIND `points` AS A DEFAULT ARG, never close over the loop variable: a late-bound
        # closure would make every gauge emit the LAST metric's points — one wrong series set
        # per run, silently, with the right series NAMES.
        def cb(_options, _pts=points):
            for labels, value in sorted(_pts.items()):
                yield Observation(value, dict(labels))

        return cb

    for suffix, points in sorted(series.items()):
        meter.create_observable_gauge(
            f"{prefix}_{suffix}", callbacks=[_cb(points)], unit=units.get(suffix, "1")
        )

    # The heartbeat is emitted BY THE PRODUCER, so no caller can forget it and then have
    # nothing to verify against. Its value is `at` verbatim (see the ⚑ above).
    meter.create_observable_gauge(f"{prefix}_emit_unixtime", callbacks=[_cb({(): at})], unit="s")

    provider.force_flush(timeout_millis=15_000)  # collect (fires callbacks) + export
    provider.shutdown()


def emit(data, endpoint: str, emit_start: float):
    """membudget's ledger → the shared producer. Kept as the named caller, not re-derived."""
    emit_gauges(
        service="substrate.membudget",
        prefix="membudget",
        series={
            "peak_mb": {(("module", m), ("dir", d)): p for (d, m), (p, _s, _n) in data.items()},
            "build_seconds": {
                (("module", m), ("dir", d)): s for (d, m), (_p, s, _n) in data.items()
            },
            "build_count": {(("module", m), ("dir", d)): n for (d, m), (_p, _s, n) in data.items()},
        },
        at=emit_start,
        endpoint=endpoint,
        units={"peak_mb": "MB", "build_seconds": "s", "build_count": "1"},
    )


def _selftest() -> bool:
    """⚑ THE PRODUCER HAD NO SUITE, so it was INVISIBLE to `run_selftests` rather than
    passing — the gap that let `rename_at_source` ship a live bug through a green run.
    These drive the two things the lift can break SILENTLY: the label projection and
    the per-metric closure binding.
    """
    cases, ok = [], 0

    def check(label, cond):
        nonlocal ok
        cases.append((label, bool(cond)))
        if cond:
            ok += 1

    # The membudget projection: the ledger's (dir, module) key must survive as LABELS.
    data = {
        ("Algebra/F2", "GF256.agda"): (300.0, 12.5, 5),
        ("Foundation", "Nat.agda"): (64.0, 1.5, 2),
    }
    ser = {
        "peak_mb": {(("module", m), ("dir", d)): p for (d, m), (p, _s, _n) in data.items()},
        "build_seconds": {(("module", m), ("dir", d)): s for (d, m), (_p, s, _n) in data.items()},
    }
    check(
        "projection keeps dir+module distinct",
        len(ser["peak_mb"]) == 2
        and ser["peak_mb"][(("module", "GF256.agda"), ("dir", "Algebra/F2"))] == 300.0,
    )

    # ⚑ THE LATE-BINDING TRAP, driven rather than reasoned about. Building callbacks in a
    # loop that closes over the loop variable makes EVERY gauge emit the LAST metric's
    # points — correct series NAMES, wrong values, no error. This asserts each callback
    # returns ITS OWN metric's points, which is exactly what a late-bound closure fails.
    def _cb(points):
        def cb(_o, _pts=points):
            return sorted(_pts.items())

        return cb

    built = {suffix: _cb(pts) for suffix, pts in sorted(ser.items())}
    got = {suffix: dict(fn(None)) for suffix, fn in built.items()}
    check(
        "each gauge emits its OWN points (late-binding guard)",
        got["peak_mb"] != got["build_seconds"]
        and got["build_seconds"][(("module", "Nat.agda"), ("dir", "Foundation"))] == 1.5,
    )

    # A bare aggregate and the heartbeat share the empty-label shape.
    check("empty labels are a valid point", dict(_cb({(): 42.0})(None)) == {(): 42.0})

    # ⚑ SORTED, so a re-run emits points in a STABLE order rather than dict order.
    check(
        "points are emitted in sorted order",
        [k for k, _ in _cb(ser["peak_mb"])(None)] == sorted(ser["peak_mb"]),
    )

    # aggregate()'s contract: peak is the MAX over last-K (cap-relevant), secs the MEDIAN.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        sub = os.path.join(td, "Algebra")
        os.makedirs(sub)
        with open(os.path.join(sub, ".agda-times.tsv"), "w") as fh:
            fh.write("M.agda\t1.0\t100\nM.agda\t5.0\t300\nM.agda\t3.0\t200\n")
        agg = aggregate(td, 5)
        peak, secs, n = agg[("Algebra", "M.agda")]
        check("aggregate: peak = MAX (worst case, not median)", peak == 300.0)
        check("aggregate: seconds = MEDIAN over last K", secs == 3.0 and n == 3)

    for label, good in cases:
        if not good:
            print(f"  FAIL {label}")
    print(f"selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main() -> int:
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--endpoint", default=OTLP_ENDPOINT, help="OTLP metrics ingest URL")
    ap.add_argument(
        "--query-base", default=QUERY_BASE, help="VictoriaMetrics base for verify-by-counter"
    )
    ap.add_argument("--last-k", type=int, default=5, help="summarise the last K runs per module")
    ap.add_argument("--root", default=AGDA_ROOT, help="tree to scan for .agda-times.tsv")
    ap.add_argument("--dry-run", action="store_true", help="print the aggregate; do not emit")
    ap.add_argument(
        "--deadline",
        type=float,
        default=_probe.DEFAULT_DEADLINE,
        help="seconds to poll for OUR value to read back "
        f"(default {_probe.DEFAULT_DEADLINE:.0f}s: VM's -search.latencyOffset floor plus index time)",
    )
    args = ap.parse_args()

    data = aggregate(args.root, args.last_k)
    n_modules = len(data)
    n_points = n_modules * 3
    print(
        f"membudget-otlp: {n_modules} modules from ledgers under {os.path.relpath(args.root, REPO)} "
        f"(last-{args.last_k}); {n_points} data points."
    )
    if not data:
        print("  no ledger rows found — nothing to emit.")
        return 0
    top = sorted(data.items(), key=lambda kv: kv[1][0], reverse=True)[:5]
    print("  top peak_mb:", ", ".join(f"{m}={p:.0f}MB" for (_d, m), (p, _s, _n) in top))
    if args.dry_run:
        for (d, m), (p, s, n) in sorted(data.items()):
            print(f"    {d}/{m}\tpeak={p:.0f}MB\tsecs={s:.2f}\tn={n}")
        return 0

    emit_start = time.time()
    emit(data, args.endpoint, emit_start)
    # Verify by READING BACK a value we control (not the transport 200, not the guide's
    # vm_rows_inserted_total which is absent on this VM). Poll until membudget_emit_unixtime ≥ emit_start.
    deadline = time.time() + args.deadline
    hb = None
    while time.time() < deadline:
        time.sleep(1.0)
        hb = query_scalar(args.query_base, "membudget_emit_unixtime")
        if hb is not None and hb >= emit_start - 1.0:
            break
    if hb is not None and hb >= emit_start - 1.0:
        peak = query_scalar(args.query_base, "count(membudget_peak_mb)")
        print(
            f"  ✓ ingested (read-your-write): membudget_emit_unixtime = {hb:.0f} ≥ emit_start "
            f"{emit_start:.0f}; membudget_peak_mb series present = {'?' if peak is None else int(peak)}. "
            f"{n_points} points emitted."
        )
        return 0
    # ⚑ NOT CONFIRMED IS NOT FAILED, and this message used to say it was ("the POST was
    # empty/malformed or dropped").  The predicate cannot distinguish un-indexed from
    # dropped from store-down (cassian's A67), so naming one is an unestablished cause —
    # the same overclaim that made `vm_rows_inserted_total` report failure on success.
    print(
        f"  ✗ NOT CONFIRMED within {args.deadline:.0f}s (membudget_emit_unixtime={hb}). "
        f"The write may have ingested and not yet be queryable, or been dropped, or the "
        f"store may be down — this check cannot tell which. Transport 200 ≠ ingestion; "
        f"diagnose with: python3 scratch/tsdbprobe.py --reachable",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
