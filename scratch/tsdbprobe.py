#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Structural questions about an HTTP/OTLP METRICS SURFACE — cassian's VictoriaMetrics.

⚑ WHY THIS IS A NEW TOOL AND NOT A MODE.  The struct-tools rule routes a missing
capability to the tool that already parses the artifact, and adds a TOOL only for an
artifact kind with no reader at all.  Agda, Python, markdown and BibTeX each have one;
a live metrics endpoint has none.  Every question this repo has asked of cassian's
store — is it up, what series exist, what does this query return, did my write land —
was answered by hand-assembled `curl | grep`, which is the shape the rule forbids:

  * "is the store reachable?" → `curl -s -o /dev/null -w %{http_code} .../health`
  * "what series exist?"      → `curl .../api/v1/series --data-urlencode ... | jq`
  * "did my push ingest?"     → the `vm_rows_inserted_total` MISTAKE (see VERIFY below)

Those are structural queries over a JSON-typed API, and assembling them at a shell is
exactly where the third of those went wrong for two projects at once.

⚑ THE PRECONDITION, AND IT DIFFERS FROM EVERY OTHER TOOL HERE.  `pycodemod` and
`mdstruct` read FILES: same input, same answer, forever.  This tool reads a LIVE
SERVICE, so its answers are timestamped observations and an empty result has three
causes it must never conflate — not written, written but not yet queryable, or the
store is down.  Cassian's guide is explicit that these are different
(scratch/inbox/2026-07-23-cassian-tsdb-query-guide.md:196-198: "do not conclude
absence from one immediate read"), so every mode here reports WHICH it means and
never collapses "absent" into "failed".

⚑ VERIFY IS NOT REIMPLEMENTED — IT IS CASSIAN'S SEMANTICS, ADOPTED.  cassian ships
`scripts/collectors/query-readback` (A98) and its docstring is the authority: the
shared `vm_rows_inserted_total` counter is the WRONG oracle twice over — it lives only
on the `:8428/metrics` exposition page (so `/api/v1/query` returns empty, which cost
substrate a false "ingestion failed") and it is GLOBAL across producers (so a
concurrent push false-passes your delta).  The right oracle is read-your-write on a
value you control: a heartbeat gauge whose VALUE is the run's start-unix-time, polled
until that exact value queries back.  Three properties of that script are load-bearing
and are carried here rather than re-derived:

  1. float-tolerant compare (`abs(got-expected) < 0.5`), never a string `==` — VM may
     render an integer as "1753300000", "…0" or "1.7533e+09" and all three must match;
  2. a fetch error is a RETRY, not a verdict — the index is being built under you;
  3. on timeout it says "NOT confirmed", never "ingestion failed" — the predicate
     cannot distinguish un-indexed from dropped from store-down (cassian's A67).

The deadline default is 45s — a CEILING on waiting, not a prediction of how long a
verify takes.  A too-generous ceiling costs nothing when the read succeeds early;
a too-tight one reports a successful write as unconfirmed.

⚑ AND THE MECHANISM THIS USED TO CITE WAS WRONG IN TWO WAYS, corrected by
cassian-observability 2026-08-04 (their A109) after they measured their own store:

  * the floor is VM's `-search.latencyOffset` — TRUE, but it is **not 30s here**.
    cassian pinned it to 1.5x their ingest-buffer flush interval (**7.5s**), so a
    default query now shades only data that may still be in the flush buffer.
  * the "residual ~10-20s of first-run name-index creation" was **the same
    misdiagnosis, not a second effect**.  There is no index-lag term; it was
    `latencyOffset` observed twice and attributed to two causes.

⚑ THE DEEPER CORRECTION, and it changes what a caller may assume: the offset shades
the FRESH EDGE OF A DEFAULT QUERY.  It does not delay the datum, and it does not
rewrite its timestamp — cassian verified a point stamped two minutes in the past
stored and read back at exactly that stamp.  Every returned point is an
`(observation_timestamp, value)` pair, so a consumer computing rates does so against
the observation time and gets an honest answer.  An explicit `time=` / `query_range`
/ `export` reads the fresh edge immediately.

So: an empty read is still a RETRY rather than a verdict (the offset is real), but
the number is a moving operational parameter on someone else's store, not a constant
of VM.  Do not re-derive a deadline from it.

    tsdbprobe.py --reachable [--base URL]      # is the store up — health, and WHICH failure
    tsdbprobe.py --series <selector>           # what series exist matching a selector
    tsdbprobe.py --names [substr]              # what metric NAMES exist (the label index)
    tsdbprobe.py --query <promql>              # what does this query return, as rows
    tsdbprobe.py --labels <series-selector>    # the label VALUES a selector's series carry
    tsdbprobe.py --verify <selector> <value>   # read-your-write: poll until OUR value returns
    tsdbprobe.py --producers                   # which known producers are live, by heartbeat

Stdlib only, like the collector it adopts — this must be runnable from a hook with no
venv.  `--base` defaults to cassian's loopback `:8428`; off-host, tunnel first
(`ssh -L 8428:127.0.0.1:8428 cassian`) — both engines bind loopback deliberately.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# cassian's metrics engine, loopback-only by deliberate configuration
# (guide: "Both bind loopback only, deliberately").
DEFAULT_BASE = "http://127.0.0.1:8428"

# ⚑ THE VERIFY DEADLINE IS A MEASURED FLOOR, NOT A ROUND NUMBER.  See the module
# docstring: VM's -search.latencyOffset (30s default) means a fresh sample is NOT
# queryable until the offset passes, EVERY time — not just first run.  45s clears
# that plus first-run name-index creation.
DEFAULT_DEADLINE = 45.0
DEFAULT_POLL = 1.5

# The heartbeat convention both live producers adopted after cassian's correction:
# a gauge named <prefix>_emit_unixtime whose VALUE is the run's start-unix-time.
# Listed, not hardcoded into logic — `--producers` reports presence per name.
KNOWN_PRODUCERS = (
    ("substrate.membudget", "membudget_emit_unixtime"),
    ("paperkit", "paperkit_emit_unixtime"),
    ("cassian", "cassian_emit_unixtime"),
)


class Unreachable(Exception):
    """The store did not answer at all — distinct from answering 'no data'.

    ⚑ THIS DISTINCTION IS THE TOOL'S REASON FOR EXISTING.  Collapsing it is the
    documented false-"ingestion failed": substrate's first emitter read an empty
    result and reported a failure while the data had in fact ingested
    (cassian-observability/inbox/2026-07-23-substrate-membudget-otlp-producer-report.md:34).
    An exception for 'no answer' and an empty list for 'answered, nothing matched'
    keeps the two un-conflatable by construction rather than by discipline.
    """


def _get(base: str, path: str, params: dict | None = None, timeout: float = 8.0):
    """GET a VM JSON endpoint → the decoded body. Raises Unreachable on no-answer.

    ⚑ A NON-200 IS ALSO AN ANSWER, and its body usually says why (a bad selector
    returns 422 with the parse error).  Surfacing that beats a bare 'failed': the
    error text is the actionable half.
    """
    url = base.rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")[:300]
        except Exception:  # noqa: BLE001
            detail = ""
        raise Unreachable(f"HTTP {e.code} from {path}: {detail}") from e
    except Exception as e:  # noqa: BLE001 — connection refused, DNS, timeout
        raise Unreachable(f"{type(e).__name__}: {e}") from e


def export_samples(base, selector, since=None, timeout=30.0):
    """[(labels, [(ts_ms, value)])] — the RAW STORED SAMPLES for a selector, via `/api/v1/export`.

    ⚑⚑⚑ THE STORE'S OWNER SHIPS THIS CAPABILITY AND THEIRS IS THE ONE TO CALL:
    `~/github/cassian-observability/scripts/collectors/series-history` (41d7c64, registered A128 /
    charter S23). Both were built the same afternoon from the same ruling, and RUN AGAINST THE SAME
    SELECTOR THEY AGREE EXACTLY — 316 samples, 10 change points, same arrival, same 44 → 41. That
    agreement is the argument for one of them ceasing to exist, not for keeping both: a range
    reader that quietly diverges from another range reader is the defect neither author would
    notice alone.

    ⚑⚑ KEPT FOR NOW BECAUSE IT IS THE READER THIS REPO'S HOOKS CAN CALL — stdlib-only, in-tree, no
    cross-repo path — and because the comparison already paid for itself in the OTHER direction:
    two properties of this implementation were missing from theirs and are now folded in (an
    ARRIVAL reported as a change from `None`, so *"began at 44"* is distinguishable from *"always
    was 44"*; and a `steady V over N sample(s)` line, so held-steady is distinguishable from
    never-written). Both are the absent-vs-empty collapse their own API guidance refuses.

    ⚑ SO THIS IS A CONVERGENCE CANDIDATE, RECORDED AS ONE RATHER THAN LEFT AS A SILENT SECOND
    SPELLING. The honest next move is this mode calling their collector, or their collector
    absorbing `--changes`; the reasoning below survives either, because it is their ruling and it
    is credited as such. What must NOT happen is the two drifting apart unremarked.

    ⚑⚑⚑ EXPORT, NOT `query_range`, AND THE CHOICE IS THE WHOLE POINT — cassian's ruling
    (2026-08-17), asked as a general capability question and answered generally:

        *"For an event-driven (irregularly-written) series, query_range's step will manufacture
        gaps that are an artifact of your write pattern, not the data — a step chosen for a
        regular scrape stamps 'no data' on every bucket you didn't happen to write in."*

    Their rule, with the fork stated: **query_range for regularly-sampled series you want
    bucketed; export for irregular/event-driven series, or when you need exact transition
    timestamps.** This repo's selftest gauges are written once per suite RUN — several times an
    hour under active work, nothing overnight — so both halves of that fork point here: the
    write pattern is event-driven AND the question is *when did this number change*.

    ⚑⚑ THERE IS NO SAFE STEP FOR AN IRREGULAR SERIES, which is why this is not a `--range` mode
    with a tuned default. Step must be >= 2x the write cadence or two changes alias into one
    bucket; an event-driven series has no cadence to size against, so any step is wrong somewhere
    in the window. Export sidesteps the parameter rather than picking a value for it.

    ⚑ AND THE FRESH EDGE IS HONEST HERE. `-search.latencyOffset=7.5s` shifts only the DEFAULT
    instant-query eval time — it does not rewrite stored timestamps, so an explicit export reads
    the edge with the producer's own stamps and needs no offset compensation. That is why bare
    `--query` reads returned 0 series while the data was present all along.

    ⚑ THE RESPONSE IS JSONL, ONE OBJECT PER SERIES — NOT the `{data:{result:[…]}}` shape
    `extract_values` parses. Reusing that parser here returns [] on every line and would report
    an empty history for a populated store: an absence manufactured by reading the right store
    with the wrong parser.
    """
    q = {"match[]": selector}
    if since is not None:
        q["start"] = "%d" % int(since)
    url = base.rstrip("/") + "/api/v1/export?" + urllib.parse.urlencode(q, doseq=True)
    out = []
    with urllib.request.urlopen(url, timeout=timeout) as fh:
        raw = fh.read().decode("utf-8", "replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        pairs = sorted(zip(obj.get("timestamps") or [], obj.get("values") or []))
        out.append((obj.get("metric") or {}, pairs))
    return out


# --- the pure half (parsers), so the tool self-proves without a live store ----------

def transitions(pairs):
    """[(ts_ms, before, after)] — only the points where the VALUE CHANGED. PURE.

    ⚑ THE SERIES IS MOSTLY REPETITION AND THE REPETITION IS NOISE. A suite holding 220 across
    three hundred samples answers "when did this move" with three numbers, not three hundred;
    printing every sample is the raw-dump shape that makes a reader scan instead of read.
    The first sample is reported as a transition from `None` — its arrival IS the first fact,
    and collapsing it into "no change" would hide when a series began.
    """
    out, prev = [], None
    for ts, v in pairs:
        if prev is None or v != prev:
            out.append((ts, prev, v))
        prev = v
    return out


def extract_values(body) -> list[float]:
    """PURE: the sample VALUES out of a Prometheus /api/v1/query response.

    ⚑ [] ON GARBAGE, NEVER AN EXCEPTION AND NEVER A FALSE VALUE.  This is the
    read-your-write oracle's parse, so a malformed response must be incapable of
    verifying a token.  Both live producers landed on exactly this shape
    (paperkit/tools/otlp_push.py:217 `_extract_values`); it is carried, not re-derived.

    Handles BOTH result types VM returns: `vector` (value: [ts, "v"]) and `matrix`
    (values: [[ts,"v"], …]) — a range query's samples are otherwise invisible.
    """
    if isinstance(body, (str, bytes)):
        try:
            body = json.loads(body)
        except (ValueError, TypeError):
            return []
    if not isinstance(body, dict):
        return []
    # ⚑ `data` IS A LIST ON /series AND /label/<n>/values, A DICT ON /query.  A bare
    # `.get("data", {}).get(...)` raises AttributeError on the list shape — caught by
    # this module's own "a /series response is NOT read as /query" case, which is why
    # the shape check is here rather than in the caller.
    data = body.get("data")
    if not isinstance(data, dict):
        return []
    out = []
    for series in data.get("result") or []:
        if not isinstance(series, dict):
            continue
        v = series.get("value")
        if isinstance(v, list) and len(v) == 2:
            try:
                out.append(float(v[1]))
            except (ValueError, TypeError):
                pass
        for pair in series.get("values") or []:
            if isinstance(pair, list) and len(pair) == 2:
                try:
                    out.append(float(pair[1]))
                except (ValueError, TypeError):
                    pass
    return out


def extract_rows(body) -> list[tuple[str, dict, float | None]]:
    """PURE: (metric_name, labels, latest_value) per returned series.

    The `--query` mode's presentation: a query answer is a SET OF LABELLED SERIES,
    and printing only the numbers loses which series each came from — the exact
    loss that made the guide's doubled-generation gotcha invisible until a job
    filter was added (guide:69-71).
    """
    if isinstance(body, (str, bytes)):
        try:
            body = json.loads(body)
        except (ValueError, TypeError):
            return []
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    if not isinstance(data, dict):
        return []
    rows = []
    for series in data.get("result") or []:
        if not isinstance(series, dict):
            continue
        labels = dict(series.get("metric") or {})
        name = labels.pop("__name__", "")
        vals = extract_values({"data": {"result": [series]}})
        rows.append((name, labels, vals[-1] if vals else None))
    return rows


def extract_series(body) -> list[dict]:
    """PURE: the label-sets from /api/v1/series (which returns `data` as a LIST).

    ⚑ A DIFFERENT SHAPE FROM /api/v1/query, and that is the bug this prevents.
    `/query` nests under data.result; `/series` and `/label/<n>/values` put a bare
    list at `data`.  One extractor over both would silently return [] for one of
    them — reporting 'no series' for a store full of them.
    """
    if isinstance(body, (str, bytes)):
        try:
            body = json.loads(body)
        except (ValueError, TypeError):
            return []
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict)]


def extract_names(body) -> list[str]:
    """PURE: the string list from /api/v1/label/__name__/values."""
    if isinstance(body, (str, bytes)):
        try:
            body = json.loads(body)
        except (ValueError, TypeError):
            return []
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, str)]


