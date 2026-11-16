---
name: feedback_reuse_analysis_queries_catalog_db
description: "dedup/reuse/SPPF analysis is a QUERY over catalog.db (the event-sourced projection), never a re-intern of raw .agdai"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The reuse/dedup/SPPF-similarity analysis must be a **query over `catalog/catalog.db`** (the event-sourced
projection), NOT a re-intern of raw `.agdai` via `jea_pysim.Corpus.add_agdai`.

**Why:** catalog.db already materializes the whole SPPF — `_node` (~77k), `node_child` (~362k),
`shared_subtree` (fanin≥2, ~20k), `_unit` (18269), `unit_node` (~417k), `orbit_node`. Re-interning raw
cores duplicates all of it into a parallel, drift-prone store — and re-decoding raw interfaces is exactly
what caused the recurring "stale-core / wrong-Agda-version" failures (the shim must match the cores' Agda;
the DB projection never has that problem). The user's tell: "Isn't all of this data supposed to be in the
sqlite DB?" — and it is.

**How to apply:**
- Consumers read the DB: `scripts/sppf_query.py` (`reuse [minunits]`, `fanin`, `extract`, `clusters`),
  `reuse_tui.db_rows()`, `reuse_sweep`. head/size/instances/contains/rung all derive from
  node_child + unit_node; the consolidated-vs-dup verdict is `shared_subtree ⋈ unit_node ⋈ unit.copy`.
- **Provenance = `unit.copy`** (Agda `Definition.defCopy`, True ⟺ a module-instantiation copy): all
  instances copy ⇒ CONSOLIDATED, none ⇒ genuine DUP (independent originals sharing structure = the
  target), else MIXED. Sourced from the shim's per-defmark `copy` into `unit_obs.copy`→`_unit.copy`.
- Rebuild the projection with `python3 scripts/sppf_db.py ""` (all cores; drops+recreates the event
  tier, so schema/column changes take effect). catalog.db is gitignored/regenerable.
- Gotcha: the `node` VIEW inner-joins `kind_id`; if a rebuild predates the ⟡node-view-kindid fix
  (project_sppf's tid must intern-if-missing) the view is empty — source head from `_node` with LEFT
  JOINs (op ▸ role) to be robust.

Relates to [[similarity-not-grep]], [[jea-pysim-clusters]], [[registry-markdown]].
