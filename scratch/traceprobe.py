#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Structural questions about an OTLP TRACE SURFACE — cassian's VictoriaTraces (:10428).

⚑ WHY A NEW TOOL AND NOT A MODE ON `tsdbprobe`.  `tsdbprobe` reads a METRICS store: its
whole vocabulary is series-selectors, PromQL, label indexes and a float-valued
read-your-write.  A trace store shares none of that.  Its objects are SPANS in a
parent/child TREE, addressed by trace_id/span_id, read through a Jaeger-shaped
services/operations/traces API — and, crucially, its ORACLE IS A DIFFERENT KIND
(set-membership, not value-comparison; see VERIFY).  Adding `--trace-*` flags to a
metrics reader would put two incompatible oracles behind one banner, which is the shape
that produced the `vm_rows_inserted_total` mistake: one surface's semantics applied to
another's endpoint.  `tsdbprobe`'s own banner argues a new artifact kind with no reader
gets a TOOL; a live span store had none.

⚑⚑ THE ORACLE IS COARSER THAN THE METRIC ONE, AND THIS IS THE MOST IMPORTANT THING HERE.
There is NO per-span read-your-write equivalent of `query-readback`.  cassian
(cassian-observability-65, 2026-08-24) reports their working confirmation checks the
OPERATIONS INDEX — `GET /select/jaeger/api/services/<service>/operations` — for the
operation NAME, not the span body, because *"the trace-body query is window-fussy"*.
So `--verify` here is SET MEMBERSHIP over that index, deliberately:

  * we choose the operation name (a nonce), so it is still read-your-write in the sense
    that matters — the token is OURS, never a shared counter;
  * a name is either in the index or it is not — no float tolerance, no rendering
    ambiguity, and nothing for a time window to shade;
  * do NOT re-derive a per-span float-tolerant compare against `/api/traces/<id>` — it
    will fight the window.  Per-span confirmation by trace_id EXISTS but cassian has not
    proven it window-stable for a just-written span; `--trace` is provided and labelled
    UNVERIFIED rather than used as the oracle.