def matches(values: list[float], expected: float, tol: float = 0.5) -> bool:
    """PURE: does any returned sample equal our token, float-tolerantly?

    ⚑ TOLERANT COMPARE, NOT `==`, AND THE REASON IS RECORDED UPSTREAM.  cassian's
    query-readback:22-24: emit INTEGER unix seconds (exact in float64) and compare
    abs-diff < 0.5, "never a raw string ==, so any VM string form ('1753300000',
    '...0', '1.7533e+09') matches".  A string compare here fails a verify whose data
    landed perfectly — a false negative on the ONE question the mode exists to answer.
    """
    return any(abs(v - expected) < tol for v in values)


# --- the live half -----------------------------------------------------------------

def reachable(base: str) -> tuple[bool, str]:
    """(ok, detail) — is the store answering, and if not, HOW does it fail?

    ⚑ 'DOWN' AND 'UP BUT REFUSING THIS QUERY' ARE DIFFERENT REPAIRS.  A bare
    boolean sends you to systemctl when the real fault is a 422 selector or a
    missing SSH tunnel, so the failure MODE is part of the answer.
    """
    try:
        _get(base, "/health", timeout=5.0)
        return True, "health ok"
    except Unreachable as e:
        # /health returns a bare "OK" body, not JSON — a decode failure there still
        # proves the socket answered, so fall back to a query that must parse.
        try:
            _get(base, "/api/v1/query", {"query": "1"}, timeout=5.0)
            return True, "query API ok (/health returned non-JSON, which is normal)"
        except Unreachable as e2:
            return False, f"{e2}"


