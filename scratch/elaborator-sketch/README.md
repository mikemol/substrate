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

```
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
| `shadows`                |   88 |
| `transitions`            |   14 |
| `role_edges`             |    9 |
| `compositions`           |    4 |
| `entailments`            |    4 |
| `cross_entailments`      |   10 |
| `library_correspondence` |    7 |

Status distribution: 58 leaves, 23 productive, 4 cross-cutting, 2 research-frontier, 1 root.

## Research frontiers (where the sketch terminates honestly)

- `C3.2.1` — type-equality decision procedure (definitional equality + higher-order patterns + sized types).
- `C4.1.2` — bootstrap of the typechecker invocation when the typechecker is itself being routed through the new Γ-store.

## Why sqlite

The sketch is graph-shaped data (the shadow tree + cross-shadow entailment edges + library-discipline correspondences). Sqlite gives the same content-addressable, queryable substrate that the sketch itself proposes for Agda's `Signature` — i.e., this file is a small instance of the very architecture it describes.
