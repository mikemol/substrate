# LEDGERS — the project's autobiography, and the law it obeys

This repository keeps a **write-ahead record of its own construction**: a family of ledgers
that bind *intent → activity → artifact*, append-only, built to survive context loss. This
file is the index to them — the parallel, at the project scale, of
[`jea/evolution/00_SYLLABUS.md`](jea/evolution/00_SYLLABUS.md) at the module scale.

The governing observation: a ledger is the project practicing its own central law —
**never discard residue** — on its *own history*. A WAL is the eval-trace-as-SPPF of the
*building*, not the computing; same structure, one meta-level up.

## The recursive structure

A ledger is one schema — *intent → activity → artifact, append-only* — pointed in one of
**five directions**, and the five directions are the shadow-architecture skills externalized
as files on disk:

| direction | family | files | skill |
|---|---|---|---|
| **forward** — intent ⟶ artifact | WAL | [`jea/jea_unification_ledger.md`](jea/jea_unification_ledger.md), [`jea/evolution/04_engine/jea_m2_ledger.md`](jea/evolution/04_engine/jea_m2_ledger.md), [`el-atlas/wal.md`](el-atlas/wal.md), [`jea/agda-emit/4bit-WAL.md`](jea/agda-emit/4bit-WAL.md) | decomposable-by-entailment |
| **pending** — intent, not yet | NEXT | [`el-atlas/NEXT.md`](el-atlas/NEXT.md) + open obligations (OB-*) | DBE (the remainder) |
| **backward** — artifact ⟶ lesson | retrospective | [`el-atlas/retrospectives/`](el-atlas/retrospectives/), [`decomposition/cotype_retrospective.md`](decomposition/cotype_retrospective.md), [`decomposition/conversation_retrospective.md`](decomposition/conversation_retrospective.md) | the retrospective ritual |
| **sideways** — artifacts ⟶ shared shape | cotype | [`el-atlas/el-atlas-cotype.md`](el-atlas/el-atlas-cotype.md), [`el-atlas/tools/cost_cotype.py`](el-atlas/tools/cost_cotype.py), [`decomposition/cotype_decomposition.sqlite`](decomposition/), [`cotype-free-self-extending-grammar.md`](cotype-free-self-extending-grammar.md) | regroup-from-shadows / snap-to-grid |
| **inward** — external source ⟶ our claims | reading-ledger | [`el-atlas/reading-ledgers/`](el-atlas/reading-ledgers/) (`.bricks`) | DBE applied to input |

And it **recurses — the same shape at three levels**:

1. **A ledger** records one work-stream's intent→artifact (e.g. `jea_unification_ledger`'s
   `Δ-X` cells → named `jea/*.py`, with `W1…W10` witnesses and `NEXT` chains).
2. **`decomposition/` is the ledger-of-ledgers** — a SQLite (630 sections, 4157 triples,
   242 conversation turns, 1471 references) that mines the WALs + the transcript + the cotype
   into one queryable provenance graph, and emits its own retrospectives. The functor applied
   to the ledgers themselves.
3. **`agda/Substrate/ShadowArchitecture/Raven/Semantics/Cotypes.agda` + `Persistence.agda`
   prove the ledger's law** — the cotype is a *monotone preorder, deletion type-forbidden*
   (rule W5), with the Raven poem as a concrete witness of cotype-thickening. The discipline
   is formalized: the autobiography is provably append-only.

## The curriculum — read in this order, the ledgers are the autobiography

| phase | ledger(s) | what it teaches |
|---|---|---|
| **I. Read** | [`el-atlas/reading-ledgers/*.bricks`](el-atlas/reading-ledgers/) | how external sources (SYSTEM Π, the literature) were *read* and decomposed — Čech overlapping-cover bricks (H1/H2/Q1/M/Q4 + A/B gluing), typed `ACT:/OBL:/GLU:/COC:`; producer tool [`el-atlas/tools/brick-schedule.py`](el-atlas/tools/brick-schedule.py) |
| **II. Accumulate** | [`el-atlas/el-atlas-cotype.md`](el-atlas/el-atlas-cotype.md) | the structural vocabulary that accumulated — literature-adjacency shadows (`S-A`…`S-H`: bilattices, evidence logic, tropical, Shannon duality, sheaf contextuality, …) and the honest self-corrections (`DRIFT-1…5`, kept not deleted) |
| **III. Build · instrument** | [`el-atlas/wal.md`](el-atlas/wal.md), [`el-atlas/NEXT.md`](el-atlas/NEXT.md) | how accumulated structure became the el-atlas instrument — 22 moves (`W1…W22`) with `BEGIN/END`, `pre=/head=` shas, named `tools/` pilots + `proofs/*.agda` |
| **IV. Build · evaluator** | [`jea/jea_unification_ledger.md`](jea/jea_unification_ledger.md), [`jea/evolution/04_engine/jea_m2_ledger.md`](jea/evolution/04_engine/jea_m2_ledger.md), [`jea/agda-emit/4bit-WAL.md`](jea/agda-emit/4bit-WAL.md) | how el-atlas became the GPU evaluator — the `Δ-X` coordinate→geometry arc → `jea/*.py`; the `M2a…M2d` milestone bricks; the `4bit-WAL` premortem (judgment discipline before code) |
| **V. Reflect** | [`el-atlas/retrospectives/`](el-atlas/retrospectives/) | the after-action reviews that fed corrections back — the ten-gate ritual (`G0…G9`) on a specific fault, decorrelation to fixpoint |
| **VI. Compile** | [`decomposition/`](decomposition/) | the whole thing mined into a queryable provenance DB + onboarding retrospectives — *read this first to onboard* ([README](decomposition/README.md)) |
| **VII. Prove** | [`Cotypes.agda`](agda/Substrate/ShadowArchitecture/Raven/Semantics/Cotypes.agda), [`Persistence.agda`](agda/Substrate/ShadowArchitecture/Persistence.agda) | the law itself — the cotype's no-deletion monotonicity, type-enforced |