def query(base: str, promql: str):
    return _get(base, "/api/v1/query", {"query": promql})


def series(base: str, selector: str):
    return _get(base, "/api/v1/series", {"match[]": selector})


def names(base: str):
    return _get(base, "/api/v1/label/__name__/values")


def label_values(base: str, label: str, selector: str | None = None):
    params = {}
    if selector:
        params["match[]"] = selector
    return _get(base, f"/api/v1/label/{urllib.parse.quote(label)}/values", params or None)


def verify(base: str, selector: str, expected: float, deadline_s: float = DEFAULT_DEADLINE,
           poll_s: float = DEFAULT_POLL, sink=None) -> int:
    """Read-your-write. 0 = our value queried back; 1 = NOT confirmed; never 'failed'.

    Adopted wholesale from cassian's `scripts/collectors/query-readback` (A98) — the
    semantics are theirs, credited, not re-derived.  The three properties that matter,
    each of which a naive rewrite gets wrong:

      * a fetch EXCEPTION is a retry, not a verdict (the store may be settling);
      * an empty vector is a retry, not an absence;
      * timeout reports NOT CONFIRMED with the last-seen state — un-indexed, dropped
        and store-down are indistinguishable to this predicate, so it must not pick one.

    ⚑⚑⚑ READS VIA `/api/v1/export`, NOT THE INSTANT QUERY — and the reason was written in
    THIS FILE, one function away, while this one kept polling the shaded path.
    `export_samples`' ⚑ block states it outright: *"an explicit export reads the edge with
    the producer's own stamps and needs no offset compensation. That is why bare `--query`
    reads returned 0 series while the data was present all along."*

    An instant query is evaluated at `now - latencyOffset`, so a point written moments ago
    is BEHIND the default eval time and reads as absent. For read-your-write — where the
    write is by construction as fresh as possible — that is the worst case: this function
    burned a full offset of retries on every successful emit and called it settling. The
    timeout message even said *"an explicit time= or query_range reads the fresh edge
    directly"*, so the knowledge was here and the code did not act on it.

    ⚑ THE RETRY LOOP STAYS, and shrinking it would be the wrong lesson. Export removes the
    OFFSET as a cause of an empty read; it does not make ingestion instantaneous, and the
    three causes of an empty result are still indistinguishable. What changes is that a
    retry now means something happened, rather than being scheduled by someone else's knob.

    ⚑ NUMBERS ARE NOT DERIVED FROM, ONLY RECORDED: cassian measured their running config
    2026-08-22 — `-inmemoryDataFlushInterval=5s`, `-search.latencyOffset=7.5s` (still 1.5x
    the flush), `-retentionPeriod=90d`. Those are THEIR operational parameters, quoted as a
    dated observation and used by no code path here. This file's standing rule is to name
    the mechanism, not the magnitude — it once froze VM's stock 30s and that aged into a
    false claim about their box.
    """
    say = (sink if sink is not None else sys.stderr).write
    end = time.monotonic() + deadline_s
    last = "no read has succeeded yet"
    while True:
        try:
            # ⚑ EXPORT RETURNS (labels, [(ts, value)]) PER SERIES, not the instant query's
            # single vector — take every sample's value, since our heartbeat's whole point
            # is that ONE of them equals the value we chose.
            vals = [v for _labels, pairs in export_samples(base, selector)
                    for _ts, v in pairs]
            if matches(vals, expected):
                say(f"tsdbprobe: CONFIRMED — {selector} returned our value "
                    f"{expected:.0f} (read-your-write)\n")
                return 0
            last = (f"got {vals!r}, not our {expected:.0f}" if vals
                    else "no stored samples for that selector yet")
        except Unreachable as e:
            last = f"unreachable: {e}"
        except Exception as e:                                    # noqa: BLE001
            # ⚑ AN EXPORT PARSE/TRANSPORT ERROR IS A RETRY TOO. `export_samples` raises
            # through `urlopen` rather than the `Unreachable` this loop was written around,
            # so catching only that would turn a transient read into an unhandled crash —
            # converting a retryable condition into a hard failure, which is the inverse of
            # this function's whole contract.
            last = f"read error: {e}"
        if time.monotonic() >= end:
            # ⚑ DO NOT QUOTE A NUMBER FOR SOMEONE ELSE'S OPERATIONAL PARAMETER.
            # This said "~30s default" — VM's stock value, which cassian has since
            # pinned to 7.5s (A109).  A figure baked into OUR error message ages
            # into a false claim about THEIR store the moment they tune it, and an
            # operator reading it would size a deadline against a constant that is
            # not one.  Name the mechanism, not the magnitude.
            # ⚑ AND THE OFFSET IS NO LONGER A CAUSE HERE — this reads via `/api/v1/export`,
            # which returns raw stored samples with the producer's own stamps and is not
            # shaded. So an empty read now means the sample is genuinely not stored yet,
            # was dropped, or the store is down — still three causes, but the fourth
            # (queryable-but-shaded) has been removed rather than waited out.
            say(f"tsdbprobe: NOT CONFIRMED within {deadline_s:.0f}s — {last}. "
                f"This does NOT mean ingestion failed: not-yet-stored, dropped and "
                f"store-down are indistinguishable here. Read via /api/v1/export, so "
                f"-search.latencyOffset is NOT a factor — diagnose with --reachable.\n")
            return 1
        time.sleep(poll_s)


