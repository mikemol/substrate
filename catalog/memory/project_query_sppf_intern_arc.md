---
name: project_query_sppf_intern_arc
description: "live arc — intern the SQLAlchemy-Core query workload into the SPPF (same interner as .py/.agdai); derive index/materialization/data-model optima from query-orbit breadth"
metadata:
  node_type: memory
  type: project
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

A live design arc opened 2026-07-13 (user): store the project's SQLAlchemy-Core query templates in a
STRUCTURED form and **intern their expression trees into the SPPF** the same way `jea_pysim` interns `.py`
and `.agdai` cores (SQLAlchemy `ClauseElement`s are content-addressable trees). Then read SPPF orbit
structure to derive **DB-management-theoretic optima**:
- a join/filter predicate appearing across many query-orbits (high sharing-BREADTH) ⇒ an INDEX candidate
  ("breadth = relevance" from the memory mesh, recast as index priority);
- a shared subquery-orbit ⇒ a MATERIALIZATION/CSE candidate;
- orbit-equivalent query trees ⇒ canonical (cheapest) rewrite; the data model itself optimizable from the
  interned workload (AutoAdmin/index-advisor recast as SPPF-orbit analysis).

**Reuse center (not new machinery):** `jea/metalanguage/jea_pysim.py` (the SPPF interner) + the just-built
graded-orbit apparatus (`graded_orbit.py`, `_orbit_def`, orbit-key + breadth) + the catalog event-sourcing
store. Confirm `jea_pysim` can accept an externally-supplied tree before building the `ClauseElement`→tree
adapter.

**Ground-truth test:** the hand-done `path_text` VIEW→PK-indexed-table fix (2026-07-13, see
[[feedback_sql_declarative_over_materialized_enumeration]]) is exactly what ⟡index-from-orbit-breadth must
surface automatically — `path_text.path_id` is a top-breadth join predicate across the workload.

Full design + labeled threads (⟡query-template-registry, ⟡query-ast-intern, ⟡index-from-orbit-breadth,
⟡materialize-from-subquery-orbit, ⟡datamodel-from-workload) in `scratch/query_sppf_intern.md`. Relates to
[[jea-pysim-clusters]], [[wedge-projection]], [[split-idempotent-apex]], [[open-threads]].
