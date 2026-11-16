---
name: reference-cassian-tsdb-observability
description: "How to query this box's memory/CPU/IO pressure correctly — cassian's VictoriaMetrics/VictoriaLogs TSDB; PSI from the counter-rate, NOT swap or avg10"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-23T20:35:15.293Z
---

This box (cassian) runs a time-series observability stack. When diagnosing build/memory behavior, query IT
with the load-bearing forms below — do NOT eyeball `free`/swap or `/proc/pressure` `avg10`. Full guide:
`scratch/inbox/2026-07-23-cassian-tsdb-query-guide.md` (config-as-code in `~/github/cassian-observability`).

**Endpoints (loopback only):** VictoriaMetrics `http://127.0.0.1:8428` (Prometheus API `/api/v1/query`,
`/api/v1/query_range` + MetricsQL); VictoriaLogs `http://127.0.0.1:9428/select/logsql/query` (LogsQL). All
series prefixed `cassian_`, filter `{job="cassian"}` for the clean generation.

**THE LOAD-BEARING PSI FORM** (fraction of a window I choose that was stalled, from the COUNTER —
scrape-invariant): `100 * rate(cassian_psi_total_usec{res=…,kind="some",job="cassian"}[5m]) / 1e6`.
`res` ∈ cpu|memory|io; `kind` ∈ some(≥1 task stalled)|full(all stalled). `cassian_psi_avg10{res,kind}` is
the decayed gauge — fine for a "right now" glance, NEVER for load-bearing math or aggregation over time.

**Instrument discriminations (each a correction to a real misread of mine):**
- **Swap is NOT a distress signal here.** zram+zswap keep swap COMPRESSED IN RAM; high swap usage (e.g. 19GB)
  is normal. Read PSI-memory, not `free`'s swap column. (`rate(cassian_vmstat_pswpout[5m])` = pages/s if
  wanted; `cassian_zswap_reject_*` nonzero RATE = swap-stack regime change worth reporting — normally 0.)
- **There is no separate "disk PSI" — `res="io"` IS the disk-pressure signal.** `io kind="full"` = everything
  blocked on I/O = real disk thrash. Near-0 io-PSI + high swap = zswap absorbing it in RAM, no disk pain.
- **OOM notices with `constraint=CONSTRAINT_MEMCG` / `oom_memcg=…/run-p*.scope` are CGROUP kills** (a
  membudget lease hitting its `MemoryMax`) — self-healing (membudget doubles the lease and retries), NOT
  system-wide OOM. `curl .../select/logsql/query -d 'query=_time:1h oom' -d 'limit=200'` to enumerate.
- **Logs: enumerate units first, and user-scopes are queryable by name as of 2026-07-23.** `query=_time:6h *
  | uniq by (unit) limit 50` lists what exists; user-session units (membudget/agda scopes) now map via
  `_SYSTEMD_USER_UNIT` — but entries ingested BEFORE 2026-07-23 carry user-unit logs under their syslog
  identifier, so free-text (`oom`) is the robust cross-generation query for old events. Labels: `unit`/`priority`/`pid`.
- **NO filesystem capacity series (df-style bytes-free) is exported** — "disk"/`res="io"` is PRESSURE, not
  capacity. Don't hunt a df metric; it's a request-channel add if ever needed. Also absent: per-process, traces.
- Box baseline: ~7.4% CPU-stalled, ~0.2% memory-stalled lifetime — **CPU is the contended resource by
  design**; a build showing high cpu-PSI + low memory-PSI is healthy, not distressed.

**OTLP PUSH surface — BUILT (substrate is the first producer).** Metrics → `POST
:8428/opentelemetry/v1/metrics`, logs → `POST :9428/insert/opentelemetry/v1/logs` (protobuf, JSON 400s; the
.venv has no pip — run the exporter via `uv`, see [[reference-uv-runs-python-with-deps]]).
`scripts/membudget_otlp.py` emits the per-module proof-cost ledger (`membudget_peak_mb`/`build_seconds`/
`build_count`, resource `service.name="substrate.membudget"`) — the PERSISTED `live_state` of
[[feedback_cost_is_structural_times_live]], 180d, queryable by module, PSI-correlatable. Two hard-won rules:
- ⚑ **VERIFY BY READ-YOUR-WRITE, not by a counter.** `vm_rows_inserted_total{type="opentelemetry"}` is a
  `/metrics` EXPOSITION counter VM does NOT self-scrape into the queryable TSDB — it reads ~62k on `:8428/metrics`
  but **0 via `/api/v1/query`**, so a real producer (which queries) correctly sees it absent. The verify (now the
  cassian guide's official one, credited to this work) is: emit a heartbeat gauge whose VALUE = the run's
  start-time, poll `/api/v1/query` until that value reads back. Endpoint-agnostic AND immune to shared-counter
  masking (cassian's own `cassian_gate_*_seconds` build-telemetry shares the store; a global-counter delta would
  be inflated by a concurrent push). Transport 200 ≠ ingestion.
- ⚑ **Pin `service.instance.id`** (I use the hostname) and use `Resource(attributes={…})` NOT `Resource.create()`
  — the SDK mints a random UUID + `telemetry.sdk.*` version labels per process → a fresh series set every run
  (cardinality churn). First-run label-index lag for a NEW metric name is ~20s (steady-state ~1-2s); size the poll deadline for it.

**Why this is load-bearing:** I killed a healthy cold build reading 19GB swap as "thrash" when memory-PSI
peaked at 2.9%, io-PSI ≈ 0, zswap-rejects = 0 — the box was fine, just CPU-bound. Query the TSDB, read PSI
from the counter, before concluding memory distress. Widens [[reread-meters-toctou]] and the
measure-the-instrument discipline. Read-your-write caveat: after a WRITE, poll with a deadline (~1s to
queryable); a transport 200 ≠ ingestion (verify `vm_rows_inserted_total`/`vl_rows_ingested_total`).