def _pb_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _pb_field(num: int, wire: int, payload: bytes) -> bytes:
    """One protobuf field: tag varint, then payload (len-prefixed for wire type 2)."""
    tag = _pb_varint((num << 3) | wire)
    return tag + (_pb_varint(len(payload)) + payload if wire == 2 else payload)


def _pb_str(num: int, s: str) -> bytes:
    return _pb_field(num, 2, s.encode())


def otlp_gauge_payload(metric: str, value: float, at_unix: float,
                       service: str, instance: str) -> bytes:
    """A minimal OTLP/protobuf `ExportMetricsServiceRequest` — ONE double gauge.

    ⚑ THE OTLP INTEGRATION WAS BUILT NOT TO NEED THE SDK, AND `--ping` REINTRODUCED IT
    (user, 2026-08-03).  I reached for `emit_gauges` because it is "the one producer" and
    thereby made the LIVENESS CHECK require the heaviest dependency in the stack — so the
    probe could not answer "is the store reachable" on a bare interpreter, which is
    precisely when the question is asked.  `spool` is stdlib+sqlite3 for the same reason.

    This is ~40 lines of `struct`-free varint encoding against a FIXED message shape, not
    a reimplementation of the SDK: the SDK's value is batching, retry, views and
    instrumentation, none of which a one-shot ping wants.  The bulk producers keep using
    it; this is the dependency-free floor.

    Message shape (opentelemetry.proto.collector.metrics.v1):
      ExportMetricsServiceRequest{1: ResourceMetrics}
        ResourceMetrics{1: Resource{1: KeyValue*}, 2: ScopeMetrics}
          ScopeMetrics{2: Metric}
            Metric{1: name, 5: Gauge{1: NumberDataPoint}}
              NumberDataPoint{3: time_unix_nano fixed64, 4: as_double}
    """
    import struct

    def kv(k: str, v: str) -> bytes:
        # KeyValue{1: key, 2: AnyValue{1: string_value}}
        return _pb_str(1, k) + _pb_field(2, 2, _pb_str(1, v))

    resource = _pb_field(1, 2, kv("service.name", service)) + \
        _pb_field(1, 2, kv("service.instance.id", instance))
    # NumberDataPoint: time_unix_nano (3, fixed64) + as_double (4, fixed64 double)
    ndp = _pb_field(3, 1, struct.pack("<Q", int(at_unix * 1e9))) + \
        _pb_field(4, 1, struct.pack("<d", float(value)))
    gauge = _pb_field(1, 2, ndp)
    metric_msg = _pb_str(1, metric) + _pb_field(5, 2, gauge)
    scope_metrics = _pb_field(2, 2, metric_msg)
    resource_metrics = _pb_field(1, 2, resource) + _pb_field(2, 2, scope_metrics)
    return _pb_field(1, 2, resource_metrics)


