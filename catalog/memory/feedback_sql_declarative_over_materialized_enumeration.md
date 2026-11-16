---
name: feedback_sql_declarative_over_materialized_enumeration
description: "SPPF/catalog work = declarative JOINs+constraints over the materialized projection (SQLAlchemy Core), never Python graph-walks or recursive-imperative CTEs; profile before blaming the DB"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

For any counting/grouping/similarity work over the SPPF (catalog.db), think in **declarative JOINs +
constraints over the MATERIALIZED enumeration**, not Python graph-walks and not recursive-imperative CTEs.
Access layer: **SQLAlchemy Core** (the project standard now; `uv pip install SQLAlchemy`, in requirements).

**Why (the load-bound vs query-bound test):** when the "fix" is *cache the whole dataset to a pickle keyed
on DB mtime*, that's a TELL you're treating SQLite as a serialization format, not a query engine — and
usually the wrong lane. PROFILE first: time the SQL execute vs the Python-side rebuild. For catalog.db the
full load is ~2.7s (SQL 2.35 + pybuild 0.35) over 362k+77k rows — **SQLite is not the bottleneck; 440k rows
is nothing.** The bottleneck was a Python graph algorithm (skeleton-hash + N-tuple co-traversal) that
*reinvented a query engine* and timed out (2m42s). Rewritten declaratively → ~4s. Don't reach for
DuckDB/Parquet/apsw or "grow beyond SQLite" for 440k rows — that's the seductive rewrite; the boring fix
(project fewer columns, query in place, GROUP BY the materialized table) is the real one.

**How to apply (the user's rule: "you don't get to count in the SPPF without enumerating — but think like
JOIN queries and declarative constraints, not recursive-imperative behaviors"):**
- The projection ALREADY enumerated each unit's node-membership into `unit_node`. A subtree/unit SIZE is
  `GROUP BY unit_node` — count the DONE enumeration, do not re-walk it (this is the thing that was
  4.5GB/32s as a bulk Python distinct-descendant count).
- EXACT body identity = GROUP BY the `unit_node` **set-signature** (`group_concat(node_id ORDER BY
  node_id)`), NOT `_unit.root_id` — root_id is only a depth-1 packing (head + direct-child heads) and
  FALSE-clusters (verified: `+-assoc` and `Z30-multiplicities` share a root_id but have 20 vs 48 node
  sets, ∩=5).
- NEAR-dup (parameterization targets WITH holes) = a `unit_node` SELF-JOIN for shared-node-count + a
  set-difference for the holes (the `EXCEPT`/`NOT EXISTS` complement). This is the declarative form of
  anti-unification — `sppf_query.py cmd_clusters` already has the self-join overlap pattern.
- Recursive-CTE reachability from a root counts descent into the shared LIBRARY core (≈ the whole tree),
  which is both slow and semantically wrong for "body size" — avoid it; use `unit_node`.

**Batch what you query for (the per-item-repetition tell).** 2026-07-13: `graded_orbit.load_core` issued
TWO queries PER core, called 213× → ~46s (profiled as the dominant cost of a 25-min run). The queries were
individually index-served (not full scans) — the cost was the REPETITION: each per-core query re-ran the
same obs⋈event⋈terms⋈path_text join. Fix = ONE bulk scan grouped by core_id in memory (`preload_cores`,
SQLAlchemy Core): 48s → 7s. **A per-item query inside a loop is the tell** (same failure family as the
pickle-cache and the deep-recursion tells): batch the whole set in one declarative scan, group in Python.
This IS the frontload-internment discipline — we don't do one-off measurements, we compute a materialized
projection ONCE that permits many readings; `_orbit_def` is such an internment, so its build must use the
right engine (batched SQLAlchemy Core), not pure-Python per-item recursion.

**Fix the habitat; don't pull data into app code.** When a join to a slow object tempts you to materialize
it into a Python dict to "avoid the join" — STOP. Do the join in the DB; if it's slow, fix the DB
(index/materialize the object), so EVERY reading benefits, not just this loader.

**Ensure PROPER INDEXES — `EXPLAIN QUERY PLAN` is the instrument.** A `GROUP_CONCAT`/aggregate VIEW has no
index on its join key, so SQLite MATERIALIZEs the WHOLE view + a TEMP B-TREE for the GROUP BY on EVERY join
that references it — even a single-row keyed join (`WHERE k=?`), because predicate-propagation cannot push
through a GROUP BY. Confirmed 2026-07-13 for the `path_text` view (`node`/`unit` views join it): every
interactive query paid a full-view materialization. Fix = materialize as a PK-indexed table
(`refresh_path_text` at the write_events boundary) → the same join becomes one `SEARCH … USING INDEX
(path_id=?)`. **Tells in a query plan: `MATERIALIZE <view>`, `USE TEMP B-TREE`, and especially
`USING AUTOMATIC … INDEX` (SQLite building a throwaway index at query time = "you're missing an index
here").** Run EXPLAIN QUERY PLAN on hot joins; don't accept an AUTOMATIC index. Broader: index/materialization
selection should be DERIVED from the query workload — see the [[query-sppf-intern]] arc (intern the
SQLAlchemy-Core query ASTs into the SPPF; a join/filter predicate's orbit-BREADTH = its index priority; the
path_text fix is the first hand-done instance the arc would automate).

Home: `jea/metalanguage/autocorr_synth.py --agda` (the SQL-native path), `graded_orbit.preload_cores`,
`sppf_db.refresh_path_text`. Relates to [[feedback_reuse_analysis_queries_catalog_db]], [[jea-pysim-clusters]],
[[validate-outputs-inputs]], [[feedback_bound_recursion_at_self_collapse_depth]], [[query-sppf-intern]].
