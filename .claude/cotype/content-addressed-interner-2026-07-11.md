# Cotype — content-addressed-interner + Set₁ mission (regrounding 2026-07-11)

Sibling of `.claude/cotype/wedge-orientation-rig-2026-07-10.md`. This file is the durable
regrounding for the interner/catalog/Set₁ arc, written under looming-compaction so the
**architecture survives outside context**. Every next-step is `⟡`-labeled for unambiguous invocation.

---

## THE ARCHITECTURE (corrected 2026-07-12 — the earlier note below the fold was BACKWARDS)

**ONE uniform scheme: base64 replaces EVERY autonumber int.** A row's id IS `base64(its UNIQUE key)`.
The only discipline: **a UNIQUE key must not be self-referentially composite** — if it references its
own table's ids compositely, it isn't normalized; move the relationships to a **bridge table** and let
the key reference the bounded base case.

| table | UNIQUE key base64 encodes | bound / note |
|---|---|---|
| **terms** | the atomic string | bounded string |
| **path_seg** (bridge) | `(path_id, ord)`→seg | `base64(qname)`, bounded |
| **_node** (SPPF **packing**) | `head ‖ child-SYMBOL-refs` | child refs = the **reentrant symbol** `base64(head)` (bounded base case, NOT the child subtree) → max id 1244, depth-independent |
| **node_child** (bridge) | `(node_id, ord, child_id)` | holds the relationships (which specific child packing) |
| **unit_node** | per-unit membership | **intern-time membership** on the acyclic original term, NOT a closure over the shared bridge |

**Why naïve base64 blew to 61 MB, and the fix.** `base64(head ‖ children)` with *children = full node
ids* is self-referentially composite → recurses through the subtree → `B=base64(arity·B)`, no bounded
fixed point (measured max 61 MB). The fix is NOT to drop children (over-collapses to 2 793 head-only
symbols; `extract` then returns only universal constructors). The fix is **normalize**: the packing's
key references children's **reentrant symbols** (`base64(head)`, bounded); the **bridge** holds which
*specific* child packing. Result: 14 913 packings, max id 1 244, **discriminating** (support median 15).
The SPPF is **reentrant** — all `Pi` share one symbol; that IS the compression, not a bug.

**The second trap: closure over a shared graph.** `support`/`unit_node` must be **membership recorded
at intern time** (acyclic original term), NOT a recursive-CTE closure over `node_child`. A shared
packing's edges conflate the children of *every* context it appears in → the closure cross-products
across units and cycles (filled the disk, 10M+ rows). Membership is bounded by term size (66 436 rows,
median 15/unit). Lifted into `jea_agdai.core_intern_agdai` as `unit_members` (Φ4c).

<details><summary>SUPERSEDED (kept as residue — it was wrong)</summary>

Earlier I wrote "two id schemes: base64 for terms, **autonumber** for nodes; base64 is impossible for
nodes." Built on the compacted summary, **backwards**. base64 IS the node id too — the "impossibility"
is only for base64-of-the-*flattened-subtree*; base64-of-the-*normalized-key* (child refs = reentrant
symbols, relationships in the bridge) is bounded and correct. User's correction: *"I never said get rid
of the table. Just the autonumber column, whose content = base64 of the UNIQUE key. If the key is
self-referentially composite, normalize — you need a bridge table."* And: *"the SPPF is supposed to be
reentrant"* — the head-sharing is the feature; I mis-measured it as over-merge, using a closure `support`
that is meaningless on a reentrant graph.
</details>

---

## REGROUNDING 2026-07-12 — the event-sourcing FIXPOINT (current; the section below is residue)

**The recursive common structure the whole arc converged to.** Every either/or this session had the SAME
shape; collapsing them recursively bottoms out in ONE invariant:

| either/or | resolved by |
|---|---|
| node id: bounded ⟂ content-addressed | (impossible at write time — pigeonhole) |
| packing: reentrant ⟂ discriminating | reentrant symbols + relationships in a bridge |
| support: closure ⟂ membership | intern-time membership (acyclic term), not closure over the shared graph |
| event key: entire-record ⟂ bounded | base64 the OBSERVATION, not the post-processed record |