def ping(base: str, at_unix: float, metric: str = "tsdbprobe_emit_unixtime",
         service: str = "substrate.tsdbprobe") -> tuple[bool, str]:
    """WRITE a value we choose. (ok, detail) — the write half of write-then-read.

    ⚑ A HEARTBEAT IS CAUSED, NOT OBSERVED (user: *"Want a heartbeat? ping; write then
    read."*).  Reporting the transport outcome SEPARATELY from the read-back is the
    point: a failed POST is a transport fault, a successful POST with no read-back is
    an ingest-or-index question, and only the pair distinguishes them.
    """
    import socket
    url = base.rstrip("/") + "/opentelemetry/v1/metrics"
    body = otlp_gauge_payload(metric, at_unix, at_unix, service, socket.gethostname())
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/x-protobuf"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.getcode()
    except Exception as e:                                        # noqa: BLE001
        return False, f"POST failed: {e}"
    # ⚑ A 200 IS NOT INGESTION — it is the ONLY thing this half can report, which is
    # exactly why the read-back half exists. Never return "ok" meaning "landed".
    return True, f"POST {code} (transport only; ingestion unproven until read-back)"


def producers(base: str):
    """[(service, metric, value_or_None, exists)] — has each producer EVER emitted, and when.

    ⚑ THE HEARTBEAT IS A WRITE-THEN-READ TOKEN, NOT A LIVENESS GAUGE, AND REPORTING IT
    AS ONE MISLED EVERY READER INCLUDING ITS AUTHOR (user, 2026-08-03: *"given how many
    times that 'NO HEARTBEAT' has been misinterpreted, there's some fault"* — the fault
    is HERE, not in the reader).  A producer is a script someone runs, not a daemon: it
    emits `<prefix>_emit_unixtime` once, verifies the read-back within seconds, and then
    the point ages out of instant-query range.  **Between runs, absent is the CORRECT
    state.**

    ⚑ THE OLD CODE QUERIED ONLY THE INSTANT, so a lapsed heartbeat came back as `None`
    and printed `NO HEARTBEAT` — alarm language for the expected condition.  MEASURED:
    it reported `0 of 3 known producer(s) have emitted` minutes after all three services
    had emitted and been CONFIRMED by read-back, while `proofcost_alloc_mb` was returning
    live data.  Its own docstring claimed "its age is the staleness" — unmeasurable when
    the value is gone.

    The fix is to ask the two questions separately: `--series` answers HAS THIS EVER
    EMITTED (the series exists), the instant query answers IS A RUN IN FLIGHT RIGHT NOW.
    A producer with a series and no current point is idle, which is neither an outage nor
    a finding.
    """
    out = []
    for service, metric in KNOWN_PRODUCERS:
        try:
            vals = extract_values(query(base, metric))
        except Unreachable:
            vals = []
        # ⚑ SERIES-EXISTS IS A DIFFERENT QUESTION FROM HAS-A-CURRENT-POINT, and conflating
        # them is what produced the false alarm.  An `Unreachable` here is unknown, not
        # absent — reported as such rather than folded into "never emitted".
        try:
            exists = bool(extract_series(series(base, metric)))
        except Unreachable:
            exists = None
        out.append((service, metric, max(vals) if vals else None, exists))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"store base URL (default {DEFAULT_BASE})")
    ap.add_argument("--reachable", action="store_true", help="is the store answering?")
    ap.add_argument("--series", metavar="SELECTOR", help="series matching a selector")
    ap.add_argument("--names", nargs="?", const="", metavar="SUBSTR", help="metric names")
    ap.add_argument("--query", metavar="PROMQL", help="run an instant query")
    ap.add_argument("--labels", metavar="SELECTOR", help="label values a selector's series carry")
    ap.add_argument("--verify", nargs=2, metavar=("SELECTOR", "VALUE"),
                    help="read-your-write: poll until SELECTOR returns VALUE")
    ap.add_argument("--changes", metavar="SELECTOR",
                    help="RAW stored samples per series, reported as TRANSITIONS (export)")
    ap.add_argument("--since", type=float, default=None,
                    help="--changes: epoch seconds to read from (default: all retained)")
    ap.add_argument("--producers", action="store_true",
                    help="listed producers: ever-emitted / in-flight (a READ, not a ping)")
    ap.add_argument("--ping", action="store_true",
                    help="write a value we choose and read it back — the only liveness test")
    ap.add_argument("--deadline", type=float, default=DEFAULT_DEADLINE)
    ap.add_argument("--poll", type=float, default=DEFAULT_POLL)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return 0 if _selftest() else 1

    if a.reachable:
        ok, detail = reachable(a.base)
        print(f"{'REACHABLE' if ok else 'UNREACHABLE'}  {a.base}  — {detail}")
        if not ok:
            print("  (both cassian engines bind loopback; off-host, tunnel first:\n"
                  "   ssh -L 8428:127.0.0.1:8428 -L 9428:127.0.0.1:9428 cassian)")
        return 0 if ok else 1

    if a.changes is not None:
        try:
            got = export_samples(a.base, a.changes, since=a.since)
        except Exception as e:                                   # noqa: BLE001
            print("UNREACHABLE  %s — %s: %s" % (a.base, type(e).__name__, e))
            return 1
        _n = 0
        for labels, pairs in sorted(got, key=lambda r: sorted(r[0].items())):
            _tr = transitions(pairs)
            _who = labels.get("suite") or labels.get("__name__") or "?"
            # ⚑ A SERIES THAT NEVER MOVED IS A RESULT, not a row to omit. Printing only the
            # changed ones would make "held steady" and "never written" look identical — the
            # absent-vs-empty collapse this module refuses everywhere else.
            if len(_tr) <= 1:
                print("  %-44s steady %s over %d sample(s)"
                      % (_who, _tr[0][2] if _tr else "-", len(pairs)))
                continue
            _n += 1
            print("  %-44s %d sample(s), %d change(s)" % (_who, len(pairs), len(_tr) - 1))
            for ts, before, after in _tr:
                print("      %s  %s → %s"
                      % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts / 1000.0)),
                         "-" if before is None else before, after))
        print("%d of %d series CHANGED in the window   (raw samples via /api/v1/export — "
              "no step, no manufactured gaps)" % (_n, len(got)))
        return 0

    try:
        if a.query is not None:
            rows = extract_rows(query(a.base, a.query))
            for name, labels, val in rows:
                lbl = ",".join(f"{k}={v!r}" for k, v in sorted(labels.items()))
                print(f"  {val!r}\t{name}{{{lbl}}}")
            print(f"{len(rows)} series returned for {a.query!r}")
            return 0

        if a.series is not None:
            found = extract_series(series(a.base, a.series))
            for s in found:
                nm = s.get("__name__", "")
                lbl = ",".join(f"{k}={v!r}" for k, v in sorted(s.items()) if k != "__name__")
                print(f"  {nm}{{{lbl}}}")
            print(f"{len(found)} series match {a.series!r}")
            return 0

        if a.names is not None:
            allnames = extract_names(names(a.base))
            hits = [n for n in allnames if a.names in n]
            for n in sorted(hits):
                print(f"  {n}")
            print(f"{len(hits)} of {len(allnames)} metric name(s) "
                  f"{'matching ' + repr(a.names) if a.names else 'in the store'}")
            return 0

        if a.labels is not None:
            found = extract_series(series(a.base, a.labels))
            keys = {}
            for s in found:
                for k, v in s.items():
                    keys.setdefault(k, set()).add(v)
            for k in sorted(keys):
                vs = sorted(keys[k])
                shown = ", ".join(vs[:8]) + (f", … (+{len(vs) - 8})" if len(vs) > 8 else "")
                print(f"  {k}\t{len(vs)} value(s)\t{shown}")
            print(f"{len(keys)} label(s) across {len(found)} series matching {a.labels!r}")
            return 0

        if a.ping:
            # ⚑ A HEARTBEAT IS CAUSED, NOT OBSERVED (user, 2026-08-03: *"Want a
            # heartbeat? ping; write then read."*).  Querying someone else's lapsed
            # token asks a question the store cannot answer — which is precisely why
            # `--producers` kept being misread as an outage.  This writes a value WE
            # choose, then polls for that exact value: the write-then-read pair is the
            # whole test, and it exercises the real path (exporter → ingest → index →
            # query) rather than inferring liveness from someone else's history.
            #
            # ⚑ NO SDK.  The OTLP integration was built not to require it, and routing
            # the ping through `emit_gauges` reintroduced it — making the liveness check
            # unavailable on a bare interpreter, which is when you most want it.
            # `otlp_gauge_payload` encodes the one fixed message shape from the stdlib.
            at = time.time()
            ok, detail = ping(a.base, at)
            print(f"tsdbprobe: ping WRITE — {detail}")
            if not ok:
                print("  A transport fault is distinct from an ingest or query fault; "
                      "this half cannot tell you about the other two.", file=sys.stderr)
                return 1
            print(f"  reading back tsdbprobe_emit_unixtime={at:.0f} "
                  f"(deadline {a.deadline:.0f}s)...")
            return verify(a.base, "tsdbprobe_emit_unixtime", at,
                          deadline_s=a.deadline, poll_s=a.poll, sink=sys.stdout)

        if a.producers:
            # ⚑ THREE STATES, NOT TWO.  `emitting` (a run is in flight), `idle` (has a
            # series, no current point — the NORMAL state between runs), and `never`
            # (no series at all).  The old report collapsed idle into `NO HEARTBEAT`,
            # which is alarm language for the expected condition and was misread every
            # time it was printed.
            rows = producers(a.base)
            now = time.time()
            for service, metric, val, exists in rows:
                if val is not None:
                    print(f"  emitting  {service:24s} run started {now - val:,.0f}s ago "
                          f"({metric}={val:.0f})")
                elif exists:
                    print(f"  idle      {service:24s} has emitted before; no run in flight "
                          f"(expected between runs)")
                elif exists is None:
                    print(f"  unknown   {service:24s} store did not answer for {metric}")
                else:
                    print(f"  never     {service:24s} no {metric} series has ever existed")
            emitting = sum(1 for r in rows if r[2] is not None)
            ever = sum(1 for r in rows if r[3])
            print(f"{ever} of {len(rows)} listed producer(s) have ever emitted; "
                  f"{emitting} with a run in flight now.")
            # ⚑ THE ROSTER IS NAME-SCOPED AND SAYS SO.  `KNOWN_PRODUCERS` is a hand-kept
            # list, so this cannot report a producer nobody added — measured: it omitted
            # `substrate.selftest` and `substrate.proofcost` while both were live.  A
            # count over a declared list is not a census, and printing it bare invites
            # exactly the coverage reading it cannot support.
            print(f"  ⚑ roster is DECLARED, not discovered ({len(rows)} name(s) in "
                  f"KNOWN_PRODUCERS) — a producer absent from it cannot appear here.")
            return 0
    except Unreachable as e:
        print(f"UNREACHABLE {a.base} — {e}", file=sys.stderr)
        print("  This is 'the store did not answer', NOT 'no data exists'.", file=sys.stderr)
        return 2

    if a.verify is not None:
        selector, value_s = a.verify
        try:
            expected = float(value_s)
        except ValueError:
            print("--verify VALUE must be a number", file=sys.stderr)
            return 2
        return verify(a.base, selector, expected, a.deadline, a.poll)

    ap.print_help()
    return 0