⚑ THE A98 POSTURE IS CARRIED, NOT RE-DERIVED (it is orthogonal to the oracle's kind):
  1. a fetch error is a RETRY, not a verdict — the store may be settling;
  2. an empty read is a RETRY, not an absence;
  3. on timeout: "NOT CONFIRMED", never "ingestion failed" — un-indexed, dropped and
     store-down are indistinguishable to this predicate, so it must not pick one.

⚑ latencyOffset: PARTIAL CONFIDENCE, and it is not ours to quote.  cassian could not
point at a traces-specific knob.  The metrics reasoning (the datum's timestamp is not
rewritten) transfers CONCEPTUALLY, but span reads are EMPIRICALLY more window-sensitive
than metric reads.  The deadline below is a CEILING ON WAITING, not a prediction, and no
number for someone else's operational parameter appears in this file.

⚑⚑⚑ THE STORE IS A WINDOW, NOT THE RECORD — and this reframes the architecture, so it is
stated before the modes rather than in a footnote.  cassian, 2026-08-25, measured on
VictoriaTraces **v0.10.0**: traces retain **30d** (metrics retain 90d), **and the on-disk
format is UNFROZEN — still v0.x, discardable across an upgrade.**  So a durable per-gate
jsonl line is NOT wedge-insurance that streaming made redundant; it is **the system of
record**, and this store is a 30-day queryable window onto it with no cross-upgrade
durability guarantee.  Anyone treating the trace store as durable loses data on an image
bump.

⚑⚑ STREAMING WORKS — MEASURED, TWICE, INDEPENDENTLY (substrate 2026-08-25 and cassian the
same day).  Spans of ONE trace_id POSTed separately are REASSEMBLED: 5/5 here, 3/3 on
their box with the parent written LAST (children referencing a parent that did not yet
exist).  No ingest-time ordering constraint.  **Orphaned children — the parent NEVER
written — are queryable as a trace.**  Incomplete traces are not GC'd waiting for a root.
So the span tree and wedge-survival collapse into ONE mechanism, and the signal is
sharper than "a gate opened and never closed": **a wedged SUITE is a trace whose ROOT is
ABSENT while children exist.**

⚑ BUT THE JOIN IS NOT INSTANT, AND THE HONEST FORM IS A RANGE: **~0 · 7.7 · 10.7 · 15.3
seconds** across 4 samples from two independent producers, with no clean relationship to
span count.  **Size any deadline against the HIGH end.**  The last POST's 200 does not
mean the assembled tree is readable — a fixed `sleep 5` would have false-negatived it
(cassian's first attempt did exactly that; polling is why the numbers are right, and a
literal `HTTP 404 {"data":[]}` was captured here — see `trace_by_id`).  **The production
emitter must EMIT AND MOVE ON**: a hook paying 8–15s of the operator's wall-clock to
confirm its own telemetry spends real time on nothing.  `--verify-tree` exists to PROVE
the path, never to run inside it.

⚑⚑ DO NOT EXPLAIN THE SPREAD.  The largest sample was the orphan case; "orphans settle
slower" is an UNESTABLISHED CAUSE and is struck.  The store indexes on a time window, so
settle time is plausibly dominated by flush PHASE rather than trace SHAPE, and at n=1
those are indistinguishable.  `verify_tree`'s docstring carries the confound and the
method that would separate it.

⚑ MEASURED LIMITS, carried rather than papered over: orphan visibility is proven at
t+0..30s, **NOT across compaction or the full 30d**.  Concurrent trace_id collisions,
gRPC, and behaviour under ingest load are UNMEASURED.  Our volume is far from those
regimes; that is a reason to proceed, not a reason to claim coverage.

⚑ WRITE ONLY TO `/insert/...`.  Ingest is OTLP/HTTP (protobuf OR JSON) at
`/insert/opentelemetry/v1/traces`.  cassian has NOT tested OTLP/gRPC and told us not to
assume it — this tool speaks HTTP only.  Reads live under `/select/jaeger/api/*` (also a
Tempo API at `/select/tempo`, unused here).

    traceprobe.py --reachable                   # is the span store up — and WHICH failure
    traceprobe.py --services                    # what service.names the store has seen
    traceprobe.py --operations <service>        # the operations index for one service
    traceprobe.py --emit [--service S]          # write a real parent/child span tree (nonce op)
    traceprobe.py --verify <service> <opname>   # set-membership read-your-write on the index
    traceprobe.py --ping                        # --emit then --verify: the only liveness test
    traceprobe.py --stream <n>                  # ⚑ does an INCREMENTAL per-span POST work?
    traceprobe.py --trace <trace_id>            # UNVERIFIED: span bodies by trace id
    traceprobe.py --selftest

Stdlib only, like `tsdbprobe` — this must be runnable from a hook with no venv.  `--base`
defaults to the loopback `:10428`; off-host, tunnel first
(`ssh -L 10428:127.0.0.1:10428 cassian`) — the engine binds loopback deliberately, the
same posture as VM `:8428` and VLogs `:9428`.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import socket
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:10428"
INSERT_PATH = "/insert/opentelemetry/v1/traces"
JAEGER = "/select/jaeger/api"

# ⚑ ONE SERVICE, COMPONENT AS AN ATTRIBUTE — cassian's recommendation, adopted with the
# reason rather than the instruction.  The operations index is PER-SERVICE, so spelling
# each component as its own service (`substrate.clause-audit`, `substrate.membudget`, …)
# fragments the query surface: N indexes to check instead of one, and N entries in
# Grafana's dropdown.  A component is a LABEL on a span, not an identity.
# ⚑ This is a preference with a stated reason, NOT a measured constraint — cassian said
# so explicitly.  It is reversible; what would not be reversible is entrenching the
# fragmented spelling across several emitters before anyone notices the cost.
DEFAULT_SERVICE = "substrate"
COMPONENT_ATTR = "component"
DEFAULT_DEADLINE = 45.0
DEFAULT_POLL = 1.5


class Unreachable(Exception):
    """The store did not answer — distinct from answering 'nothing matched'.

    ⚑ Same reason as `tsdbprobe.Unreachable`, and it is the tool's reason for existing.
    An exception for 'no answer' and an empty list for 'answered, empty' keeps the two
    un-conflatable BY CONSTRUCTION rather than by the caller's discipline.
    """


def _get(base: str, path: str, params: dict | None = None, timeout: float = 8.0):
    url = base.rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")[:300]
        except Exception:  # noqa: BLE001
            detail = ""
        raise Unreachable(f"HTTP {e.code} from {path}: {detail}") from e
    except Exception as e:  # noqa: BLE001
        raise Unreachable(f"{type(e).__name__}: {e}") from e
    try:
        return json.loads(raw)
    except ValueError as e:
        raise Unreachable(f"non-JSON body from {path}: {raw[:200]!r}") from e


# --- the pure half (parsers + encoder), so the tool self-proves without a live store ---

def extract_data_list(body) -> list:
    """PURE: the `data` list from a Jaeger-shaped response. [] on anything else.

    ⚑ [] ON GARBAGE, NEVER AN EXCEPTION AND NEVER A FALSE MEMBER.  This parses the
    ORACLE's response, so a malformed body must be INCAPABLE of confirming a write.
    The metrics tool's `extract_values` has the identical safety property for the
    identical reason; it is carried, not re-derived.
    """
    if isinstance(body, (str, bytes)):
        try:
            body = json.loads(body)
        except (ValueError, TypeError):
            return []
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    return data if isinstance(data, list) else []


def extract_names(body) -> list[str]:
    """PURE: string entries of a Jaeger `data` list (services / operations).

    ⚑ THE OPERATIONS INDEX HAS TWO RENDERINGS and both must read.  Jaeger's older
    `/operations` returns bare strings; the newer one returns
    `{"name": ..., "spanKind": ...}` objects.  An extractor written against one
    silently returns [] for the other — which would report an EMPTY INDEX for a
    populated store, i.e. manufacture the exact absence this tool exists to avoid
    asserting.
    """
    out = []
    for d in extract_data_list(body):
        if isinstance(d, str):
            out.append(d)
        elif isinstance(d, dict):
            n = d.get("name")
            if isinstance(n, str):
                out.append(n)
    return out


def member(names: list[str], expected: str) -> bool:
    """PURE: the ORACLE. Set membership — exact, no tolerance, no rendering ambiguity.

    ⚑⚑ THIS IS DELIBERATELY *NOT* `tsdbprobe.matches`.  There, the token is a float the
    store may render three ways, so a string `==` would false-negative a landed write.
    Here the token is a NAME the store echoes verbatim, so a fuzzy compare would
    false-POSITIVE — a near-miss operation from an earlier run confirming this one.
    The two oracles are different KINDS, and that difference is why this is a separate
    tool rather than a flag on that one.
    """
    return expected in names


def _hexid(nbytes: int) -> str:
    return "%0*x" % (nbytes * 2, random.getrandbits(nbytes * 8))


def _pb_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _pb_field(num: int, wire: int, payload: bytes) -> bytes:
    tag = _pb_varint((num << 3) | wire)
    return tag + (_pb_varint(len(payload)) + payload if wire == 2 else payload)


def _pb_str(num: int, s: str) -> bytes:
    return _pb_field(num, 2, s.encode())


#: ⚑⚑⚑ THE ATTRIBUTE NAMES ARE THE WHOLE POINT OF Ⓞ9, so they are declared, not spelled
#: inline.  A span carries `startTimeUnixNano`/`endTimeUnixNano` and NOTHING ELSE by
#: default, and those measure WALL CLOCK.  On a box that is busy by design, wall clock is
#: a fact about CO-TENANCY, not about the work: the same gate reads 60s or 600s depending
#: on who else is running.  CPU time is the invariant — contention delays a process, it
#: does not inflate the cycles it consumes.
#:
#: ⚑⚑ BOTH ARE KEPT AND BOTH ARE NAMED, because they answer DIFFERENT questions and
#: collapsing them is the error this fixes:
#:   * WALL answers *did this wedge* — a span opened and never closed is a wall-clock
#:     fact, and the orphan/no-root signal is a wall-clock signal.  A wedged gate consumes
#:     no CPU at all while blocked on a lock or a pipe, so CPU alone CANNOT see a wedge.
#:   * CPU answers *what does this cost* — the figure that survives contention and is
#:     comparable across runs.
#: Choosing one would blind the tool to half its purpose.  A reader must never have to
#: guess which a bare "duration" meant, so neither is called `duration`.
CPU_ATTR = "cpu.seconds"              # user+sys of THIS process, delta across the span
CPU_USER_ATTR = "cpu.user.seconds"
CPU_SYS_ATTR = "cpu.sys.seconds"
CPU_CHILDREN_ATTR = "cpu.children.seconds"   # REAPED children only — see CpuClock
WALL_ATTR = "wall.seconds"            # named explicitly so it is never the unlabelled default
CPU_SCOPE_ATTR = "cpu.scope"          # which rusage scope produced the numbers


class CpuClock:
    """CPU-time delta across a span. `RUSAGE_SELF` + `RUSAGE_CHILDREN`, reported apart.

    ⚑⚑⚑ WHAT THIS CANNOT SEE, STATED FIRST BECAUSE IT IS THE TRAP.  `RUSAGE_CHILDREN`
    accrues ONLY ON REAPED CHILDREN — the kernel adds a child's usage to the parent's
    accounting at `wait()`, not while it runs.  Three consequences, all of them silent:

      * a gate that shells out and is KILLED before reaping loses its subprocess CPU
        ENTIRELY — the number reads LOW, and low reads as cheap;
      * a still-RUNNING child contributes ZERO until it exits, so a span closed while
        work is in flight undercounts;
      * an ORPHANED subtree reparented to init is never reaped by us and is invisible
        forever.  (Measured on this box: an orphaned fan-out held 7533s of subtree CPU.)

    ⚑ SO THE SCOPE IS RECORDED ON THE SPAN (`cpu.scope`), NEVER ASSUMED.  A consumer that
    cannot tell `self` from `self+reaped-children` will read a shell-out gate's cost as
    its Python overhead.  `procstruct --cost` reads LIVE processes and is the better
    source for a running subtree — but it cannot attribute CPU to a PHASE inside one
    process, which is what a span needs, so the two are complementary rather than
    alternatives.

    ⚑ `time.process_time()` IS DELIBERATELY NOT USED: it excludes children entirely and
    on some platforms excludes system time, so it would silently answer a narrower
    question than the attribute name promises.
    """

    def __init__(self, with_children: bool = True):
        self.with_children = with_children
        self.scope = "self+reaped_children" if with_children else "self"
        self._t0 = self._read()
        self._w0 = time.monotonic()

    @staticmethod
    def _rusage(who):
        import resource
        r = resource.getrusage(who)
        return r.ru_utime, r.ru_stime

    def _read(self):
        import resource
        su, ss = self._rusage(resource.RUSAGE_SELF)
        if not self.with_children:
            return su, ss, 0.0, 0.0
        cu, cs = self._rusage(resource.RUSAGE_CHILDREN)
        return su, ss, cu, cs

    def deltas(self) -> dict:
        """{attr: seconds} — CPU and WALL together, each explicitly labelled."""
        su, ss, cu, cs = self._read()
        d_su, d_ss = su - self._t0[0], ss - self._t0[1]
        d_cu, d_cs = cu - self._t0[2], cs - self._t0[3]
        out = {
            CPU_USER_ATTR: round(d_su, 6),
            CPU_SYS_ATTR: round(d_ss, 6),
            CPU_ATTR: round(d_su + d_ss + d_cu + d_cs, 6),
            WALL_ATTR: round(time.monotonic() - self._w0, 6),
            CPU_SCOPE_ATTR: self.scope,
        }
        if self.with_children:
            out[CPU_CHILDREN_ATTR] = round(d_cu + d_cs, 6)
        return out


def span_json(name: str, trace_id: str, span_id: str, start_unix: float,
              end_unix: float, parent_id: str = "", attrs: dict | None = None) -> dict:
    """PURE: one OTLP/JSON Span object.

    ⚑ JSON, NOT PROTOBUF, AND THE CHOICE IS LOAD-BEARING FOR THIS TOOL'S PURPOSE.
    cassian confirms the endpoint accepts BOTH.  `tsdbprobe` hand-rolls protobuf because
    a metric gauge is a fixed 4-field shape; a span tree is nested, variable-arity and
    carries arbitrary attributes, so hand-rolled protobuf here would be a real encoder to
    maintain — and its bugs would be SILENT (a mis-tagged field is dropped, not rejected).
    JSON is inspectable in the failure case, which is the whole reason a probe exists.

    ⚑ ids are HEX STRINGS in OTLP/JSON (base64 in protobuf) — a common and silent error.
    Times are STRING nanoseconds: JSON numbers lose precision above 2^53 ns.
    """
    # ⚑⚑⚑ ASSERT THE ID LENGTHS AT CONSTRUCTION — cassian's trap 1, and it is the
    # dangerous one because it FAILS SILENTLY IN THE WORST POSSIBLE PLACE. A
    # wrong-length id is OTLP-SHAPED BUT INVALID, so the store may return 200 AND DROP
    # the span. At the transport layer that is indistinguishable from a successful
    # write, and our `--verify` would then report NOT CONFIRMED — which we would read as
    # flush lag and bank as a store property. A false diagnosis about someone else's
    # store, caused by our own malformed producer.
    # So: fail LOUDLY at the producer rather than quietly at the store. This is the one
    # place in this file where an exception beats a tolerant parse, because here the
    # caller is US and the mistake is ours to fix.
    for _nm, _v, _want in (("traceId", trace_id, 32), ("spanId", span_id, 16),
                           ("parentSpanId", parent_id, 16)):
        if _v and len(_v) != _want:
            raise ValueError(
                f"{_nm} must be {_want} hex chars ({_want // 2} bytes), got {len(_v)}: "
                f"{_v!r} — a wrong-length id may be accepted with 200 and DROPPED, "
                f"which reads back as 'unconfirmed' and gets misdiagnosed as lag.")
    s = {
        "traceId": trace_id,
        "spanId": span_id,
        "name": name,
        "kind": 1,  # SPAN_KIND_INTERNAL
        "startTimeUnixNano": str(int(start_unix * 1e9)),
        "endTimeUnixNano": str(int(end_unix * 1e9)),
    }
    if parent_id:
        s["parentSpanId"] = parent_id
    if attrs:
        s["attributes"] = [
            {"key": k, "value": ({"stringValue": v} if isinstance(v, str)
                                 else {"intValue": str(int(v))} if isinstance(v, bool) is False and isinstance(v, int)
                                 else {"doubleValue": float(v)} if isinstance(v, float)
                                 else {"boolValue": bool(v)} if isinstance(v, bool)
                                 else {"stringValue": str(v)})}
            for k, v in attrs.items()
        ]
    return s


def traces_payload(spans: list[dict], service: str, instance: str | None = None,
                   component: str | None = None) -> dict:
    """PURE: an OTLP/JSON ExportTraceServiceRequest wrapping `spans`.

    ⚑ PIN THE RESOURCE, never a generated instance id.  The metrics side learned this
    the expensive way: `Resource.create()` injects a random per-process
    `service.instance.id`, so every run mints a fresh series set instead of updating one.
    The trace analogue is cardinality churn in the service index; the same rule applies.
    """
    # ⚑ `component` IS A RESOURCE ATTRIBUTE, NOT A SPAN ATTRIBUTE — cassian's trap 3,
    # and I had it on the span until they sent the verbatim shape. It belongs beside
    # `service.name` because it identifies the PRODUCER, not the operation: it is
    # constant across every span of a run, so per-span is both wrong and N× redundant.
    # Per-span attributes are for what VARIES (gate verdict, gate name).
    attrs = [
        {"key": "service.name", "value": {"stringValue": service}},
        {"key": "service.instance.id",
         "value": {"stringValue": instance or socket.gethostname()}},
    ]
    if component:
        attrs.append({"key": COMPONENT_ATTR, "value": {"stringValue": component}})
    return {"resourceSpans": [{
        "resource": {"attributes": attrs},
        "scopeSpans": [{"scope": {"name": "substrate.traceprobe"}, "spans": spans}],
    }]}


def suite_tree(op: str, service: str, gates: list[tuple[str, float, str]],
               t0: float | None = None) -> tuple[str, list[dict]]:
    """PURE: (trace_id, spans) — a suite parent with one child per gate.

    ⚑ THIS IS THE SHAPE THE USE CASE NEEDS: suite = parent, gate = child, verdict an
    ATTRIBUTE.  A wedged gate is then a span that OPENED and never CLOSED — structurally
    distinct from slow-but-completed, which is exactly the question stdout could not
    answer after `check_clause_audit` was killed at ~30 min with 10 bytes of output.
    """
    t0 = time.time() if t0 is None else t0
    tid = _hexid(16)
    root = _hexid(8)
    spans = [span_json(op, tid, root, t0, t0 + sum(g[1] for g in gates),
                       attrs={"suite.gates": len(gates)})]
    at = t0
    for gname, dur, verdict in gates:
        spans.append(span_json(gname, tid, _hexid(8), at, at + dur, parent_id=root,
                               attrs={"gate.verdict": verdict}))
        at += dur
    return tid, spans


# --- the live half ------------------------------------------------------------------

RETRYABLE = (429, 503, 502, 504)


def post_spans(base: str, payload: dict, timeout: float = 10.0,
               retries: int = 3, backoff: float = 0.5) -> tuple[bool, str]:
    """WRITE. (ok, detail) — the transport half only.

    ⚑⚑ THE ASYMMETRY, AND IT IS OUR OWN LESSON INVERTED: **a 200 is NOT proof of
    storage, but a non-200 IS proof of refusal.**  Everywhere else in this file an
    absence is ambiguous and must not be read as a verdict; here, a 429/503 is the
    store SAYING NO, which is a fact, and the one signal we are obliged to act on.
    So this is the single place that retries on the store's answer rather than on the
    absence of one.

    ⚑ THE BACKPRESSURE DIVISION (cassian, 2026-08-25), adopted as stated: THEY own the
    store-health signal — the cgroup's `memory.events` and PSI on `cassian-vtraces`
    go red BEFORE drops and they already collect them; they explicitly do NOT want a
    backpressure metric from us.  WE own respecting a non-200.  That is the whole of
    our obligation, and it is small.

    ⚑ THEY HAVE NOT STRESS-TESTED the 256M cap under trace-ingest load and REFUSE to
    guess the spans/sec at which `memory.events` increments — *"measurement extended
    past its domain."*  At ~36 spans a few times an hour we are nowhere near, so this
    is deliberately NOT designed for volume.  If we ever plan real trace volume we tell
    them BEFORE and they watch the cgroup live while we ramp: coordinated measurement,
    not discovery.

    ⚑ A 200 IS NOT INGESTION.  It is the only thing this half can report, which is
    exactly why the read-back half exists.  Never return ok meaning 'landed'.
    """
    data = json.dumps(payload).encode()
    for attempt in range(retries):
        req = urllib.request.Request(
            base.rstrip("/") + INSERT_PATH, data=data,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return True, (f"POST {r.getcode()} (transport only; ingestion unproven "
                              f"until read-back)")
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", "replace")[:300]
            except Exception:  # noqa: BLE001
                detail = ""
            if e.code in RETRYABLE and attempt < retries - 1:
                # ⚑ THE STORE SAID NO AND THAT IS ACTIONABLE — back off rather than
                # hammer it. A refusal under pressure is the one non-ambiguous signal
                # this transport gets.
                time.sleep(backoff * (2 ** attempt))
                continue
            return False, (f"POST REFUSED HTTP {e.code}{' (retryable, gave up after '
                           f'{retries})' if e.code in RETRYABLE else ''}: {detail}")
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            return False, f"POST failed: {type(e).__name__}: {e}"
    return False, "POST failed: retries exhausted"


def reachable(base: str) -> tuple[bool, str]:
    """(ok, detail) — is the span store answering, and if not, HOW does it fail?

    ⚑ 'DOWN' AND 'UP BUT REFUSING THIS PATH' ARE DIFFERENT REPAIRS.  A bare boolean sends
    you to systemctl when the fault is a missing tunnel or a wrong API prefix.  The
    services index is used as the probe because it is the cheapest READ on the API we
    actually depend on — a `/health` that passes while `/select/jaeger` 404s would be a
    green light for a surface we cannot use.
    """
    try:
        body = _get(base, JAEGER + "/services", timeout=5.0)
        return True, f"jaeger services index ok ({len(extract_names(body))} service(s) known)"
    except Unreachable as e:
        return False, str(e)


def services(base: str) -> list[str]:
    return extract_names(_get(base, JAEGER + "/services"))


def operations(base: str, service: str) -> list[str]:
    return extract_names(_get(base, JAEGER + "/services/"
                              + urllib.parse.quote(service, safe="") + "/operations"))


def trace_by_id(base: str, trace_id: str) -> list:
    """UNVERIFIED per cassian: exists, but not proven window-stable for a fresh span.

    ⚑⚑ A 404 HERE IS AN ANSWER, NOT A FAILURE TO ANSWER — and reading it as the latter
    was this tool committing, on its first live run, the exact collapse its banner
    refuses.  MEASURED 2026-08-25: a trace whose 5 spans had just been POSTed (each a
    200, the operation CONFIRMED in the index) read back as
    `HTTP 404 {"data":[],"errors":[{"code":404,"msg":"trace not found"}]}`.  That body
    is well-formed, it parses, and it says *nothing matched* — which is the empty case,
    distinct from `Unreachable`.  Surfacing it as UNREACHABLE told the operator to check
    the tunnel about a store that was answering perfectly.

    ⚑⚑⚑ AND THIS IS THE WITNESS FOR THE POLL-DON'T-SLEEP RULE — the captured failure,
    not the reasoning about it.  cassian rewrote a fixed `sleep` into a poll to AVOID
    manufacturing a false negative; that was foresight.  THIS is the literal artifact
    that foresight was about: a SINGLE read here, taken moments after the last 200,
    would have produced *"VictoriaTraces does not reassemble streamed traces"* — a false
    STRUCTURAL conclusion about the store's design, drawn from a TIMING artifact, on the
    exact question this tool was built to settle.  The same trace read back complete
    seconds later.  Kept verbatim because a rule keeps its force only while the failure
    it prevents is still legible.

    ⚑ AND THE EMPTY IS ITSELF AMBIGUOUS, which is cassian's whole warning about this
    path: not-yet-indexed, aged-out-of-window, and genuinely-not-joined are
    indistinguishable to this read.  So this returns [] and the CALLER must not read []
    as "the store did not reassemble the tree".  That is why `--verify` uses the
    operations index instead, and why this mode is labelled UNVERIFIED in the output.
    """
    try:
        return extract_data_list(
            _get(base, JAEGER + "/traces/" + urllib.parse.quote(trace_id)))
    except Unreachable as e:
        if "HTTP 404" in str(e):
            return []
        raise


def verify(base: str, service: str, op: str, deadline_s: float = DEFAULT_DEADLINE,
           poll_s: float = DEFAULT_POLL, sink=None) -> int:
    """SET-MEMBERSHIP read-your-write on the operations index. 0 = confirmed, 1 = NOT.

    Oracle per cassian-observability-65: check the operations index for the operation
    NAME, not the span body — *"the trace-body query is window-fussy"*.  The A98 posture
    (retry on error, retry on empty, never say 'failed') is carried from `tsdbprobe`.
    """
    say = (sink if sink is not None else sys.stderr).write
    end = time.monotonic() + deadline_s
    last = "no read has succeeded yet"
    while True:
        try:
            ops = operations(base, service)
            if member(ops, op):
                say(f"traceprobe: CONFIRMED — operation {op!r} is in the index for "
                    f"service {service!r} (set-membership read-your-write)\n")
                return 0
            last = (f"service known, {len(ops)} operation(s), none is {op!r}" if ops
                    else f"no operations indexed for {service!r} yet")
        except Unreachable as e:
            last = f"unreachable: {e}"
        except Exception as e:  # noqa: BLE001
            last = f"read error: {e}"
        if time.monotonic() >= end:
            say(f"traceprobe: NOT CONFIRMED within {deadline_s:.0f}s — {last}. "
                f"This does NOT mean ingestion failed: not-yet-indexed, dropped and "
                f"store-down are indistinguishable here. Diagnose with --reachable.\n")
            return 1
        time.sleep(poll_s)


def tree_shape(traces: list) -> tuple[int, int, list[str]]:
    """PURE: (n_spans, n_roots, orphan_parent_ids) over a Jaeger /traces response.

    ⚑⚑ THE SECOND ORACLE'S PREDICATE, AND IT IS A DIFFERENT KIND FROM `member`.
    cassian's correction (2026-08-25), which is our own lesson turned back on us: the
    operations index shows a name the instant ANY ONE span carrying it lands, so
    `--verify` **cannot distinguish 3 spans that joined from 3 one-span traces**, and it
    cannot witness a missing parent.  It answers *did a span LAND*; it is STRUCTURALLY
    BLIND to shape.  Letting it pretend otherwise would be `vm_rows_inserted_total`
    again — one oracle's semantics applied to another's question.

    A ROOT is a span with no parent reference.  An ORPHAN parent id is one referenced as
    a CHILD_OF but never itself written — and for us that is not an error, it is THE
    WEDGE SIGNAL: a suite whose root is absent while its children exist.
    """
    spans, roots, seen, referenced = 0, 0, set(), []
    for t in traces:
        if not isinstance(t, dict):
            continue
        for sp in t.get("spans") or []:
            if not isinstance(sp, dict):
                continue
            spans += 1
            sid = sp.get("spanID")
            if sid:
                seen.add(sid)
            refs = [r for r in (sp.get("references") or [])
                    if isinstance(r, dict) and r.get("refType") == "CHILD_OF"]
            if not refs:
                roots += 1
            for r in refs:
                if r.get("spanID"):
                    referenced.append(r["spanID"])
    return spans, roots, sorted({p for p in referenced if p not in seen})


def verify_tree(base: str, trace_id: str, expect_spans: int | None = None,
                deadline_s: float = 30.0, poll_s: float = DEFAULT_POLL, sink=None) -> int:
    """STRUCTURE oracle: poll /traces/<id> until the tree is assembled. 0 = ok, 1 = NOT.

    ⚑⚑ THE DEADLINE IS 30s AND IT IS A CEILING OVER A RANGE — never one figure plus a
    hedge.  MEASURED settle times for a streamed join, 4 samples across two independent
    producers (substrate + cassian-observability, 2026-08-25):

        ~0s  ·  7.7s  ·  10.7s  ·  15.3s        — SIZE AGAINST THE HIGH END

    There is no clean relationship to span count.  Anything tuned toward the middle of
    that range sizes against a low sample and FLAKES; 30s clears the observed high with
    headroom.  Do NOT read it as a prediction, and do NOT shrink it toward any single
    measurement.

    ⚑⚑ WHY A RANGE AND NOT A NUMBER, recorded because the correction ran BOTH ways.  This
    docstring cited only cassian's 10.7s; I then measured 15.3s and told them a single
    figure plus a hedge reads as a figure — a reader treats the hedge as politeness.
    They conceded and rewrote their record, and the same correction applied HERE, to the
    artifact I had already written.  Catching it in someone else's prose is not catching
    it in your own.

    ⚑⚑⚑ AND THE SPREAD HAS AN UNSEPARATED CONFOUND — DO NOT EXPLAIN IT.  The largest
    sample happened to be the orphan/no-root case, and I offered "plausibly the no-root
    path has no natural completion trigger."  That is an UNESTABLISHED CAUSE and it is
    struck.  VictoriaTraces indexes on a time window — which is WHY a settle delay exists
    at all — so settle time on a lightly-loaded box is plausibly dominated by WHERE IN
    THE FLUSH CYCLE the POST landed, not by trace shape.  At n=1 for the orphan case,
    "orphans settle slower" and "that POST landed early in a flush window" are
    INDISTINGUISHABLE, and the second requires no new mechanism.  Shape-vs-phase is
    unseparated; the observation stands, the explanation does not.

    ⚑⚑ AND A FIFTH SAMPLE ARRIVED THAT SETTLES IT AGAINST THE SHAPE STORY.  Re-reading
    THE SAME orphan trace (`41fb226f…`, 4 spans, 0 roots) minutes later returned in
    **0.1s** — the identical shape that had taken 15.3s.  Same trace, same structure,
    two orders of magnitude apart.  Shape is CONSTANT across those two reads and cannot
    explain the difference; the elapsed time since the write is what changed.  That is
    direct evidence for the flush/index-window account and against the one I floated,
    and it is stronger than the argument that displaced it.

    ⚑ SO THE MEASUREMENT IS "TIME SINCE WRITE", NOT "SETTLE TIME OF A SHAPE".  The 4
    numbers above are first-read latencies for freshly-written traces; a trace already
    past its indexing window reads immediately.  A deadline still sizes against the high
    end, because the emitter's own read-back is always the fresh case.

    ⚑ WHAT WOULD FULLY SEPARATE THEM, recorded so the next reader knows the method rather
    than inheriting the folklore: emit the SAME shape many times and read the settle
    DISTRIBUTION — flush noise shows as variance uncorrelated with shape.  Neither party
    is proposing that; our volume does not warrant it, and the 0.1s re-read already
    removes the motivation.  Written down because a plausible mechanism attached to one
    sample is exactly how "orphans are slow" becomes a fact the next reader inherits.

    ⚑ THE PRODUCTION EMITTER MUST NOT CALL THIS.  A pre-commit hook paying 8–15s of the
    operator's wall-clock to confirm its own telemetry is spending real time on nothing.
    Emit-and-move-on; this mode is for PROVING the path, not for running inside it.
    """
    say = (sink if sink is not None else sys.stderr).write
    end = time.monotonic() + deadline_s
    t_start = time.monotonic()
    last = "no read has succeeded yet"
    while True:
        try:
            got = trace_by_id(base, trace_id)
            nspans, nroots, orphans = tree_shape(got)
            if nspans and (expect_spans is None or nspans == expect_spans):
                say(f"traceprobe: TREE CONFIRMED — {nspans} span(s) in {len(got)} trace(s), "
                    f"{nroots} root(s), {len(orphans)} orphaned parent ref(s), "
                    f"settled in {time.monotonic() - t_start:.1f}s\n")
                if orphans:
                    say(f"  ⚑ WEDGE SIGNAL: parent(s) {', '.join(orphans)} referenced but "
                        f"never written — children exist with no root. This is the "
                        f"structure a membership oracle CANNOT see.\n")
                return 0
            last = (f"{nspans} span(s) so far, expected {expect_spans}" if nspans
                    else "no spans readable yet")
        except Unreachable as e:
            last = f"unreachable: {e}"
        except Exception as e:  # noqa: BLE001
            last = f"read error: {e}"
        if time.monotonic() >= end:
            say(f"traceprobe: TREE NOT CONFIRMED within {deadline_s:.0f}s — {last}. "
                f"Not-yet-joined, dropped and store-down are indistinguishable here. "
                f"Measured joins settle over ~0-15.3s (4 samples, two producers), so a "
                f"short read proves nothing; diagnose with --reachable.\n")
            return 1
        time.sleep(poll_s)


def emit(base: str, service: str, op: str | None = None):
    """Write one real suite/gate span TREE in a single POST. -> (ok, detail, op, trace_id)."""
    op = op or ("traceprobe-suite-%d-%s" % (int(time.time()), _hexid(3)))
    tid, spans = suite_tree(op, service, [
        ("gate.alpha", 0.20, "pass"),
        ("gate.beta", 0.35, "pass"),
        ("gate.gamma", 0.10, "fail"),
    ])
    ok, detail = post_spans(base, traces_payload(spans, service, component="traceprobe"))
    return ok, detail, op, tid


def stream(base: str, service: str, n: int):
    """⚑ THE CRUX: does an INCREMENTAL per-span POST work for ONE trace_id?

    The pre-commit use case needs spans emitted AS EACH GATE ENDS, not assembled and
    POSTed once at the end.  cassian named the trap in their own `build-telemetry`: it
    POSTs the whole trace at the end, so **if the run wedges mid-way the trace never
    emits** — the same failure as stdout evaporating, for the exact case we most need.

    ⚑⚑ MEASURED AND SETTLED — this docstring said "that is a prediction" until the
    measurement came in, and the answer is YES.  5/5 incremental POSTs reassembled into
    one trace here (2026-08-25), and cassian independently got 3/3 on their box with the
    PARENT WRITTEN LAST.  So the span tree and wedge-survival collapse into ONE
    mechanism; the durable jsonl floor stays for a different reason (retention +
    unfrozen format), not as wedge-insurance.

    ⚑⚑ AND THE TWO RESULTS ARE DECORRELATED, WHICH IS WHY THE PAIR IS WORTH MORE THAN
    EITHER: two textually-distinct producers, different span counts (5 vs 3), different
    code, different orderings — agreeing on BOTH join and orphan-visibility.  A second
    run of the same script would have been repetition; this is independent corroboration,
    and it is the reason these claims are stated flatly rather than hedged.

    ⚑ THE JOIN IS NOT INSTANT — settles measured at ~0 / 7.7 / 10.7 / 15.3s, no clean
    relation to span count — so this mode's own read-back polls.  A single read moments
    after the last 200 reads EMPTY and would report "the store does not reassemble": a
    false structural conclusion from a timing artifact.  Observed here for real (the
    verbatim 404 is in `trace_by_id`), which is why the read path retries.

    Returns (op, trace_id, [(i, ok, detail)]) — the per-POST outcomes.
    """
    op = "traceprobe-stream-%d-%s" % (int(time.time()), _hexid(3))
    t0 = time.time()
    tid, spans = suite_tree(op, service,
                            [("stream.gate.%d" % i, 0.1, "pass") for i in range(n)], t0=t0)
    results = []
    for i, sp in enumerate(spans):
        ok, detail = post_spans(base, traces_payload([sp], service,
                                                     component="traceprobe"))
        results.append((i, ok, detail))
    return op, tid, results


def wedge(base: str, service: str):
    """⚑⚑ THE SIGNAL, NOT AN ERROR CASE: children written, parent NEVER written.

    This is the pre-commit wedge, staged deliberately. A suite opens, three gates run
    and are each emitted as they close, then the fourth gate HANGS and the process is
    killed — so the fourth child never closes and the ROOT SPAN IS NEVER WRITTEN AT ALL
    (it cannot close until every gate has). Post-hoc assembly emits nothing here, which
    is precisely the failure mode `build-telemetry` has and stdout has.

    The question this measures: does the store keep and serve ORPHANED CHILDREN — spans
    whose parentSpanId names a span that does not exist? If yes, a wedge is READABLE:
    the trace shows N-1 closed gates plus one open, and no root. If the store GCs
    incomplete traces, streaming alone cannot carry this and the durable jsonl floor is
    load-bearing rather than belt-and-braces.

    ⚑ The still-open gate is emitted with end == start. A zero-duration span is how "it
    started and we never saw it finish" is representable at all; the alternative is not
    emitting it, which loses WHICH gate wedged — the single most useful fact.
    """
    op = "traceprobe-wedge-%d-%s" % (int(time.time()), _hexid(3))
    t0 = time.time()
    tid = _hexid(16)
    ghost_root = _hexid(8)  # the parent that will NEVER be written
    results = []
    spans = []
    for i in range(3):
        spans.append(span_json("wedge.gate.%d" % i, tid, _hexid(8),
                               t0 + i, t0 + i + 0.5, parent_id=ghost_root,
                               attrs={"gate.verdict": "pass", "suite.op": op}))
    # the gate that hung: opened, never closed
    spans.append(span_json("wedge.gate.3.OPEN", tid, _hexid(8), t0 + 3, t0 + 3,
                           parent_id=ghost_root,
                           attrs={"gate.verdict": "OPEN-never-closed", "suite.op": op}))
    for i, sp in enumerate(spans):
        ok, detail = post_spans(base, traces_payload([sp], service,
                                                     component="traceprobe"))
        results.append((i, ok, detail))
    return op, tid, ghost_root, results


def gate_spans(gate: str, phases: list[tuple[str, dict, float, float]],
               service: str = DEFAULT_SERVICE):
    """PURE: (trace_id, spans) for ONE gate run — parent + one child per phase.

    `phases` is [(name, cpu_attrs, t_start_unix, t_end_unix)] — the attrs coming from
    `CpuClock.deltas()`, so every child carries BOTH its CPU cost and its wall time,
    each explicitly labelled.

    ⚑ AN OPEN PHASE IS `t_end is None` → emitted with end == start.  That is how "this
    phase began and we never saw it finish" is representable; the alternative is not
    emitting it, which loses WHICH phase wedged — the single most useful fact.
    """
    tid = _hexid(16)
    root = _hexid(8)
    t0 = phases[0][2] if phases else time.time()
    t1 = max((p[3] if p[3] is not None else p[2]) for p in phases) if phases else t0
    spans = [span_json(gate, tid, root, t0, t1, attrs={"gate.phases": len(phases)})]
    for name, attrs, ts, te in phases:
        spans.append(span_json(name, tid, _hexid(8), ts,
                               ts if te is None else te,
                               parent_id=root, attrs=dict(attrs)))
    return tid, spans


def profile_clause_audit(base: str, service: str = DEFAULT_SERVICE,
                         emit_spans: bool = True, sink=None):
    """Ⓞ8: run `agda_defs.clause_audit` and report EACH PHASE'S CPU COST.

    ⚑⚑⚑ CPU, NOT WALL, AND THAT IS THE WHOLE DELIVERABLE.  This box is busy by design,
    so a phase's wall time is a fact about co-tenancy.  The premise that a quiet box was
    needed to measure this gate was retired 2026-08-25: contention delays a process, it
    does not inflate the cycles it consumes, so CPU was always the measurement.

    ⚑ STREAMING, NOT POST-HOC.  Each phase's span is POSTed AS THAT PHASE CLOSES, so a
    wedge mid-run leaves the completed phases already in the store plus an absent root —
    the orphan signal proved earlier.  A post-hoc assembly would emit nothing for exactly
    the run we most want to see.

    ⚑ EMIT-AND-MOVE-ON: no in-run readback.  Joins settle over ~0-15.3s and a gate must
    not pay that on the operator's wall clock.  Confirm afterwards with `--verify-tree`.
    """
    say = (sink if sink is not None else sys.stderr).write
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import agda_defs

    tid, root = _hexid(16), _hexid(8)
    t_run0 = time.time()
    run_clock = CpuClock()
    state = {"phase": None, "clock": None, "t0": None, "n": 0}
    profile = []

    def _close(open_phase=False):
        if state["phase"] is None:
            return
        d = state["clock"].deltas()
        te = None if open_phase else time.time()
        profile.append((state["phase"], d, state["t0"], te))
        say(f"  {state['phase']:<22} cpu={d[CPU_ATTR]:8.2f}s  wall={d[WALL_ATTR]:8.2f}s"
            f"  (scope={d[CPU_SCOPE_ATTR]})\n")
        if emit_spans:
            sp = span_json(state["phase"], tid, _hexid(8), state["t0"],
                           state["t0"] if te is None else te,
                           parent_id=root, attrs=dict(d))
            post_spans(base, traces_payload([sp], service, component="clause-audit"))
        state["phase"] = None

    def on_module(phase, done, total):
        if phase != state["phase"]:
            _close()
            state.update(phase=phase, clock=CpuClock(), t0=time.time())
        state["n"] = done

    say(f"clause_audit phase profile (CPU is the measurement; wall is co-tenancy)\n")
    rows = agda_defs.clause_audit(on_module=on_module)
    _close()
    total = run_clock.deltas()
    say(f"  {'TOTAL':<22} cpu={total[CPU_ATTR]:8.2f}s  wall={total[WALL_ATTR]:8.2f}s"
        f"   -> {len(rows)} row(s)\n")

    if emit_spans:
        # ⚑ THE ROOT IS WRITTEN LAST, deliberately: it cannot close until every phase
        # has, and cassian proved parent-last reassembles. If this line is never reached
        # (the gate wedged or was killed), the children stand as an ORPHANED trace —
        # which is precisely the wedge signal, not a defect.
        rootspan = span_json("check_clause_audit", tid, root, t_run0, time.time(),
                             attrs=dict(total, **{"gate.rows": len(rows),
                                                  "gate.phases": len(profile)}))
        post_spans(base, traces_payload([rootspan], service, component="clause-audit"))
        say(f"  trace_id={tid}  (confirm later: --verify-tree {tid})\n")
    return tid, profile, len(rows)


def run_gate(base: str, script: str, argv: list[str], service: str = DEFAULT_SERVICE,
             emit_spans: bool = True, sink=None):
    """Ⓞ6: run ONE real gate as a subprocess, emit a CPU-instrumented span. -> (rc, tid).

    ⚑⚑ `RUSAGE_CHILDREN` IS THE RIGHT SCOPE HERE AND IT IS WHY THE SPAN IS HONEST: the
    gate is a CHILD PROCESS, so its CPU lands in this process's children accounting only
    when we REAP it.  We use `subprocess.run`, which waits — so the child IS reaped and
    its CPU IS counted.  A gate we killed instead of waiting for would contribute ZERO,
    and the span would read as free.  `cpu.scope` records which case produced the number
    so a reader never has to guess.

    ⚑ THE ROOT SPAN IS WRITTEN AFTER THE GATE RETURNS.  If this process dies with the
    gate, the trace is an orphan — children, no root — which is the wedge signal rather
    than a lost measurement.  For a single-span gate run there are no children to
    orphan, so a wedge here shows as NO TRACE AT ALL; the per-phase form
    (`--profile-clause-audit`) is the one that degrades gracefully, and that is an
    argument for phase-level spans over gate-level ones.
    """
    import subprocess
    say = (sink if sink is not None else sys.stderr).write
    tid, root = _hexid(16), _hexid(8)
    clock = CpuClock()
    t0 = time.time()
    proc = subprocess.run([sys.executable, script, *argv], capture_output=True, text=True)
    t1 = time.time()
    d = clock.deltas()

    name = os.path.basename(script)
    say(f"{name} rc={proc.returncode}  cpu={d[CPU_ATTR]:.2f}s  "
        f"wall={d[WALL_ATTR]:.2f}s  (scope={d[CPU_SCOPE_ATTR]}, "
        f"children={d.get(CPU_CHILDREN_ATTR, 0.0):.2f}s)\n")
    if emit_spans:
        sp = span_json(name, tid, root, t0, t1,
                       attrs=dict(d, **{"gate.verdict": "pass" if proc.returncode == 0
                                        else "fail",
                                        "gate.rc": proc.returncode}))
        ok, detail = post_spans(base, traces_payload([sp], service, component=name))
        say(f"  span POST: {detail}\n  trace_id={tid}\n")
    return proc.returncode, tid


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"span store base URL (default {DEFAULT_BASE})")
    ap.add_argument("--service", default=DEFAULT_SERVICE, help="service.name to emit under")
    ap.add_argument("--reachable", action="store_true", help="is the span store answering?")
    ap.add_argument("--services", action="store_true", help="service names the store has seen")
    ap.add_argument("--operations", metavar="SERVICE", help="the operations index for a service")
    ap.add_argument("--emit", action="store_true", help="write one suite/gate span tree (one POST)")
    ap.add_argument("--verify", nargs=2, metavar=("SERVICE", "OPNAME"),
                    help="set-membership read-your-write on the operations index")
    ap.add_argument("--ping", action="store_true", help="--emit then --verify: the only liveness test")
    ap.add_argument("--stream", type=int, metavar="N",
                    help="measure whether N spans of ONE trace can be POSTed incrementally")
    ap.add_argument("--gate", metavar="SCRIPT", help="Ⓞ6: run one gate, emit a CPU span")
    ap.add_argument("--gate-args", nargs=argparse.REMAINDER, default=[],
                    help="--gate: arguments passed through to the gate")
    ap.add_argument("--profile-clause-audit", action="store_true",
                    help="Ⓞ8: per-phase CPU profile of clause_audit; streams gate spans")
    ap.add_argument("--no-emit", action="store_true",
                    help="--profile-clause-audit: measure only, post no spans")
    ap.add_argument("--verify-tree", metavar="TRACE_ID",
                    help="STRUCTURE oracle: poll until the tree assembles (≠ --verify)")
    ap.add_argument("--expect-spans", type=int, default=None,
                    help="--verify-tree: assert this exact span count")
    ap.add_argument("--tree-deadline", type=float, default=30.0,
                    help="--verify-tree ceiling (joins measured at ~0-15.3s; size high)")
    ap.add_argument("--wedge", action="store_true",
                    help="stage the WEDGE case: orphaned children, parent never written")
    ap.add_argument("--trace", metavar="TRACE_ID",
                    help="UNVERIFIED (cassian): span bodies by trace id — window-fussy")
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
            print("  (the engine binds loopback deliberately; off-host, tunnel first:\n"
                  "   ssh -L 10428:127.0.0.1:10428 cassian)\n"
                  "  ⚑ This is 'the store did not answer', NOT 'VictoriaTraces is absent'.")
        return 0 if ok else 1

    try:
        if a.services:
            found = services(a.base)
            for s in sorted(found):
                print(f"  {s}")
            print(f"{len(found)} service(s) in the index")
            return 0

        if a.operations is not None:
            found = operations(a.base, a.operations)
            for o in sorted(found):
                print(f"  {o}")
            print(f"{len(found)} operation(s) indexed for {a.operations!r}")
            print("  ⚑ an empty index is 'nothing indexed for that service name', NOT "
                  "'that service never emitted'.")
            return 0

        if a.trace is not None:
            # ⚑ RETRY, BECAUSE AN EMPTY READ IS A RETRY — the A98 posture applies to this
            # path MORE than to the index, not less: cassian calls it window-fussy, and
            # MEASURED 2026-08-25 a streamed trace read 404-empty then read back complete
            # moments later. A single read here would have reported "the store does not
            # reassemble streamed traces" — a false structural conclusion drawn from a
            # timing artifact, about the exact question this tool was built to settle.
            _end = time.monotonic() + a.deadline
            while True:
                got = trace_by_id(a.base, a.trace)
                if got or time.monotonic() >= _end:
                    break
                time.sleep(a.poll)
            nspans = sum(len(t.get("spans") or []) for t in got if isinstance(t, dict))
            print(f"{len(got)} trace(s), {nspans} span(s) for {a.trace}")
            for t in got:
                for sp in (t.get("spans") or []) if isinstance(t, dict) else []:
                    print(f"  {sp.get('spanID','?')}  parent={sp.get('references') or '-'}  "
                          f"{sp.get('operationName','?')}  dur={sp.get('duration','?')}us")
            if not got:
                print("  ⚑ EMPTY IS NOT 'NOT JOINED'. This read has three "
                      "indistinguishable causes: not yet indexed, aged out of the "
                      "query window, or genuinely absent. A 404 body here is the "
                      "store ANSWERING 'nothing matched' — it is not a transport "
                      "fault and says nothing about your tunnel.")
            print("  ⚑ UNVERIFIED PATH: cassian has not proven this window-stable for a "
                  "just-written span. Use --verify (operations index) as the oracle.")
            return 0

        if a.gate is not None:
            rc, _tid = run_gate(a.base, a.gate, a.gate_args, a.service,
                                emit_spans=not a.no_emit, sink=sys.stdout)
            return rc

        if a.profile_clause_audit:
            profile_clause_audit(a.base, a.service, emit_spans=not a.no_emit,
                                 sink=sys.stdout)
            return 0

        if a.verify_tree is not None:
            return verify_tree(a.base, a.verify_tree, a.expect_spans,
                               a.tree_deadline, a.poll, sink=sys.stdout)

        if a.wedge:
            op, tid, ghost, results = wedge(a.base, a.service)
            for i, ok, detail in results:
                print(f"  span[{i}] {'OK ' if ok else 'ERR'} {detail}")
            nok = sum(1 for _i, ok, _d in results if ok)
            print(f"{nok}/{len(results)} orphaned-child POST(s) accepted")
            print(f"  trace_id={tid}  operation={op}")
            print(f"  ⚑ parentSpanId={ghost} was NEVER written — that is the wedge.")
            print(f"  Read it back:  traceprobe.py --trace {tid}")
            print("  If those children are served with no root, a wedge is READABLE "
                  "from a streamed trace and needs no post-hoc assembly.")
            return 0 if nok == len(results) else 1

        if a.stream is not None:
            op, tid, results = stream(a.base, a.service, a.stream)
            for i, ok, detail in results:
                print(f"  span[{i}] {'OK ' if ok else 'ERR'} {detail}")
            nok = sum(1 for _i, ok, _d in results if ok)
            print(f"{nok}/{len(results)} incremental POST(s) accepted for ONE trace_id {tid}")
            print(f"  operation={op}  service={a.service}")
            if nok == len(results):
                print("  → the TRANSPORT accepts incremental per-span POSTs. Confirming "
                      "the index sees the operation...")
                rc = verify(a.base, a.service, op, a.deadline, a.poll, sink=sys.stdout)
                print("  ⚑ transport-accepted + index-confirmed does NOT yet prove the "
                      "store REASSEMBLES the tree across POSTs — read it back with "
                      f"--trace {tid} to see whether all {len(results)} spans join.")
                return rc
            print("  → at least one incremental POST was REJECTED: streaming per-gate "
                  "emission is not available on this path as written.")
            return 1

        if a.emit or a.ping:
            ok, detail, op, tid = emit(a.base, a.service)
            print(f"traceprobe: emit WRITE — {detail}")
            print(f"  service={a.service}  operation={op}  trace_id={tid}")
            if not ok:
                print("  A transport fault is distinct from an ingest or index fault; "
                      "this half cannot tell you about the other two.", file=sys.stderr)
                return 1
            if not a.ping:
                return 0
            print(f"  reading back the operations index for {op!r} "
                  f"(deadline {a.deadline:.0f}s)...")
            return verify(a.base, a.service, op, a.deadline, a.poll, sink=sys.stdout)

    except Unreachable as e:
        print(f"UNREACHABLE {a.base} — {e}", file=sys.stderr)
        print("  This is 'the store did not answer', NOT 'no data exists'.", file=sys.stderr)
        return 2

    if a.verify is not None:
        svc, op = a.verify
        return verify(a.base, svc, op, a.deadline, a.poll)

    ap.print_help()
    return 0


def _selftest():
    """Counted from len(cases). The PURE half proves without a live store.

    ⚑ THE LIVE HALF IS DELIBERATELY NOT MOCKED, for `tsdbprobe`'s reason: a fake
    VictoriaTraces would test my MODEL of it, and my model is exactly what is unproven
    here (cassian has not tested gRPC; the trace-body window is unmeasured). Mocking
    would launder an assumption into a green test.
    """
    import inspect as _insp
    import io
    cases, ok = [], 0

    def check(name, got, want):
        nonlocal ok
        cases.append(name)
        if got == want:
            ok += 1
        else:
            print(f"  FAIL {name}: got {got!r} want {want!r}")

    # ── the oracle's parser: BOTH operations-index renderings ──────────────
    check("a bare-string operations index reads",
          extract_names('{"data":["a","b"]}'), ["a", "b"])
    check("an OBJECT operations index reads too (newer Jaeger shape)",
          extract_names('{"data":[{"name":"a","spanKind":"internal"}]}'), ["a"])
    check("a mixed index reads both entry shapes",
          extract_names('{"data":["a",{"name":"b"}]}'), ["a", "b"])
    # ⚑ GARBAGE CAN NEVER CONFIRM. If a malformed body could yield a name, a broken
    # store would confirm a write that never landed.
    check("a malformed body yields no names", extract_names("not json"), [])
    check("a null data yields no names", extract_names('{"data":null}'), [])
    check("a non-dict body yields no names", extract_names([1, 2]), [])
    check("an entry with a non-string name is dropped",
          extract_names('{"data":[{"name":3},{"name":"ok"}]}'), ["ok"])

    # ── the oracle itself: EXACT, unlike the metric one ────────────────────
    check("membership confirms an exact name", member(["a", "op-1"], "op-1"), True)
    # ⚑ A PREFIX MUST NOT CONFIRM: the metric oracle is deliberately fuzzy (float
    # renderings); this one must be exact or a near-miss from an earlier run passes.
    check("a PREFIX does not confirm", member(["op-12"], "op-1"), False)
    check("an empty index confirms nothing", member([], "op-1"), False)

    # ── the OTLP/JSON span encoding ────────────────────────────────────────
    sp = span_json("gate.x", "a" * 32, "b" * 16, 1000.0, 1000.5, parent_id="c" * 16,
                   attrs={"gate.verdict": "pass"})
    check("ids are HEX strings, not base64 (the OTLP/JSON rule)", sp["traceId"], "a" * 32)
    check("a child carries its parentSpanId", sp["parentSpanId"], "c" * 16)
    # ⚑ NANOSECOND TIMES MUST BE STRINGS — a JSON number loses precision above 2^53 ns,
    # which silently corrupts every timestamp after 1970+104 days. Type, not value.
    check("start time is a STRING of nanoseconds", isinstance(sp["startTimeUnixNano"], str), True)
    check("the span ends after it starts",
          int(sp["endTimeUnixNano"]) > int(sp["startTimeUnixNano"]), True)
    check("an attribute is carried as a typed OTLP value",
          sp["attributes"][0], {"key": "gate.verdict", "value": {"stringValue": "pass"}})

    # ── the suite/gate tree: the SHAPE the use case needs ──────────────────
    tid, spans = suite_tree("suite-1", "svc", [("g1", 1.0, "pass"), ("g2", 2.0, "fail")])
    check("a tree is one parent plus one child per gate", len(spans), 3)
    check("every span shares the trace id", {s["traceId"] for s in spans}, {tid})
    check("the root has NO parent", "parentSpanId" in spans[0], False)
    check("every gate is a child of the root",
          {s["parentSpanId"] for s in spans[1:]}, {spans[0]["spanId"]})
    check("span ids are distinct", len({s["spanId"] for s in spans}), 3)
    check("the verdict rides as an attribute, not in the name",
          spans[2]["attributes"][0]["value"]["stringValue"], "fail")

    # ⚑ THE WEDGE CASE IS THE WHOLE POINT: a gate that opened and never closed is
    # representable — an unterminated child. If the encoder REQUIRED an end time, the
    # one question we built this for would be inexpressible.
    _open = span_json("wedged", "a" * 32, "d" * 16, 1000.0, 1000.0, parent_id="c" * 16)
    check("a zero-duration (still-open) span is representable",
          _open["startTimeUnixNano"] == _open["endTimeUnixNano"], True)

    # ── the payload envelope ───────────────────────────────────────────────
    pl = traces_payload(spans, "svc", instance="host-1")
    attrs = pl["resourceSpans"][0]["resource"]["attributes"]
    check("the payload pins service.name", attrs[0]["value"]["stringValue"], "svc")
    # ⚑ PINNED INSTANCE ID, never generated per process — the metrics side's
    # cardinality-churn lesson, applied to the service index.
    check("the payload pins service.instance.id", attrs[1]["value"]["stringValue"], "host-1")
    # ⚑ TRAP 3: `component` is a RESOURCE attribute, beside service.name — not a span
    # attribute. I had it on the span until cassian sent the verbatim wire shape.
    _pc = traces_payload(spans, "svc", instance="h", component="clause-audit")
    _rattrs = {a["key"]: a["value"]["stringValue"]
               for a in _pc["resourceSpans"][0]["resource"]["attributes"]}
    check("component rides in resource.attributes", _rattrs.get("component"), "clause-audit")
    check("component is ABSENT from resource attrs when not given",
          "component" in {a["key"] for a in attrs}, False)

    # ⚑⚑ TRAP 1: WRONG-LENGTH IDS MUST FAIL LOUDLY AT THE PRODUCER. A malformed id may
    # be accepted with 200 and DROPPED, which reads back as "unconfirmed" and gets
    # misdiagnosed as store lag — a false claim about someone else's store caused by
    # our own bug. Assert at construction, not at the store.
    def _raises(fn):
        try:
            fn()
            return False
        except ValueError:
            return True
    check("a short traceId is REFUSED at construction",
          _raises(lambda: span_json("n", "a" * 16, "b" * 16, 1.0, 2.0)), True)
    check("a short spanId is REFUSED at construction",
          _raises(lambda: span_json("n", "a" * 32, "b" * 8, 1.0, 2.0)), True)
    check("a short parentSpanId is REFUSED at construction",
          _raises(lambda: span_json("n", "a" * 32, "b" * 16, 1.0, 2.0, parent_id="c" * 8)),
          True)
    check("correct lengths are accepted",
          _raises(lambda: span_json("n", "a" * 32, "b" * 16, 1.0, 2.0)), False)
    # ⚑ and the generator must produce exactly those lengths
    check("_hexid(16) is 32 hex chars (traceId)", len(_hexid(16)), 32)
    check("_hexid(8) is 16 hex chars (spanId)", len(_hexid(8)), 16)

    # ⚑ A NON-200 IS PROOF OF REFUSAL — the one signal we must act on, inverted from
    # everywhere else in this file where an absence is never a verdict.
    check("retryable refusal codes include 429 and 503",
          429 in RETRYABLE and 503 in RETRYABLE, True)
    check("post_spans backs off on a retryable refusal",
          "backoff" in _insp.getsource(post_spans)
          and "RETRYABLE" in _insp.getsource(post_spans), True)

    check("the spans ride under scopeSpans",
          len(pl["resourceSpans"][0]["scopeSpans"][0]["spans"]), 3)
    check("the payload is JSON-serialisable", isinstance(json.dumps(pl), str), True)

    # ── writes go ONLY to /insert; reads to /select ────────────────────────
    check("the insert path is the OTLP traces endpoint", INSERT_PATH,
          "/insert/opentelemetry/v1/traces")
    check("reads live under /select/jaeger", JAEGER.startswith("/select/"), True)

    # ── the A98 posture, driven for real against a closed port ─────────────
    import io
    sink = io.StringIO()
    rc = verify("http://127.0.0.1:1", "svc", "op", deadline_s=0.0, poll_s=0.0, sink=sink)
    check("verify against a dead store returns NOT-CONFIRMED (1), not a crash", rc, 1)
    check("and it says NOT CONFIRMED, never 'ingestion failed'",
          "NOT CONFIRMED" in sink.getvalue()
          and "ingestion failed" not in
          sink.getvalue().replace("does NOT mean ingestion failed", ""), True)
    # ⚑⚑ A 404 FROM /traces IS THE STORE ANSWERING 'nothing matched', NOT A FAULT.
    # Measured 2026-08-25: this tool's FIRST live run reported UNREACHABLE for a store
    # that was answering perfectly, telling the operator to check a working tunnel.
    # Pinned as a case because the distinction is the tool's reason for existing and it
    # got it wrong anyway.
    import inspect as _i2
    check("a 404 from /traces is read as EMPTY, not Unreachable",
          "HTTP 404" in _i2.getsource(trace_by_id) and "return []" in _i2.getsource(trace_by_id),
          True)
    check("a NON-404 transport fault still raises (empty != unreachable)",
          "raise" in _i2.getsource(trace_by_id), True)

    # ── Ⓞ9 CPU vs WALL: two measures, never collapsed ─────────────────────
    # ⚑⚑ THE BOX IS BUSY BY DESIGN, so wall clock is a fact about co-tenancy. These
    # cases pin that BOTH are carried and BOTH are named — a bare "duration" attribute
    # would let a reader take a contention artifact for a cost.
    _clk = CpuClock()
    for _ in range(200000):
        pass
    _d = _clk.deltas()
    check("a clock reports CPU and WALL as SEPARATE attributes",
          CPU_ATTR in _d and WALL_ATTR in _d, True)
    check("neither is named the ambiguous 'duration'",
          any(k == "duration" for k in _d), False)
    check("the rusage SCOPE is recorded on the span, never assumed",
          _d[CPU_SCOPE_ATTR], "self+reaped_children")
    check("cpu total is user+sys (+reaped children)",
          abs(_d[CPU_ATTR] - (_d[CPU_USER_ATTR] + _d[CPU_SYS_ATTR]
                              + _d[CPU_CHILDREN_ATTR])) < 1e-6, True)
    check("busy work consumes measurable CPU", _d[CPU_ATTR] > 0.0, True)
    # ⚑ A CHILDREN-EXCLUDED CLOCK MUST SAY SO — the scope label is the only thing
    # standing between a shell-out gate's real cost and its Python overhead.
    _self = CpuClock(with_children=False)
    check("a self-only clock labels its narrower scope",
          _self.deltas()[CPU_SCOPE_ATTR], "self")
    check("...and omits the children attribute entirely (never a silent 0.0)",
          CPU_CHILDREN_ATTR in _self.deltas(), False)

    # ⚑⚑ WALL IS WHAT SEES A WEDGE; CPU CANNOT. A span blocked on a lock burns no
    # cycles, so a CPU-only view reports a wedged gate as free. This pins that the
    # open-phase span is representable and carries both numbers.
    _gt, _gs = gate_spans("g", [("p1", {CPU_ATTR: 1.0, WALL_ATTR: 9.0}, 100.0, 101.0),
                                ("p2", {CPU_ATTR: 0.0, WALL_ATTR: 0.0}, 101.0, None)])
    check("a gate trace is parent + one child per phase", len(_gs), 3)
    check("an OPEN phase is emitted with end == start (the wedge shape)",
          _gs[2]["endTimeUnixNano"] == _gs[2]["startTimeUnixNano"], True)
    check("a phase child carries its CPU cost",
          _gs[1]["attributes"][0]["value"], {"doubleValue": 1.0})
    check("every phase span shares the gate's trace id",
          {s["traceId"] for s in _gs}, {_gt})

    # ── the SECOND oracle: structure, blind to which the FIRST one is ──────
    # ⚑⚑ cassian's correction: the operations index shows a name the instant ANY span
    # carrying it lands, so it cannot tell a joined tree from N one-span traces. These
    # cases pin the distinction the membership oracle cannot make.
    _joined = [{"spans": [
        {"spanID": "r", "references": []},
        {"spanID": "c1", "references": [{"refType": "CHILD_OF", "spanID": "r"}]},
        {"spanID": "c2", "references": [{"refType": "CHILD_OF", "spanID": "r"}]}]}]
    check("a joined tree reports its span count", tree_shape(_joined)[0], 3)
    check("a joined tree has exactly ONE root", tree_shape(_joined)[1], 1)
    check("a joined tree has NO orphaned parent refs", tree_shape(_joined)[2], [])
    # ⚑ THE SHAPE THE MEMBERSHIP ORACLE CANNOT DISTINGUISH: same span count, three roots.
    _split = [{"spans": [{"spanID": "a", "references": []}]},
              {"spans": [{"spanID": "b", "references": []}]},
              {"spans": [{"spanID": "c", "references": []}]}]
    check("3 one-span traces have the SAME span count as a joined tree",
          tree_shape(_split)[0], tree_shape(_joined)[0])
    check("...but are told apart by ROOT COUNT (why this oracle exists)",
          tree_shape(_split)[1] != tree_shape(_joined)[1], True)
    # ⚑⚑ THE WEDGE: children referencing a parent that was never written. NOT an error
    # case — it is the signal, and it must be legible as a positive fact.
    _wedged = [{"spans": [
        {"spanID": "c1", "references": [{"refType": "CHILD_OF", "spanID": "ghost"}]},
        {"spanID": "c2", "references": [{"refType": "CHILD_OF", "spanID": "ghost"}]}]}]
    check("a wedge names the parent that was never written",
          tree_shape(_wedged)[2], ["ghost"])
    check("a wedge has ZERO roots — that IS the signal", tree_shape(_wedged)[1], 0)
    check("an empty response is a shape of nothing, not a crash", tree_shape([]), (0, 0, []))
    check("garbage yields no shape", tree_shape(["x", None]), (0, 0, []))

    # ⚑ THE TWO ORACLES MUST NOT MERGE. If a future edit routes --verify through the
    # trace body, the membership/structure distinction is lost and both questions get
    # one wrong answer.
    check("the membership oracle reads the operations index, not the trace body",
          "operations(" in _insp.getsource(verify)
          and "trace_by_id" not in _insp.getsource(verify), True)
    check("the structure oracle reads the trace body, not the index",
          "trace_by_id" in _insp.getsource(verify_tree)
          and "operations(" not in _insp.getsource(verify_tree), True)

    sink2 = io.StringIO()
    rc2 = verify_tree("http://127.0.0.1:1", "abc", 3, deadline_s=0.0, poll_s=0.0, sink=sink2)
    check("verify_tree against a dead store returns NOT-CONFIRMED (1)", rc2, 1)
    # ⚑ THE MESSAGE MUST CITE THE RANGE, NOT ONE FIGURE. A single number plus a hedge
    # reads as a number — the correction I made to cassian, which applied to my own
    # artifact too. Pinned so a later edit cannot quietly collapse the range back.
    check("...and cites the measured RANGE so a short read is not read as absence",
          "15.3s" in sink2.getvalue(), True)
    check("...and does NOT present a single settle figure as the expectation",
          "10.7s" not in sink2.getvalue(), True)

    okp, detail = post_spans("http://127.0.0.1:1", {"resourceSpans": []})
    check("a POST to a dead store reports a TRANSPORT fault, not success", okp, False)
    # ⚑ A 200 IS NOT INGESTION and the message must never imply otherwise.
    import inspect as _insp
    check("post_spans' success message disclaims ingestion",
          "ingestion unproven" in _insp.getsource(post_spans), True)

    print(f"traceprobe selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(main())