## Per-ledger reference

Legend — **role**: `spine` (teaches the build story) · `index` (maps things) · `certificate`
(records completion, no narrative).

| ledger | direction | one entry is… | link quality | status | role |
|---|---|---|---|---|---|
| `jea/jea_unification_ledger.md` | WAL | a `Δ-X` cell: intent + `W1…W10` witnesses + named artifact + honest scope + `NEXT` | explicit | live + frozen | **spine** |
| `el-atlas/wal.md` | WAL | `BEGIN/END <tag>`: intent, expected + actual artifacts, `pre=/head=` shas | explicit | live | **spine** |
| `el-atlas/el-atlas-cotype.md` | cotype | `S-x` shadow: shared-structure / imports / exports / generates + a 3-bit signature | explicit + literature | live | **spine** (glossary) |
| `el-atlas/reading-ledgers/*.bricks` | reading | a brick: line-range + state + `ACT:/OBL:/GLU:/COC:` | explicit (→ `S-`/`B-` claims) | live | **spine** (method) |
| `decomposition/` suite | ledger-of-ledgers | a triple `(section, subject, predicate, object)` line-anchored to source | explicit + queryable | live | **spine** (meta) |
| `el-atlas/retrospectives/*.md` | retrospective | a gate `G0…G9` finding with commit shas | explicit (internal) | live / awaiting-fix | **spine** (method) |
| `jea/agda-emit/4bit-WAL.md` | WAL (premortem) | a shadow / plan-gate `P1…P4`, design-time | design-time | live study | **spine** (judgment) |
| `jea/evolution/04_engine/jea_m2_ledger.md` | WAL | an `M2x` brick → reference script + production twin | explicit | homed (Λ1 ✅) | index |
| `el-atlas/NEXT.md` | NEXT | a numbered opening move + state snapshot | current header + W15-frozen State | live (Λ3 ✅ banner) | index |
| `el-atlas/tools/ai_ledger.md` | WAL | an `AI-N` item → tool file + finding | outcome-indexed | closed-record (Λ4 ✅ labeled) | **certificate** |
| `cotype-free-self-extending-grammar.md` | cotype | a `Move M1…M41` with shadows + probe-state | explicit | live, **bifurcated** (see cracks) | spine, then crisis-journal |

## Known cracks (kept visible, not hidden)

An honest index records where the record itself is imperfect:

1. ✅ **CLOSED (Λ1, L0)** — `jea/evolution/04_engine/jea_m2_ledger.md`: the orphan was `git mv`'d out
   of `scripts/` to sit beside the `M2a…M2d` scripts it documents.
2. ✅ **CLOSED (Λ2, L0)** — the exact-MD5 duplicate `scratch/cotype-free-self-extending-grammar (16).md`
   was deleted; the root copy (the one `decomposition/` ingests) is now the single canonical.
3. ✅ **ADDRESSED (Λ4, L0)** — `el-atlas/tools/ai_ledger.md` is now labeled for what it is: a CLOSED
   completion certificate (outcome-indexed; cite the finding for the *why*), not a live worklist.
4. ✅ **ADDRESSED (Λ3, L0)** — `el-atlas/NEXT.md`'s stale `W15` State block now carries a FROZEN/STALE
   banner pointing to `wal.md` W16–W23 for current state.
5. **The cotype-grammar is bifurcated at `M33`** (OPEN — Λ5) — the design ledger claims 9
   `V₄`-twin cells; observation found 4 inhabited. The repair (`M34…M41 v22`) lives *only in the
   cotype*; `scratch/chart.py` and the Agda side were never re-synced. Unlike jea's `fit_plant`
   (an honestly-closed dead-end), this one is still *claiming*.
6. **`decomposition/` covers only the SPPF/grammar arc** (OPEN — Λ6) — the 242-turn design conversation
   + the grammar; the later el-atlas and jea arcs are not yet in the DB. The autobiography's
   meta-layer stops two chapters short.

## How to onboard

1. [`decomposition/README.md`](decomposition/README.md) — the mechanical provenance layer + how
   to refresh it.
2. [`decomposition/cotype_retrospective.md`](decomposition/cotype_retrospective.md) — the move
   chronology (M1…M41) with axis signatures.
3. This file's **curriculum** table — walk the seven phases.
4. For any single arc, open its WAL and follow the `NEXT`/witness chains to the named artifacts.