def _selftest():
    """Counted from len(cases). The PURE half proves without a live store.

    ⚑ THE LIVE HALF IS DELIBERATELY NOT MOCKED.  A suite that stands up a fake VM
    would be testing my model of VM, which is precisely the thing that was wrong in
    the `vm_rows_inserted_total` episode: everyone's model said the counter was
    queryable and the store disagreed.  So the cases pin the PARSERS and the COMPARE
    — the parts whose bugs are silent — and reachability stays an observation.
    """
    cases, ok = [], 0

    def check(name, got, want):
        nonlocal ok
        cases.append(name)
        if got == want:
            ok += 1
        else:
            print(f"  FAIL {name}: got {got!r} want {want!r}")

    vec = ('{"status":"success","data":{"resultType":"vector","result":'
           '[{"metric":{"__name__":"membudget_emit_unixtime"},'
           '"value":[1753300000.1,"1753300000"]}]}}')
    check("a vector response yields its sample value",
          extract_values(vec), [1753300000.0])

    # ⚑ THE MATRIX CASE: a range query nests samples under `values`, not `value`.
    # An extractor written against `vector` alone returns [] here — reporting a
    # range query with data as empty.
    mat = ('{"data":{"resultType":"matrix","result":[{"metric":{"__name__":"m"},'
           '"values":[[1,"1.5"],[2,"2.5"]]}]}}')
    check("a matrix (range) response yields ALL its samples",
          extract_values(mat), [1.5, 2.5])

    # ⚑ GARBAGE CAN NEVER VERIFY.  This is the oracle's safety property: if a
    # malformed body could yield a value, a broken store would confirm a write
    # that never landed.
    check("a malformed body yields no values", extract_values("not json"), [])
    check("an empty result vector yields no values",
          extract_values('{"data":{"result":[]}}'), [])
    check("a non-dict body yields no values", extract_values([1, 2, 3]), [])

    # ── transitions: the repetition is noise, the CHANGE is the answer ────
    # ⚑⚑ THIS MODE EXISTS BECAUSE I GUESSED THREE TIMES AND WAS WRONG THREE TIMES. A suite
    # total moved 2932 → 2929 and I attributed it to `_population`, then `--establish`, then
    # `project_sppf` — all edits I had just made, all innocent. The actual cause was
    # `reconstruct.py` 44 → 41 at 12:37, three cases GATED ON STORE STATE that stopped running
    # when `_node` emptied. No amount of reading my own diff could have found it; the series
    # answered it in one call.
    # ⚑ AND THE FIRST SAMPLE IS A TRANSITION FROM `None`, deliberately: a series' ARRIVAL is a
    # fact, and folding it into "no change" would make "began at 44" indistinguishable from
    # "always was 44" — the same absent-vs-empty collapse this module refuses at the API layer.
    check("an unchanged series reports ONE transition (its arrival)",
          transitions([(1, 5.0), (2, 5.0), (3, 5.0)]), [(1, None, 5.0)])
    check("a changed series reports the arrival AND the change",
          transitions([(1, 5.0), (2, 5.0), (3, 4.0)]),
          [(1, None, 5.0), (3, 5.0, 4.0)])
    check("...and a return to a prior value is its own transition",
          [t[2] for t in transitions([(1, 5.0), (2, 4.0), (3, 5.0)])], [5.0, 4.0, 5.0])
    check("an empty series yields no transitions", transitions([]), [])
    # ⚑ EXPORT'S SHAPE IS JSONL, NOT `{data:{result:[…]}}` — reusing `extract_values` here
    # would return [] for every line and report an EMPTY HISTORY for a populated store: an
    # absence manufactured by reading the right store with the wrong parser.
    check("the /query parser cannot read an /export line (why export has its own)",
          extract_values('{"metric":{},"values":[1],"timestamps":[2]}'), [])

    # ── the heartbeat is CAUSED, not observed ────────────────────────────
    # ⚑ `--ping` MUST WRITE BEFORE IT READS, and this asserts the pairing rather
    # than the outcome.  A liveness check that only QUERIES is asking about someone
    # else's last run — which is how `--producers` came to print `NO HEARTBEAT` for
    # a healthy store and be misread every time.  If a future edit drops the emit
    # and keeps the verify, this case fails.
    import inspect as _insp
    _src = _insp.getsource(main)
    _ping = _src[_src.index("if a.ping:"):]
    _ping = _ping[: _ping.index("if a.producers:")]
    check("--ping WRITES before it reads",
          _ping.index("ping(a.base") < _ping.index("verify("), True)
    # ⚑ AND IT MUST NOT NEED THE SDK.  My first cut routed the ping through
    # `membudget_otlp.emit_gauges` — "the one producer" — which made the LIVENESS check
    # require `opentelemetry-sdk`, unavailable exactly when you need to ask whether the
    # store is reachable. The OTLP integration was deliberately built SDK-free (as is
    # `spool`, on sqlite3); a probe is the last place to add a heavy optional dep.
    check("--ping needs no OTLP SDK",
          "membudget_otlp" not in _ping and "opentelemetry" not in _ping, True)

    # The hand-rolled protobuf must produce a decodable gauge, not merely some bytes.
    _pl = otlp_gauge_payload("m_test", 1753300000.0, 1753300000.0, "svc", "host")
    check("the OTLP payload carries the metric name", b"m_test" in _pl, True)
    check("the OTLP payload carries the resource attributes",
          b"service.name" in _pl and b"svc" in _pl, True)
    check("the OTLP payload is non-trivial protobuf", len(_pl) > 40, True)
    # ⚑ AND IT VERIFIES ITS OWN VALUE — `at`, chosen here — never a shared counter
    # and never the transport's 200.
    check("--ping verifies the value it chose", "verify(a.base," in _ping
          and '"tsdbprobe_emit_unixtime", at' in _ping, True)

    # ⚑ `producers()` REPORTS THREE STATES, and the middle one is why it was wrong.
    # `idle` (series exists, no current point) is the EXPECTED condition between
    # runs; the old code had only present/absent and printed `NO HEARTBEAT` for it.
    _psrc = _insp.getsource(producers)
    check("producers() asks series-exists separately from has-a-point",
          "extract_series" in _psrc and "extract_values" in _psrc, True)
    # ⚑ ASSERT ON THE CODE, NOT THE COMMENTARY.  My first cut searched `main`'s raw
    # source for `"NO HEARTBEAT" not in ...` — and FAILED, because the ⚑ comment
    # EXPLAINING the old defect quotes that string.  A source-text search cannot tell
    # a USE from a MENTION; this is the same class as `pycodemod --calls` needing a
    # CST because a docstring naming a function is not a call to it, and the same
    # class as my `agda_lex` sweep rewriting the case that DEMONSTRATES `\b` failing.
    # Strip comments, then assert on what executes.
    _rep = "\n".join(l for l in _src[_src.index("if a.producers:"):].splitlines()
                     if not l.lstrip().startswith("#"))
    check("the report distinguishes idle from never",
          "idle" in _rep and "never" in _rep and "NO HEARTBEAT" not in _rep, True)

    # ⚑ THE FLOAT-TOLERANT COMPARE, cassian query-readback:22-24. A string `==`
    # fails all three of these renderings of the SAME integer second.
    check("an integer rendering matches", matches([1753300000.0], 1753300000), True)
    check("a trailing-zero rendering matches", matches([1753300000.0], 1753300000.0), True)
    check("an exponent rendering matches", matches([1.7533e9], 1753300000), True)
    check("a DIFFERENT value does not match", matches([1753300001.0], 1753300000), False)
    check("no values never matches", matches([], 1753300000), False)

    # ⚑ /series RETURNS A BARE LIST AT `data` — a different shape from /query.
    # One extractor over both silently reports an inhabited store as empty.
    ser = ('{"status":"success","data":[{"__name__":"membudget_peak_mb",'
           '"module":"Foo","dir":"a/b"},{"__name__":"membudget_peak_mb",'
           '"module":"Bar","dir":"a/b"}]}')
    check("a /series response yields its label-sets", len(extract_series(ser)), 2)
    check("a /query response is NOT read as /series", extract_series(vec), [])
    check("a /series response is NOT read as /query", extract_values(ser), [])

    check("a label-values response yields its names",
          extract_names('{"data":["cassian_psi_avg10","membudget_peak_mb"]}'),
          ["cassian_psi_avg10", "membudget_peak_mb"])
    check("a non-string entry is dropped from names",
          extract_names('{"data":["ok",3,null]}'), ["ok"])

    # ⚑ ROWS KEEP THEIR LABELS.  The guide's doubled-generation gotcha (guide:69-71)
    # was invisible precisely because a value list cannot show that two series came
    # back where one was expected.
    rows = extract_rows(vec)
    check("a row carries its metric name", rows[0][0], "membudget_emit_unixtime")
    check("a row carries its latest value", rows[0][2], 1753300000.0)
    two = ('{"data":{"result":[{"metric":{"__name__":"m","job":"cassian"},"value":[1,"1"]},'
           '{"metric":{"__name__":"m"},"value":[1,"2"]}]}}')
    check("the label-less legacy generation shows as a SEPARATE row", len(extract_rows(two)), 2)
    check("labels are preserved per row", extract_rows(two)[0][1], {"job": "cassian"})

    # ⚑ verify() ON AN UNREACHABLE BASE MUST SAY 'NOT CONFIRMED', NOT 'FAILED'.
    # Conflating them is the documented false-"ingestion failed"
    # (substrate field report, 2026-07-23).  Driven for real against a closed port
    # with a zero deadline, not asserted from reading the code.
    import io
    sink = io.StringIO()
    rc = verify("http://127.0.0.1:1", "nope", 1.0, deadline_s=0.0, poll_s=0.0, sink=sink)
    check("verify against a dead store returns NOT-CONFIRMED (1), not a crash", rc, 1)
    check("and it says NOT CONFIRMED, never 'ingestion failed'",
          "NOT CONFIRMED" in sink.getvalue() and "ingestion failed" not in
          sink.getvalue().replace("does NOT mean ingestion failed", ""), True)

    print(f"tsdbprobe selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(main())