The invariant under all of them: **separate the immutable, bounded OBSERVATION from the derived
STRUCTURE.** The observation is a fact (one node, bounded). Structure — the tree, global sharing, support,
the catalog — is a PROJECTION (a query), never stored at write time, never embedded in a key.
Content-address the observation (bounded); DERIVE the structure. That IS event sourcing — the fixpoint the
entire content-addressed-interner arc was groping toward. The recurring miss (5+ rounds) was
content-addressing the RESOLVED form (the tree) → unbounded; the fix each time pushed the resolution OUT
of the key. Event sourcing does it at the boundary, once. `sppf_db` writes events; SPPF is a projection;
catalog + all else are queries against the projection.

### Retrospective (G0–G9) — the event-sourcing arc
- **G2 DELTA.** Expected a bounded content-addressed id for a tree node. Actual: impossible at write time
  (measured — 61 MB Merkle, 2 793 over-collapse, 11.3× merge). Closed only when the frame moved from
  "content-address the node" to "content-address the OBSERVATION, project the node."
- **G3 CAUSE.** *root*: I repeatedly content-addressed the post-processed (child-resolved) record — the
  processing is what's unbounded; no step forced "what is the raw OBSERVATION vs its processing." The
  user's corrections ("deep is a path not a string"; "SPPF packed node IS hash-consing"; "you only need
  the observation, not post-processing") were the SAME correction at increasing depth.
- **G5 BLAMELESS.** The pipeline had no explicit OBSERVATION/PROJECTION seam; write-time interning fused
  them, so every content-address reached for the resolved form. Event sourcing installs the seam.
- **G6 SUSTAIN.** MEASUREMENT settled every round where theory spun (61 MB / 194 KB / 312 / merge-factor /
  support-explosion). Reusing jea_agdai + jea_pyalg (not re-rolled) kept each pivot cheap. Verify-before-
  done caught the `file_id`/unit-view bug and the `path_seg` tripling.
- **G8 HANDOFF.** operator=self probes: `⟡es-unitnode-delta` (+23), `⟡sppf-projection-sql` (is the
  projection pure SQL?). operator=other residue: whether per-node OBSERVATION grain fits the catalog's
  domain semantics — P3 tells.
- **G9 ESCALATE.** Class "content-addressing the resolved form" is now covered BY CONSTRUCTION: the event
  writer only ever sees `decode_core`'s raw observation, so the resolved form is unreachable at write
  time. The observation/projection seam IS the gate. Deposited here.

### Shadow-engineer — the event-sourcing move
`110 mediated-composite`: goal (bounded content-addressed interner) → shadow (observation ≠ processing;
projection) → artefact (event log + projection). **L₁ COMPLETE** (interner decomp + events regroup →
composite built + verified, numbers reproduced). **L₆ guard-reconstitution COMPLETE**: my repeated
"bounded + bijective + content-addressed is impossible" WALL (a direct goal↔artefact `001` guard-trigger)
was reconstituted as positive content — the impossibility is TRUE for the resolved form, FALSE for the
observation; the guard's prohibition PRODUCED the observation/projection seam. The wall was load-bearing.

---

## RETROSPECTIVE (G0–G9) — the base64-everywhere detour

- **G0 PRECOMMIT.** ⟡content-addressed-interner: make db interning idempotent + concurrency-safe by
  content-addressing ids (base64), applied to the catalog (done, byte-identical, `3ad6cbe`) then to
  the SPPF.
- **G2 DELTA.** Expected base64 to *generalize* from catalog terms to SPPF nodes. Actual: nodes are
  unbounded trees; `base64(head ‖ child_ids)` embeds the subtree → 61 MB ids. The base64 **scope**
  was over-generalized from bounded leaves to unbounded trees.
