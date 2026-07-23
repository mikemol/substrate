#!/usr/bin/env python3
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
value is queryable back — proving ingestion, not just transport. The FIRST run creates new
metric NAMES, whose label-index appearance lags the write by up to ~20s (steady-state ~1-2s).

Metrics (resource `service.name="substrate.membudget"` → job label, distinct from cassian's own):
    membudget_peak_mb{module,dir}       gauge  — max maxRSS over the last K builds (cap-relevant worst case)
    membudget_build_seconds{module,dir} gauge  — median build seconds over the last K builds
    membudget_build_count{module,dir}   gauge  — how many recent runs the above summarise
"""
from __future__ import annotations
import argparse, json, os, statistics, sys, time, urllib.parse, urllib.request
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def emit(data, endpoint: str, emit_start: float):
    import socket
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.metrics import Observation

    exporter = OTLPMetricExporter(endpoint=endpoint)
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=3_600_000)
    # ⚑ Resource(attributes=…), NOT Resource.create(): the latter injects a RANDOM
    # `service.instance.id` (UUID per process) + `telemetry.sdk.*` version labels, so every
    # run would mint a fresh series set (cardinality churn). Pin both to STABLE values so a
    # re-run UPDATES the same (module,dir) series over time — proper time-series semantics.
    provider = MeterProvider(
        metric_readers=[reader],
        resource=Resource(attributes={
            "service.name": "substrate.membudget",
            "service.instance.id": socket.gethostname(),
        }),
    )
    meter = provider.get_meter("membudget")

    def gauge_cb(pick):
        def cb(_options):
            for (reldir, mod), (peak, secs, n) in data.items():
                attrs = {"module": mod, "dir": reldir}
                yield Observation(pick(peak, secs, n), attrs)
        return cb

    meter.create_observable_gauge("membudget_peak_mb",
                                  callbacks=[gauge_cb(lambda p, s, n: p)], unit="MB")
    meter.create_observable_gauge("membudget_build_seconds",
                                  callbacks=[gauge_cb(lambda p, s, n: s)], unit="s")
    meter.create_observable_gauge("membudget_build_count",
                                  callbacks=[gauge_cb(lambda p, s, n: n)], unit="1")

    # Heartbeat we control: value == this run's start unix time. Reading it back ≥ emit_start
    # confirms INGESTION (not just the transport 200) — read-your-write on a known value.
    def hb_cb(_options):
        from opentelemetry.metrics import Observation as _Obs
        yield _Obs(emit_start, {})
    meter.create_observable_gauge("membudget_emit_unixtime", callbacks=[hb_cb], unit="s")

    provider.force_flush(timeout_millis=15_000)  # collect (fires callbacks) + export
    provider.shutdown()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--endpoint", default=OTLP_ENDPOINT, help="OTLP metrics ingest URL")
    ap.add_argument("--query-base", default=QUERY_BASE, help="VictoriaMetrics base for verify-by-counter")
    ap.add_argument("--last-k", type=int, default=5, help="summarise the last K runs per module")
    ap.add_argument("--root", default=AGDA_ROOT, help="tree to scan for .agda-times.tsv")
    ap.add_argument("--dry-run", action="store_true", help="print the aggregate; do not emit")
    ap.add_argument("--deadline", type=float, default=30.0, help="seconds to poll for the counter to move")
    args = ap.parse_args()

    data = aggregate(args.root, args.last_k)
    n_modules = len(data)
    n_points = n_modules * 3
    print(f"membudget-otlp: {n_modules} modules from ledgers under {os.path.relpath(args.root, REPO)} "
          f"(last-{args.last_k}); {n_points} data points.")
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
        print(f"  ✓ ingested (read-your-write): membudget_emit_unixtime = {hb:.0f} ≥ emit_start "
              f"{emit_start:.0f}; membudget_peak_mb series present = {'?' if peak is None else int(peak)}. "
              f"{n_points} points emitted.")
        return 0
    print(f"  ✗ NOT queryable within {args.deadline:.0f}s (membudget_emit_unixtime={hb}). "
          f"Transport 200 ≠ ingestion — the POST was empty/malformed or dropped.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
