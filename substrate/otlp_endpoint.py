#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve where metrics are written and read — the SPECIFIED name for write, ours for read.

⚑⚑⚑ THE COMPILED-IN ENDPOINT WAS STALE, AND IT HAD MOVED TWICE. Verified with cassian
2026-08-31 rather than assumed: `scripts/membudget_otlp.py:47-48` holds
`http://127.0.0.1:8428/...` for BOTH write and read, and `:8428` is a retired quadlet. From
their declared source (`host/store-migration.tsv`, gated by `check --only accumulators`):

    :8428              verified by substrate 2026-07-23. NOW DEAD.
    :30828  (A192)     re-pointed :8428 -> :30828, 2026-08-26
    :30828  (A206)     moved onto vmagent, 2026-08-27 — a write RELAY fanning out to
                       vm (3d raw) + vm-disk (90d aggregated)

⚑⚑ AND THE READ PORT IS A DIFFERENT SERVICE, which the old constant did not distinguish at
all. `:30828` is vmagent and serves NO PromQL; read-your-write must query `:30829` (vm-read).
A single `QUERY_BASE = ...:8428` was wrong twice over — dead host AND conflated role.

⚑⚑⚑ THE WRITE KNOB IS `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, NOT A NAME WE INVENT — and the
first draft of this module got that wrong. It minted `SUBSTRATE_OTLP_METRICS`, which is not
merely non-standard but REDUNDANT AND SHADOWING: the OpenTelemetry specification defines these
names, and `opentelemetry-python`'s `_resolve_endpoint` implements them literally —

    self._endpoint = endpoint or _resolve_endpoint(
        OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, DEFAULT_METRICS_EXPORT_PATH)

**and our emitter already uses that SDK.** `membudget_otlp.emit_gauges` constructs
`OTLPMetricExporter(endpoint=endpoint)` — and passing `endpoint=` explicitly is exactly what
DISABLES the env vars. So a compiled-in constant did not merely go stale; it turned off the
mechanism that would have let the operator re-point it without touching our code.

⚑⚑ THE PATH-SUFFIX ASYMMETRY IS SPECIFIED AND IS A FOOTGUN. The GENERAL var
(`OTEL_EXPORTER_OTLP_ENDPOINT`) is a BASE and the SDK appends `v1/metrics`; the SIGNAL var
(`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`) "MUST be used as-is without any modification". Setting
the general var to our old full-path constant would POST to `.../v1/metrics/v1/metrics`. This
module resolves the SIGNAL name, so the value carries its path.

⚑ AND THE STANDARD IS WRITE-ONLY — cassian's caveat, and it is the reason the read stays ours.
`OTEL_EXPORTER_OTLP_*` names an EXPORT endpoint; querying your own emission is not an OTel
concept, so there is no specified env for a read base. `SUBSTRATE_OTLP_QUERY` has no standard
to converge on and is not a name we chose over one.

⚑ THE COUNTER-EXAMPLE IS IN OUR OWN TREE AND THEY FLAGGED IT: `scratch/shared_cache.py:71`
hardcodes `127.0.0.1:6379` with no re-point knob, called out in their `terraform/cache.tf:95`.

⚑ VERIFICATION IS READ-YOUR-WRITE OVER THE QUERY API, and there is no shortcut: the
`vm_rows_inserted_total{type="opentelemetry"}` counter does NOT exist on this instance.
"""

from __future__ import annotations

import os

# ⚑ THE SPECIFIED NAME, honoured by every OTel SDK. Signal-specific, so it takes precedence
# over the general var and is used AS-IS including its path.
WRITE_ENV = "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"

# ⚑ THE GENERAL NAME, consulted second — a BASE with no path, per the spec. Read here so a
# host that sets only the general var still re-points us, matching SDK precedence exactly.
WRITE_ENV_BASE = "OTEL_EXPORTER_OTLP_ENDPOINT"

# The path the SDK appends to a base endpoint.
_METRICS_PATH = "v1/metrics"

# ⚑ OURS, BECAUSE THE STANDARD HAS NO READ EQUIVALENT. Kept deliberately un-derived from the
# write URL: A206 moved one service without moving the other, so any derivation would encode a
# relationship that does not hold.
READ_ENV = "SUBSTRATE_OTLP_QUERY"

# ⚑ DEFAULTS ARE THE CURRENT VALUES, VERIFIED 2026-08-31 — recorded with their date because
# they are someone else's operational parameters and WILL move again. A default is a fallback
# for a producer nobody has configured, never an authority.
DEFAULT_WRITE = "http://127.0.0.1:30828/opentelemetry/v1/metrics"
DEFAULT_READ = "http://127.0.0.1:30829"


def write_endpoint() -> str:
    """Return the OTLP metrics ingest URL, following the SDK's own precedence.

    ⚑ SIGNAL-SPECIFIC FIRST, THEN THE BASE + PATH, THEN THE VERIFIED DEFAULT. This mirrors
    `_resolve_endpoint`; a caller passing the result to `OTLPMetricExporter(endpoint=...)`
    therefore gets what the SDK would have chosen for itself.

    ⚑ THE BETTER SHAPE IS TO PASS NOTHING AT ALL and let the SDK resolve — an explicit
    `endpoint=` disables these vars. This function exists for the interim, while the emitter
    still threads an endpoint argument through three callers.
    """
    signal = os.environ.get(WRITE_ENV)
    if signal:
        return signal
    base = os.environ.get(WRITE_ENV_BASE)
    if base:
        return f"{base.removesuffix('/')}/{_METRICS_PATH}"
    return DEFAULT_WRITE


def query_base() -> str:
    """Return the PromQL read base for read-your-write verification.

    ⚑ NOT DERIVED FROM THE WRITE URL. A reader tempted to swap the port or strip the path
    would be encoding a relationship that does not hold: they are separate services, and A206
    moved one without moving the other.
    """
    return os.environ.get(READ_ENV) or DEFAULT_READ
