# ⟡query-sppf-intern — intern the SQLAlchemy-Core query workload into the SPPF; derive DB-physical-design from orbit breadth

**Origin (2026-07-13).** During ⟡argperm-full-corpus the per-def loader was slow. Chasing it produced a
chain of user corrections that generalize into an arc:
1. Engine: the graded-orbit compute was **pure Python per-item** (numpy only in the rig_coherence oracle,
   not the hot path). "We don't do one-off measurements; we frontload internments that permit multiple
   readings." → `_orbit_def` IS such an internment; frame + compute it as one.
2. "For SQL we have **SQLAlchemy Core** — prioritize that over direct query engineering."
3. "Don't pull data out of its habitat when you can **fix the habitat**." (I had materialized a view into a
   Python dict — wrong; do the join in the DB.)
4. "Constraint propagation + **batching what you query for** should make the joins cheap." — TRUE and the
   load-bearing fix: 213 per-core queries (48s) → 1 batched scan (7s). The view was NOT intrinsically slow.
5. "If the table under the view isn't **indexed properly**, that's another problem — that's why I raised
   identifying/ensuring proper indexes." — Confirmed by EXPLAIN: `path_text` (a GROUP_CONCAT VIEW) forces
   SQLite to MATERIALIZE the whole aggregation + TEMP-B-TREE on **every** join, even a single-row keyed
   join, because the join key `path_id` has no index and predicate-propagation can't push through GROUP BY.
   Fix = materialize path_text as a PK-indexed table (one `SEARCH … USING INDEX (path_id=?)`), helping the
   whole workload (every interactive node/unit-view query previously paid a full-view materialization).

**The generalization (the user's actual proposal).** Store the SQLAlchemy-Core query **templates in a
structured form** and **intern them into the SPPF** exactly as we intern Python (`jea_pysim`) and agdai
cores. SQLAlchemy-Core expressions are `ClauseElement` TREES (select / join / onclause / where-predicate /
column-access) — content-addressable the same way. Then use SPPF orbit structure to derive
**DB-management-theoretic optima**:
- **Index selection** = a column appearing as a join/filter predicate across MANY query-orbits (high
  sharing-breadth). The `path_text.path_id` join we hand-fixed would surface automatically as a
  top-breadth join predicate ⇒ index-here. "Breadth = relevance" (the MEMORY-mesh graded reading) becomes
  "breadth = index priority."
- **Materialization / denormalization** = a whole subquery-orbit (e.g. the GROUP_CONCAT of path_seg)
  shared across many readings ⇒ materialize it (a CSE over the query corpus — the same anti-unification
  autocorr_synth does for defs, applied to queries).
- **Query rewriting / data-model** = orbit-equivalent query trees with different cost ⇒ pick the canonical
  (cheapest) rep; the schema itself is optimizable from the interned workload.

**Reuse center (search before building — CLAUDE.md discipline).** This is NOT new machinery: the SPPF
interner (`jea/metalanguage/jea_pysim.py`, interns `.py` + `.agdai` → shared canonical nodes) is the center;
a `ClauseElement`→tree adapter feeds query ASTs into it. The graded-orbit apparatus just built
(`graded_orbit.py`, `_orbit_def`, orbit-key + breadth) is the analysis layer — apply it to query-orbits.
The catalog event-sourcing is the store. CONFIRM (quick) that `jea_pysim` can accept an externally-supplied
tree before building the adapter.

## Labeled threads (⟡)
- **⟡query-template-registry** — collect the project's SQLAlchemy-Core queries as named structured builders
  (not inline strings), so they are enumerable/internable. (autocorr_synth, reuse_tui, sppf_db, graded_orbit
  are the current query sites.)
- **⟡query-ast-intern** — a `ClauseElement`→SPPF-tree adapter; intern the registry via `jea_pysim`.
- **⟡index-from-orbit-breadth** — read join/filter-predicate orbit breadth → index recommendations; the
  path_text.path_id case is the ground-truth test (the tool must surface it).
- **⟡materialize-from-subquery-orbit** — shared subquery-orbits → materialization/CSE candidates.
- **⟡datamodel-from-workload** — schema/query-structure optima from the interned workload (AutoAdmin recast
  as SPPF-orbit analysis).

## RESHAPED (2026-07-13) — the breadth signal lives in VIEW DEFINITIONS (checkpoint, deferred)

Item 1 (⟡orbit-def-by-reference) + the membudget stderr fix are COMMITTED (`6714614`, full-build gate
green). ⟡query-sppf-intern was STARTED then deferred to a fresh session after a material discovery that
reshapes it — start next session from HERE, do not re-derive:

- **The 28 `path_text.path_id` joins live mostly INSIDE VIEW DEFINITIONS** (the `node` and `unit` views in
  `scripts/sppf_db.py` + `scripts/reuse_catalog.py:114-144`), NOT in the ad-hoc query strings. The ad-hoc
  queries (`sppf_query.py`, `reuse_tui.py`) join those VIEWS, which hide the path_text join one level down.
  So migrating ad-hoc SELECTs → Core would NOT surface path_text.path_id as breadth — the signal is in the
  view DDL. (Also `sppf_query.py cmd_sql` is an arbitrary-SQL passthrough — not a fixed Core builder.)
- **Coverage decision stands (user): migrate raw → Core.** But the reshaping means the FIRST, highest-value,
  lowest-risk milestone is: build `jea/metalanguage/query_registry.py` (the `ClauseLowerer` + index report)
  pointed at the **node/unit VIEW-definition SELECTs + the existing Core sites** (where the join predicates
  actually are) — proving `path_text.path_id` ranks #1 — BEFORE the broad ad-hoc-query result-equivalence
  migration (which carries less of the breadth signal and is the multi-hour part).
- Recommended next-session order: (1) `ClauseLowerer` (mirror `jea_pyalg.Lowerer`/`CstLowerer`) →
  `jea_pyalg.Intern`; register each query as a `Unit` (the ~6-line `jea_pysim.add_file:121-128` shape);
  (2) express the node/unit view SELECTs + Core sites as builders; (3) `--index-report` via
  `extract_candidates`/`fanin`, filtered to Column/Compare/Join-onclause nodes → path_text.path_id #1;
  (4) THEN migrate the ad-hoc raw SELECTs → Core for fuller coverage (result-equivalence-gated, per file).
- Ground truth unchanged: `path_text.path_id` (28 join sites) must rank #1 — the tool would have surfaced
  the hand-done `path_text` PK-index fix. `sqlglot` is NOT installed (avoid; migrate to Core instead).

## Retrospective residue (perf arc, already applied)
- `graded_orbit.preload_cores` — ONE bulk SQLAlchemy-Core scan grouped by core_id (was 213 per-core
  nested-loop queries); `Ctx(preload=True)` frontloads all cores; `preload=False` for tiny cases.
- `sppf_db.path_text` — VIEW → PK-indexed materialized table + `refresh_path_text` at the write_events
  boundary. **This is a hand-done instance of ⟡index-from-orbit-breadth** — the arc automates finding it.
- Kept honest: the batched view is only ~5% slower than the table for a SINGLE bulk query; the table's real
  win is the per-query interactive workload (no whole-view materialization). Do not overclaim the bulk delta.