- **G3 CAUSE.** *trigger*: I wrote `node_id = base64(head ‖ child_ids)`. *root (systemic)*: under
  context pressure I lost **why** base64 was adopted (concurrency-idempotency of the **shared leaf
  table**) and applied it as a universal id scheme; **no step forced me to re-derive the reason
  before extending the scope.** *contributing*: compaction carried "content-addressed base64 ids" as
  a slogan without the "only for bounded leaves / only for the concurrency win" qualifier.
- **G5 BLAMELESS.** Not "I lost sight" (character) → the pipeline recorded no **invariant** that
  base64 is *the leaf-interning concurrency mechanism, not a tree-id scheme* — so a compacted actor
  re-derives base64 as a universal and misapplies it.
- **G6 SUSTAIN (co-equal).** (a) The **measurement discipline held** — I measured node-id length
  (61 MB) instead of shipping; the number refuted me instantly. (b) The catalog base64 win is
  **real and verified** (byte-identical `reuse-index.md`, 0 bijection violations, concurrent-idempotent).
  (c) The autonumber hash-cons was **preserved in `jea_pyalg.IR.key()`** — recovery was a scope-revert,
  not a rebuild (reuse-search discipline paid off).
- **G7 COMMITS.** → the `⟡` ledger below.
- **G8 HANDOFF.** Probe I *can* run (operator=self → it's ⟡, not a handoff): do two concurrent
  `sppf_db` builds race on autonumber node ids? → **⟡concurrent-node-intern-probe**. Genuine residue
  (operator=other): whether **single-writer node interning matches the substrate's actual workflow**,
  or nodes truly need cross-writer concurrency (→ a Merkle/content address, accepting unboundedness or
  a hash). Only the user knows the workflow. **Open question, surfaced not resolved.**
- **G9 ESCALATE (class-level).** Recurring class: *an id/content-address scheme applied beyond its
  valid domain (bounded leaves) to unbounded structures.* Measure, escalated to the **strongest
  layer (schema gate)**: make `node_id INTEGER` so a base64 tree-id (unbounded string) is
  **unrepresentable by construction** → **⟡node-id-integer-gate**. Plus memory (below). Not a one-off:
  this is the second flatten-into-a-proxy recurrence this arc (paths, then nodes).

---

## SHADOW-ENGINEER — axis-tagged moves + probes

- `110 mediated-composite` — restore autonumber nodes + keep base64 terms (goal: bounded idempotent
  interner → artefact: the two-scheme `SqlIntern`). Mediated through the shadow "base64 is a
  leaf-only mechanism."
- `010 pure-SA` — docstring corrected to state the two-scheme architecture (artefact ↔ shadow, no goal change).
- `001→110 guard` — my "bounded+bijective+content-addressed is impossible" was a would-be direct
  goal↔artefact **wall**; the guard redirected it through the shadow "that's only true for *trees*;
  leaves are bounded" → the two-scheme composite. (The wall was real for trees, false as a universal.)
- **Probe L₁ (positive-closure): COMPLETE** — decomp (terms vs nodes) + regroup (one `SqlIntern`) →
  the mediated composite (two-scheme interner) is reachable and built.
- **Probe L₂/L₃ (guard-coverage): COMPLETE** — the node scheme is guard-cleared against "flatten the
  subtree into the id" (the 61 MB smuggling), now blocked by ⟡node-id-integer-gate.
- **Standing line (do NOT force):** whether the SPPF needs concurrent multi-writer node interning —
  stands until the workflow question (G8 residue) is answered by the user. Do not build a Merkle
  node-address speculatively to "close" it.

---

## ⟡ NEXT-STEPS LEDGER (invoke by label)

### The mission trunk (the ONLY AI that moves the Set₁ number 697)
- **⟡upfamily-rewire** — migrate consumers `Instances → UPArrowᴳ` (Set₀ constructive-solve), cascading
  into Phase1/BackedUP; retire the flat Set₂/Set₁ `UPArrow`. Migration pattern parked in `scratch/`.
  This is the paused trunk; everything else is foundation/tooling.
- **⟡ratchet-clean-census-guard** — the Set₁ census ratchet (true baseline 697); guard against a
  transient-undercount corrupting it (the 692 incident). Wire as a pre-commit check.

### Event-sourcing pipeline (the current architecture — `scratch/event_sourcing_build.md`)
- ~~**⟡content-addressed-interner** (catalog)~~ ✅ `3ad6cbe`; ~~(SPPF packing)~~ ✅ `3c28aa2` — SUPERSEDED
  by event-sourcing but the packing IS the SPPF projection, so it lives on as `project_sppf`.
- ~~**⟡sppf-full-build**~~ ✅ 2026-07-12 (packing era) — 1893 cores/180s, max id 4184, discriminates.
  RE-RUN under event-sourcing → `⟡es-full-build` (verify events+projection at full scale).
- ~~**⟡event-sourcing P1+P2**~~ ✅ `9046058` — sppf_db writes bounded events (max ekey 312); SPPF derived
  by projection; reproduces the interner EXACTLY (14913 packings, support 15, named-Functor=18).
- **⟡es-p3-catalog** *(the big remaining piece)* — the catalog + every other table become QUERIES against
  the SPPF projection. Do it as verifiable sub-steps (each is a real AI):
  - ~~**⟡es-p3-refs**~~ ✅ `6e1fe57` — refs = `unit_node ⋈ _node.op_path_id`, structs only (`_unit.kind`,
    added to projection). Exact match 358==358 (Category). Reads the PROJECTION, not events (tiering fix).
  - ~~**⟡es-p3-modules**~~ ✅ `ecfd02f` — `module_pid` into the projection (agdai_module from the core
    relpath); import edges = module-refs → owning-module (longest module-prefix). Exact 725==725 (Category).
  - ~~**⟡es-p3-structs**~~ ✅ `303691b` — structs=`_unit` kind∈{Datatype,Record}; members=`unit_member`
    (stored in events; names 1356==1356); field-heads=`_unit_cod` (codomain via `raw_final_head`,
    computed at PROJECTION time over the unambiguous per-core raw tree — the reentrant packing bridge
    CONFLATES contexts at shared Pi (node_child walk 51–68% wrong), so materialize it; catalog reads it +
    ⟨CARRIER⟩ abstraction). Member-heads 1356==1356 (Category). KEY LESSON: a per-instance structural walk
    can't run on the reentrant packing bridge — compute it in the projection (over raw, unambiguous) and
    materialize. Residue not from term structure: `desc` (module purpose / decl comments from .agda source).
  - ~~**⟡es-p3-edges**~~ ✅ verified (no code change) — struct-refinement `_edges` = the refs derivation +
    longest-STRUCT-prefix owner. 114==114 (Category). Query lives in ⟡es-p3-rewire. ALL catalog graph/struct
    tables now provably derive from the projection: _refs, _edges, _module_edges, _structs, _members, _member_heads.
  - **⟡es-p3-rewire** *(the integration + gate)* — make reuse_catalog CONSUME the projection (drop its own
    DbBuilder core-walk; `desc`/purpose stay a source read); full-tree reuse-index.md BYTE-IDENTICAL is acceptance.
    PREP done `2cf454d`: ParsedCore-from-projection == deserialize_core walk for 349/360 Category structs
    (members/refs/roots/field-heads exact); projection now carries `root_lid` + true codomain ctor; DROP-reset fix.
    - ~~**⟡es-p3-multihomed**~~ ✅ `9513286` — unit_id = base64(qname‖root) (unique per defmark);
      name_pid=base64(qname) kept for display. Member links RESOLVED at write time via per-core root_of
      (last-wins) → unit_member(member_name_pid, member_unit_id). VERIFIED: ParsedCore==walk for ALL
      360/360 structs; _refs 358, _members 1358, _member_heads 1358, _module_edges 725 all match. Homonyms
      recovered (units 3698→3730, members/heads 1356→1358). sppf_query ok.
    - ~~**⟡es-p3-wire**~~ ✅ `9be0ab2` — reuse_catalog CONSUMES the projection: `deserialize_from_projection`
      yields ParsedCore by querying the projection; fed to the UNCHANGED DbBuilder/write/render. generate()
      builds the projection (sppf_db) FIRST, then derives; write() is append-safe (no os.remove, IF-NOT-EXISTS
      schema, OR-IGNORE terms/path_seg). ACCEPTANCE MET full-tree: EVERY catalog output BYTE-IDENTICAL
      (reuse-index/graph/usage/import/sitemap). Order/empty-module/homonym edge cases did not bite.
  - ✅✅ **⟡es-p3-catalog COMPLETE** — the whole pipeline (event log → SPPF projection → catalog) derives
    from bounded content-addressed OBSERVATIONS; nothing is a write-time flattening. The event-sourcing arc is done.
  - (common structure under "full vs sub-step": sub-stepping IS the full P3, gated incrementally — not a separate path.)
- **⟡es-full-build** — rebuild the whole tree via the event-sourced path; confirm bounded events + SPPF at scale.
- **⟡es-unitnode-delta** *(G8 self-probe)* — pin down unit_node 66 459 vs 66 436 (+23); real queries identical, so low-pri.
- **⟡sppf-projection-sql** — make `project_sppf` a pure SQL query (base64 UDF + GROUP_CONCAT) not a Python fold — the "query, don't code" endpoint.
- **⟡sppf-query-display** — `sppf_query` truncates `node_id` to its shared base64 prefix (cosmetic; show a distinguishing suffix).
- **⟡sppf-default-fulltree** — make full-tree the default `sppf_db` invocation (currently defaults to `Category`).

### Catalog refinements (deferred, non-blocking)
- ~~**⟡catalog-pathseg-unique**~~ ✅ 2026-07-12 (`e7ff5c5`) — `UNIQUE(path_id, ord)` hoisted into
  `reuse_catalog` (owner); subsumes `ix_pathseg_path`; reuse-index.md byte-identical; 0 dup violations
  on live data. sppf_db keeps a defensive IF-NOT-EXISTS copy for fresh-db self-sufficiency.
- **⟡catalog-transitive-views** — transitive-closure readouts as SQL views.
- **⟡owner-as-view** — owner/home as a view, not a stored flattening.
- **⟡unhold-fp-subrank** — sub-rank the unhold_fp view.
- **⟡deserialize-decouple-sweep** — apply `deserialize_core` (parse-then-process) across the pipeline
  wherever tokenize sits adjacent to use (standing lint, memory `feedback_decouple_deserialize_from_processing`).

### Standing
- **⟡push** — HEAD ahead of origin; push after post-commit advisory amend marker + `git fetch` + ff.

---

## WHAT'S TRUE RIGHT NOW (state, for a cold restart)
- HEAD = `9046058` (event-sourcing P1+P2), 6 ahead of origin (unpushed — `⟡push`).
- `scripts/sppf_db.py` = EVENT-SOURCED: `write_events` (append-only event/obs/edge/unit_obs, bounded ekey
  ≤312) → `project_sppf` (derives the packing SPPF `_node`/`node_child`/`unit_node`). `build` = both.
  Verified on Category; reproduces the interner exactly. `sppf_query` reads the projection unchanged.
- The SPPF lives IN `catalog.db` (gitignored, one db). `reuse_catalog` OWNS terms/path_seg + the
  `ix_pathseg_uniq` invariant; its structs/refs/modules are NOT yet event-sourced → `⟡es-p3-catalog`.
- Next: `⟡es-p3-catalog` (sub-stepped: refs → modules → structs, gate reuse-index.md byte-identical).
- Set₁ live count = **697** (unchanged all arc; only foundation `UPArrowGraded`/`UPArrow2Collapse` +
  tooling built; `⟡upfamily-rewire` is the ONLY AI that moves it — the untouched mission trunk).
