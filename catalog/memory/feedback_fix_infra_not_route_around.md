---
name: feedback_fix_infra_not_route_around
description: "a slow/awkward SHARED infra module is fixed AT THE SOURCE (lazy its truly-optional deps; cache its expensive compilation) — NEVER routed around per-consumer (lazy-import in the caller / raw-SQL to dodge the query layer / avoid-the-import), which creates SPRAWL"
metadata:
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When a shared infrastructure module is slow or awkward (a heavy import, an expensive
compile step), fix it AT THE SOURCE so every consumer benefits from one change. Do NOT
work around it in each consumer — that is SPRAWL, and the user named it verbatim
(2026-07-17): "These libraries are infrastructure. Fix the libraries. Do not treat them
as things to route around. That creates sprawl."

The recurring failure this session: I reached for the CONSUMER-SIDE workaround three times —
(a) a lazy `import query_builders` INSIDE sppf_db to dodge SQLAlchemy's ~0.4s import;
(b) raw `SELECT`s in the gate code to dodge the query_builders discipline;
(c) per-core-*process* ingest paying the import ×N. Each is local-optimization of the file
I was editing, not the shared library.

**Why:** the infra module has many consumers; a per-consumer workaround multiplies (N places
to maintain, each subtly different) AND leaves the root cost unfixed. The fix belongs once,
at the source: `jea_pyalg` eagerly imported `libcst` (0.2s) just to set a flag → `find_spec`
+ lazy at the 2 use sites; `jea_rigcat` eagerly imported `rig_coherence`→numpy (0.1s) →
lazy in the coherence-check methods; SQLAlchemy's ~0.4s is INHERENT to its SQL layer →
**cache the compiled queries** (query_builders = a `--compile` compiler that writes a
generated `name→SQL` .py + a runtime that executes it with no SQLAlchemy). Then the
discipline (use query_builders, no raw SQL) costs ~nothing, and per-core becomes viable.

**How to apply:** before lazy-importing / raw-SQL-ing / avoiding an infra module in a
consumer, ask "is this the LIBRARY's cost to fix?" — lazy its *truly-optional* deps IN the
library (find_spec for availability); cache its expensive compilation IN the library. The
tell = "let me lazy-import here / raw SELECT is simpler / avoid the import." Correct-by-
construction escalations built this session: the schema-version auto-migrate net (a column
add can't break the incremental path) and the compiled-query cache (runtime never imports
the compiler). Also: MEASURE the cost first (cProfile / `-X importtime`) — I theorized the
per-core overhead before measuring; the user's "cprofile it" caught it. Relates to
[[single-source-truth]], [[read-structure-dont-rebuild]], [[feedback_measure_instrument_before_theorize]].
