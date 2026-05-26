# elaborator-sketch

Sqlite-backed persistence of the depth-4 architectural sketch for routing
Agda's `Signature` and `MetaStore` through a sequent-indexed SPPF.

The sketch was produced under the combined disciplines of
`decompose-by-entailment` and `structural-strictifier`. This directory holds
the structural content as queryable rows so future sessions can navigate by
SQL rather than by re-reading prose.

## Files

- `schema.sql` — DDL (7 tables: shadows, transitions, role_edges, compositions, entailments, cross_entailments, library_correspondence).
- `populate.sql` — INSERT statements encoding the full depth-4 sketch.
- `sketch.db` — the populated sqlite database (regeneratable from the SQL files).
- `queries.sql` — sample queries demonstrating tree walks, cross-shadow entailment retrieval, and library-discipline correspondence lookup.

## Regenerating the database

```bash
cd scratch/elaborator-sketch
rm -f sketch.db
sqlite3 sketch.db < schema.sql
sqlite3 sketch.db < populate.sql
```

## Running the sample queries

```bash
sqlite3 sketch.db < queries.sql
```

## Schema overview

The shadow tree is the spine. Every node in the sketch is one row in `shadows`:

```sql
shadows(id, parent_id, code, name, depth, cluster, status, rung, description)
```

- `code` — dotted identifier (`arch`, `C1.2.2`, `X1`, etc.)
- `depth` — 0 = root, 1 = layer-1, 2 = layer-2, 3 = layer-3, 4 = layer-4
- `cluster` — `C1`/`C2`/`C3`/`C4` for the four main clusters; `X` for cross-cutting infrastructure
- `status` — `root | productive | leaf | research-frontier | cross-cutting`
- `rung` — structural-strictifier `R(stage, kind)` header where present

Detail tables hang off shadows:

- `transitions(shadow_id, ordinal, before_state, morphism, preconditions, after_state)` — for R(reach, transitions) cells.
- `role_edges(shadow_id, source_node, role_label, target_node, target_role)` — for R(reach, graph) cells (PENMAN-shaped).
- `compositions(shadow_id, description)` — one row per shadow describing how its sub-shadows compose.
- `entailments(shadow_id, antecedent, consequent)` — per-shadow entailment claims.

Cross-cutting relationships:

- `cross_entailments(from_shadow_id, to_shadow_id, claim)` — entailment edges that span the tree.
- `library_correspondence(shadow_id, library_discipline, notes)` — maps substrate library-discipline artefacts to the implementation shadow they realise.

## Current counts

| Table                    | Rows |
|--------------------------|------|
| `shadows`                |  108 |
| `transitions`            |   65 |
| `role_edges`             |   34 |
| `compositions`           |   35 |
| `entailments`            |   35 |
| `cross_entailments`      |   15 |
| `library_correspondence` |   12 |
| `productions`            |    3 |
| `production_usages`      |   45 |
| `extraction_candidates`  |   39 |

Status distribution: 70 leaves, 31 productive, 4 cross-cutting, 2 research-frontier, 1 root.

**Clusters now include C5 (gap-detector-precision-layer).** Added in the same commit that records the depth-4 sketch of the precision sub-architecture. C5 sits between raw regex gap-detection and `C4.2.3` candidate registration; discriminates real candidates from substring false positives via three precision tiers (lexical / AST-aware / semantic). The cluster is the architectural response to the structural-strictifier finding from commit `136c901` (regex catches `cong₂` as `cong`, `sym-sum-cong` as `sym`).

Candidates distribution: 21 proposed (cong-trans: 20, sym-trans: 1), 16 done (trans-sym arc closed in `f429d6f`: 2 files; multi-production cohort migrated in `136c901`: 7 files × 2 productions = 14), 2 rejected. The trans-sym arc is closed; the sym-trans arc is one file from closure (`Cocycles/F2CubedPuncturing.agda`).

Adoption picture per production:

| Production   | Files | Total sites |
|--------------|-------|-------------|
| `cong-trans` |    20 |          98 |
| `sym-trans`  |    15 |          47 |
| `trans-sym`  |    10 |          72 |

**Coverage invariants.** Every productive and cross-cutting shadow has exactly one `compositions` and one `entailments` row. Every shadow with `rung = 'R(reach, transitions)'` has its prose-described transitions in `transitions`. Every shadow with `rung = 'R(reach, role-labeled-graphs)'` has its PENMAN edges in `role_edges`. These invariants can be checked by the queries in `queries.sql`.

## Γ-instance: the file is the architecture it sketches

The `productions` and `production_usages` tables instantiate the C1 cluster (`Γ-store`). Each row in `productions` is an actual right-rule introduction registered in the substrate library by an extraction commit; each row in `production_usages` records a left-rule call site.

Current Γ-instance: 3 productions (`cong-trans`, `sym-trans`, `trans-sym` from `Substrate.Foundation.Eq`, extracted at commit `894cd8a`); 28 usage rows across the 14 files that have adopted them. The library_correspondence rows link `C1` ↔ `productions table` and `C1.2` ↔ `production_usages table`.

This closes a structural loop: the sqlite file *is* a small Γ-store, holding the same productions whose extraction-discipline it describes in its shadow tree.

## Research frontiers (where the sketch terminates honestly)

- `C3.2.1` — type-equality decision procedure (definitional equality + higher-order patterns + sized types).
- `C4.1.2` — bootstrap of the typechecker invocation when the typechecker is itself being routed through the new Γ-store.

## Why sqlite

The sketch is graph-shaped data (the shadow tree + cross-shadow entailment edges + library-discipline correspondences). Sqlite gives the same content-addressable, queryable substrate that the sketch itself proposes for Agda's `Signature` — i.e., this file is a small instance of the very architecture it describes.
