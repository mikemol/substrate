---
name: project_z47_migration_cotype
description: "Shadow-engineer cotype for the z47→substrate migration arc: axis-tagged shadows, Fano-probe state, residue ledger. The compaction-survival record — read at session start, grow monotonically, never delete."
metadata:
  node_type: cotype
  type: project
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

# Cotype — z47 → substrate migration arc

## ⟡ NEXT-STEPS ROADMAP — labeled AIs (retro-ritual + shadow-engineer, 2026-07-05; read first if resuming)

**ARC STATUS: Ⓜ + Ⓓ COMPLETE · Ⓒ COMPLETE · Ⓖ (ground-in-tower) ACTIVE.** all full-build-green. HEAD 53b4759 on main,
AHEAD 7 of origin (user pushes MANUALLY — verify by `git fetch`, don't assert "pushed"; I overclaimed "pushed as you go",
retro G2). Trail 98291eb→53b4759 (13 commits): Ⓓ.gate-graph (d25015e) · z47 residue (0a7d044) · Ⓓ.catalog-db (1e5b008) ·
Ⓓ.render-from-db+sitemap+usage (30f8354) · Ⓓ.import-graph (2d72880) · Ⓒ.closure (d173e85, reinvention→collapse) ·
Ⓒ.bijection (f9f80b7, NEGATIVE→document) · Ⓒ.linear (58b7ac8, deferral→discharge) · Ⓒ.v4.{rotate 0a492fd, 3-carrier
7ed4c5c, site b77eecd} · Ⓖ.cyclic (53b4759).
**The recursive either/or DISSOLVED (Ⓒ vs Ⓖ):** NOT a choice — Ⓒ relates a reinvention to an existing abstract CENTER;
Ⓖ grounds that center itself in the tower's CONSTRUCTION. One ladder: instance → center → build. The center Groups.V4.V₄
that Ⓒ.v4 unified onto is ITSELF a build-trace (Ⓖ.v4 grounds it in the tower's rung-4 Klein-four). BOTTOM invariant = the
WITNESS TOWER'S CONSTRUCTION (the combinatorial basis; Cayley made constructive). "Grounding in the build IS unification"
— [[feedback_ground_in_tower_build]]. The labeled Ⓖ/Ⓥ roadmap is in that memory; next pivot: continue Ⓖ (tower-basis).

**The recursive either/or, dissolved (the user's reflex applied):** "build detection (Ⓓ) vs act on it (Ⓒ)"
is NOT a choice — they are the DETECT→NAME phases of ONE **reuse-mesh loop**: detect a shared center (Ⓓ) →
name it (Ⓒ) → the naming adds a bridge the index then surfaces (Ⓓ). And within Ⓒ, "witness-by-iso vs
lift-to-parent" is ONE move — *relate to the shared center* — at two distances: **iso** when the instances are
load-bearing-distinct (KleinV4≅V₄; Groups.V4's Coxeter `_·_` vs the direct table), **lift** when fungible
(bump/unbump→mapT). detect=Ⓓ, name=Ⓒ; the naming is iso-or-lift by distance. Governed by
[[feedback_dedup_preserve_crossdomain_bridges]].

**Ⓓ — DISCOVERY / ONTOLOGY layer (.agdai-derived standing analyses).**
- ✅ Ⓓ.reuse-index (d8cefcd) · ✅ Ⓓ.parallel-detect (5360dd8) — name→home + cross-name shape-parallels from the cores.
- ✅ **Ⓓ.gate (bd29882)** — pre-commit regenerates + auto-stages catalog/reuse-index.md in the full-build success
  branch (fresh .agdai), advisory/non-blocking. Verified end-to-end (fired on a forced build); the generator is
  BYTE-STABLE (deterministic sort) so no spurious diffs — only real structure changes churn the catalog. G9 escalation closed.
- ✅ **Ⓓ.reuse-graph (98291eb)** — structure→structure refinement graph from the RAW shim cores (interned form is
  shape-normalized, drops qname refs; RAW nodes carry constructor/qname/children). 753 nodes, 492 edges →
  catalog/reuse-graph.dot (GraphViz) + .md (Mermaid slice + degree ranking). In-degree census = reuse-primitives:
  ℕ(141)≫Fin(29)/≡(26)/Dec(22)/Word(22)/Gen(20)/CategoryOf(15)/DivStr(9)/Functor(7)/Ring(5). Format = Mermaid+DOT
  (LLM-fluent + tooling), per the user's sitemap/LLM-training point (see Ⓓ.sitemap-index). Manual regen (~1.5min raw shim).
- ✅ **Ⓓ.gate-graph (d25015e)** — DONE. The "share the shim" premise CONFIRMED: core_intern_agdai (which
  gen_reuse_index used) ALSO shells out to agdai_shim under the hood, so the tree was decoded TWICE. Factored the
  common phase into scripts/reuse_catalog.py: ONE streaming shim-walk (walk_cores) → THREE reducers
  (IndexBuilder / GraphBuilder / DbBuilder). gen_reuse_{index,graph}.py are now thin single-catalog wrappers;
  gen_catalog.py is the combined gate entry (one walk, both markdown files). Pre-commit Ⓓ.gate now calls
  gen_catalog.py + stages BOTH catalogs. Equivalence WITNESSED: refactor output byte-identical to committed
  reuse-index.md + reuse-graph.dot. The verify surfaced + FIXED a PRE-EXISTING non-determinism in reuse-graph.md
  (mermaid ids via hash(); degree-table ties via set-iteration — both PYTHONHASHSEED-randomized → churn every
  regen); now md5 ids + qname-sorted ties → byte-stable (two consecutive runs match). Gate fired end-to-end on the
  0a7d044 forced build.
- ✅ **Ⓓ.catalog-db (1e5b008)** — DONE. The next depth of single-source (the user's "shim→sqlite adapter?" Q): the
  SAME walk gains DbBuilder → catalog/catalog.db {structs,members,refs,edges + views in/out_degree, multiply_homed,
  shape_parallel}; fp computed in Python (sorted members) = the reuse-index fingerprint. scripts/catalog_query.py =
  the reuse-search INTERACTIVE endpoint (find/refiners/builds-on/homes/parallels/primitives/sql; read-only twice:
  mode=ro + SELECT-guard). Cross-check: DB's 492 edges == the graph's 492 (independent owner-resolution). .db is a
  derived non-deterministic binary → gitignored, regenerated by gate/on-demand; only markdown/dot committed.
- ✗ **Ⓓ.catalog-vtab — REJECTED** (the user's "weirder: sqlite read-only agdai backend?"). A vtab's whole point is
  row-addressability; .agdai is EmbPrj WHOLE-FILE, so `WHERE name='X'` still decodes every file — no locality to
  exploit; degenerates to catalog-db with a non-stdlib dep (stdlib sqlite3 can't even create vtabs). Charter-residue,
  not open work. Kept as considered-and-rejected with the locality argument.
- ✅ **Ⓓ.render-from-db (30f8354)** — DONE. catalog.db is now the SOLE canonical store: DbBuilder is the only
  accumulator (absorbs the .agda read for per-struct `desc` + per-module `purpose`/`is_index`); the former
  IndexBuilder/GraphBuilder are replaced by render_index(con)/render_graph(con) that SELECT from the DB. The walk
  builds the DB once; every artifact is a fast DB read; `gen_catalog.py --render-only` re-renders with NO walk
  (proven to reproduce identical files → the DB is a sufficient store). Byte-identity of index+graph WITNESSED
  across the rewrite. THE SUBTLETY that would have silently drifted: renders sort in PYTHON, not SQL ORDER BY —
  SQLite lower()/collation ≠ Python's on the Unicode struct names (ℕ, ℚ, α).
- ✅ **Ⓓ.sitemap-index (30f8354)** — DONE. catalog/reuse-sitemap.xml: 753 <url> entries, loc=synthetic
  https://substrate.local/<module-path>#<name> (substrate isn't served), priority=in-degree/max (the census as a
  crawl signal), lastmod OMITTED (only signal is non-deterministic .agdai mtime → would churn a committed file).
  Committed render (deterministic), the LLM-fluent discovery-manifest format the user flagged.
- ✅ **Ⓓ.usage-stats (30f8354)** — DONE. catalog/usage-stats.md: the reuse-graph census read from the TAIL —
  654 never-refined (in-deg 0), 424 refine-nothing (out-deg 0), 348 structurally isolated (both; used only via
  functions, not as struct components) vs the primitive head (ℕ 141≫…). Dead-center candidates to scan before adding.
- ✅ **Ⓓ.import-graph (2d72880)** — DONE. The MODULE-level twin of reuse-graph (struct-level): edge X→Y iff X's
  elaborated core references a name DEFINED in Y — SEMANTIC dependency (actual post-elaboration usage), NOT source
  `import` lines (unused imports drop; transitive-used appear). DbBuilder collects per-module ALL core-node qnames
  (before the struct early-return, so struct-less law/fn modules are nodes), resolves each by longest-module-prefix
  over the full 1751-module set → module_edges table + module_in/out_degree views → render_import →
  catalog/import-graph.{dot,md}; catalog_query gains imports/imported-by. GRANULARITY MATTERS (reads differently from
  reuse-graph): top MODULE = Foundation.Eq (1041) ≫ Foundation.Nat (765) — equality-reasoning is the most-imported
  module, though ℕ the TYPE is the most-refined struct. 1644 modules, 10382 edges. 5 prior renders byte-identical.
- ✗ **Ⓓ.catalog-vtab** — REJECTED (above).

**Ⓓ DISCOVERY LAYER: COMPLETE (no ◇ left).** Architecture settled: ONE shim-walk → catalog.db (the sole store) →
SIX renders (reuse-index.md, reuse-graph.{dot,md}, reuse-sitemap.xml, usage-stats.md, import-graph.{dot,md}) +
catalog_query.py (interactive: find/refiners/builds-on/imports/imported-by/homes/parallels/primitives/sql, read-only) +
the pre-commit Ⓓ.gate that rebuilds catalog.db + stages every render on each structural full build. A NEW discovery
artifact = one more render function (or a SELECT); never a new walk. The natural pivot is now Ⓒ (ACT on what the
catalog surfaces — the detect→name loop), starting Ⓒ.closure (`_⇒*_` ×7 vs Foundation.RewriteConfluence).

**Ⓧ — PROMOTION / housekeeping (immediate).**
- ○ **Ⓧ.push** — HEAD 2d72880; local shows `ahead 2` of the LAST-FETCHED origin/main (1e5b008) — but that count is
  UNVERIFIED until a `git fetch` (the remote-tracking ref is stale; I wrongly asserted "nothing pushed" this arc).
  Per policy: `git fetch` → confirm post-commit amend markers present (they are) → fast-forward → push. All 6
  session-2 commits are gate-green.

**Ⓖ — GATE / DISCIPLINE HARDENING (from the session-2 retro G9; the recurring-class findings).**
- ✅ **Ⓖ.async-hygiene** — DEPOSITED as memory [[feedback_async_commit_hygiene]]: structural commits → `run_in_background`
  (the ~2.5min full build exceeds the 2-min foreground limit → SIGTERM aborts the commit); rely on the task-completion
  notification, NOT a `pgrep -f <string-in-my-own-command>` poll (self-matches → hangs); verify push-state by `fetch`
  before asserting it. G9 closed at the memory layer (a Claude-behavior rule; not automatable by a hook).
- ◇ **Ⓖ.commit-tree-clean** — the migration-residue class: the pre-commit gates validate the WORKING TREE, so a commit
  that stages a SUBSET can pass while leaving gate-output (decl-shape tags, gen_build_makefiles) uncommitted (exactly
  the 0a7d044 residue). Consider a cheap check that, after a structural commit, `git status` shows no uncommitted
  gate-generator output. Moderate recurrence; needs scoping (don't over-block). NOT yet escalated.

**Ⓒ — NAME THE SURFACED CENTERS (Ⓜ.dedup-pass generalized tree-wide).** Each: `jea_pysim … --clusters` confirm
(type-aware, cross-domain-vs-within) → witness-by-iso OR lift. Data-driven by Ⓓ.parallel-detect's 25 clusters —
NOW ALSO catalog-driven: `scripts/catalog_query.py parallels` / a `shape_parallel` SELECT is the live worklist.
- ✅ **Ⓒ.closure (d173e85)** — DONE. The `_⇒*_`/`_⟶*_` ×7 (fp data|_◅_,done) audited & related to the center
  Foundation.RewriteConfluence (relation-generic Newman/CR). The audit SPLIT them (candidates≠auto-collapse):
  3 were ALREADY the center's instances (native R.Trace: NewmanKI.Properties, NewmanSKI.Properties,
  SKIReductionToList — the catalog flags instances because a parameterized-module instantiation emits a
  specialized def-marker); 3 were FUSep reinventions (from z47) — FUSepQCR.Newman was a FULL copy incl. the
  diamond-tiling proof → now RE-EXPORTS the center (interface verbatim, FUSepQReduce opens it unchanged);
  FUSepConvEtaWitness's local `_⟶*_` → instantiates the center. Corrected FUSepQCR's stale ⟡H0 absence-claim
  ("NO Newman anywhere"; RewriteConfluence was upstreamed independently after). RewriteConfluence now has 6
  dependents (was 3) — the import-graph CORROBORATES the shape-parallel (the two catalog graphs complement:
  parallel-detect flags the candidate, import-graph confirms the shared center). Compiler-confirmed, full-build
  1751/1751. −55 net lines. THE detect→name loop demonstrated end-to-end.
- ✅ **Ⓒ.bijection (NEGATIVE finding, DONE)** — the record {to,from,to-from,from-to} ×5 shape-parallel is a
  FALSE POSITIVE for collapse (fingerprint is member-NAME based, type-BLIND). Audited: 3 are load-bearing
  setoid/extensional isos (Stab≃S₃ @apply-agreement, TotalSpace≃S₄ @≈/≡ heterogeneous, Live≃Permutation — their
  authors DOCUMENTED they can't use `_↔_`); 2 are scoped propositional generics (Algebra._↔_ Set₀-stdlib+combinators
  /7 deps vs Foundations.Bijection universe-poly /3 deps — same concept, NOT merged: 7-dep migration for ~5 lines,
  low-value/moderate-risk). Action taken: cross-reference comments in the 2 generic headers (resolves "which bijection?"
  debt without churn) + memory [[feedback_bijection_parallel_false_positive]]. NO collapse (would destroy the
  load-bearing equalities). The Ⓜ.dedup precedent (false-positives ARE a correct audit outcome) — negative-findings-corpus.
- ◇ **Ⓒ.setoid-bij** (BUILD arc, only if count grows) — the true common center the 3 specifics gesture at: a
  HETEROGENEOUS setoid-bijection (bijection up to per-side `_≈A_`/`_≈B_`; `_↔_` = the (≡,≡) case). Does NOT exist
  (reuse-searched). Building it + relating all 5 is new machinery — its own dispatch, not a fold-in.
- ✅ **Ⓒ.linear (DONE)** — 3 fingerprint groups: (C) `LinearAlgebra` = a full STRUCTURE, excluded; (B) `Linear
  {…preserves-·c}` ×8 = ALREADY factored (one record in Polynomial/Graded.agda, re-exported via the `.Over` chain —
  the open/import caveat again, no action); (A) `Linear`/`Linearℚ` {…preserves-*ₛ} = the real target. Center EXISTS &
  its header BEGGED for it: Algebra.Module.Hom "ModuleHom is the universal Linear map — F₂.Linear and ℚ.Linear
  retrofit as ModuleHom instances at Mod6/Mod7" — a promise NEVER delivered. REALIZED (witnessed, not collapsed —
  F₂.Linear keeps its small vector API): NEW F2.Linear.AsModuleHom + Q.Linear.AsModuleHom, each `Linear ↔ ModuleHom
  (…FreeModule)` BOTH directions (transport is DEFINITIONAL: module ·ₛ=*ₛ, +=+ⱽ; carriers F₂/ℚ-FreeModule were
  ready in {F2,Q}.AsModule; ℚ side parametric in a ℚ-Field-Obligation). ModuleHom.agda now points at the realizations.
  Compiler-confirmed. "A deferral is a hypothesis to verify" — discharged. Contrast Ⓒ.bijection (center didn't exist);
  here the center existed and its retrofit was the deliverable.
- ◑ **Ⓒ.v4 (exemplar done; gaps labeled)** — data{e,α,β,γ} ×8. ⚠ I first mis-called this a
  false-positive-for-collapse; the USER CORRECTED me (twice): "lack of relating may be a BUG / an implicit
  group action needing another object", and ComposedReference's "kept local, dependency-light" is an
  unverified LLM rationalization (contradicted by its own Record.action : ActionAlgebra). CORRECTED finding:
  `data V₄` is the CARRIER; most of the 8 USE it as an ACTING GROUP with implicit/vacuous laws → the
  non-relating is a latent GAP (relate to Groups.V4 `V₄-Group` + `Actionᴳ`), not a distinction. LESSON: don't
  accept "just a label" / "kept local" self-descriptions as load-bearing — VERIFY (the absence-words trigger).
  DONE (exemplar): `Pipeline.Examples.RotateCrumb` — its empty `record Preserves-V4` (a vacuous homomorphism-tag
  over a real v4-xor F₂²-XOR action) → a WITNESSED `crumb-action : Actionᴳ V₄-Group Crumb` (real act-id/act-∙,
  refl by computation once V₄'s op-computability was verified), carrier now the canonical V₄. [committed]
  REMAINING GAPS (each a relate + Actionᴳ arc, dispatch by symbol):
  - ✅ **Ⓒ.v4.composed-ref / .residue / .rule-action (DONE, one commit)** — the sharper bug: RuleAction,
    ComposedReference, ResidueCompensation each had their OWN `data V₄`, so a residue σ composed in one couldn't
    flow into another (three incompatible copies of the one group). UNIFIED all three onto Groups.V4's canonical V₄
    (re-export shims — constructors e α β γ preserved, dependents unchanged). RuleAction.V4Compose._∘V_ (a
    hand-written 16-entry Cayley table = eliza/rule_action.py) DEDUPED to Groups.V4.Operations._·_. Compiler-verified
    across all 6 dependents. Residues now interoperate. The "dependency-light" exclusion was an unverified
    self-description (contradicted by ActionAlgebra.residue : V₄). [committed]
  - ✅ **Ⓒ.v4.site (DONE — and it DEEPENED the whole arc)** — the user reframed: don't compare V₄ to the tower,
    GROUND V₄ IN the tower's BUILD. The tower's growth inductively constructs the Sₙ chain (Enumerate.perms); V₄
    is the Klein-four subgroup it PRODUCES at rung 4 (KleinCensus debut). So V₄'s elements ARE the tower's
    permutations, its op IS the tower's `compose`. Method interned from the user's reference ExtrudeSKIKFaces
    ("an attribute IS its build-trace"; see [[feedback_ground_in_tower_build]]). NEW WitnessTower.V4Grounding:
    ⟦_⟧ : V₄ → Perm 4 (the normal V₄ = id + 3 double-transpositions) + `·-is-compose : ⟦x·y⟧ ≡ compose ⟦x⟧⟦y⟧`
    (16× REFL — Groups.V4's op IS the tower's compose, ⟦_⟧ a homomorphism) + involution/rung-4 placement +
    the TopologicalGroup inhabitant. Because Groups.V4.V₄ is the Ⓒ.v4-unified carrier, this REGROUNDS all 82
    dependents on the tower's construction at once. Sites.V4 fixed (was a bare op-table OVERCLAIMING a bridge;
    TopologicalGroup's only field is the group + V₄-Group is proven → `record { group = V₄-Group }`, canonical V₄,
    reinvention removed). Comonoid.Sites.V4 (comonoid diagonal) genuinely stands. **Ⓒ.v4 COMPLETE.**
    ⟡ NEXT (user's vision, bigger): "grounding in the build IS unification" — the abstract data-type carriers are
    themselves regroundable on the tower's construction. V4Grounding is the pattern; other tower-built groups
    (S₃, S₄, Z_n, the whole Sₙ chain the tower builds) are candidates to ground the same way (Ⓒ.ground-in-tower).
  Banked: [[feedback_v4_carrier_action_gap]] (the corrected finding + the don't-credulously-exclude lesson).
- ◇ **Ⓒ.torsor / Ⓒ.action** — IsTorsor×2, Action×2 (audit cross-vs-within first).
- ⚠ FALSE-POSITIVES (name-based screening, NOT dups): Fin/ℕ {suc,zero}; the {[],_∷_} `*Term` cluster.

**Ⓟ — build/membudget infra (standing, untouched this session).**
- ○ Ⓟ.selftest (lock kernel under real concurrent load — [[feedback_test_infra_under_real_concurrent_load]]) ·
  ○ Ⓟ.profile-reconcile · ○ Ⓟ.grow-ledger.

**Ⓐ — ◇ Ⓐ.gf256-primitive** (needs re-scoping; no live intent recovered).

**HANDOFF blind spot (retro G8, operator=other):** whether the reuse-index actually changes future-LLM behavior
(does a builder consult it before re-deriving?) is only observable across sessions / cold-restate — CLAUDE.md now
points at it (fastest-check), but the behavioral change is unverified from inside. The instrument is the next
session's own reuse-search trace.

---

**GOAL (user, verbatim intent).** Migrate the provided z47 Agda files into appropriate places within the
agda substrate; **dedup** proofs where truly structurally identical; otherwise **preserve alternate paths as
pinned intermediate forms** (which accelerates future resolution via SPPF sharing). Then: **retire the
baseline** (user dislikes grandfathered debt — drive the import-shape ratchet to 0).

**ARTEFACT (workspace state, as of this write).** substrate @ HEAD 7c61738. Working tree: 91 z47
Substrate.*-namespaced modules placed at declared paths + typecheck green (built on the fixed membudget
`make -j`); OrbitAudit `Bool` deduped into `Foundation.Bool` (ratchet 94→27); the bulk Wedge-pin attempt
REVERTED (baseline→HEAD, migrated→z47). Ratchet = 27 (all `Wedge`), baseline=11. Uncommitted (gate blocks
until the 27 Wedge imports are pinned). 35 bare self-contained z47 modules (FoldUnfold/FUSep/S5* clusters)
NOT yet placed (need a home namespace).

## Shadows (axis-tagged; monotonic — append, never rewrite)

- **S1 [100 pure-GS, lift]** — ingest of the 182-file z47 corpus → the ingest map (4 parallel readers +
  synthesis). Intact goal "understand+integrate" → named shadows (Kolmogorov-topos frame; the Rosetta;
  the 2 verified-new modules RewriteConfluence+Allegory.Mono; the extruder-as-wedge bridge).
- **S2 [100 pure-GS, lift]** — the migration target-map manifest (/tmp/z47_manifest.tsv): 92 Substrate-path
  drop-ins (0 path-collisions) + 35 bare-need-home. Decomposes the migration goal into per-module targets.
- **S3 [110 mediated-composite]** — place 91 + `make -j` → 91 green (goal→shadows→artefact, mediated by S2).
  First large-scale run of the fixed membudget lock: no deadlock, no starvation.
- **S4 [010 pure-SA]** — Bool dedup: OrbitAudit's local `data Bool (tt ff)` folded into `Foundation.Bool`
  (renamed constructors). Behaviour-preserving extraction of the canonical center. Ratchet 94→27.
- **S5 [001→guard-fired, redirected]** — the bulk Wedge-pin: a goal ("retire baseline") → artefact ("rename
  Wedge across 39 modules") move executed **without mediation through per-module verified shadows**. The
  guard fired POST-hoc: build → [NotInScope] (missed-token regex) + OOM churn (ill-formed modules churn the
  typechecker). REVERTED. This is the mediation-guard event; the redirect is S6.
- **S6 [residue, portable]** — baseline-retirement re-scoped as SURGICAL/incremental. (Executed as S7.)
- **S7 [111 triadic-full, DELIVERABLE] — DONE, commit 65ffa12, full build 1700/1700 PASS.** Surgical Wedge-pin
  migrated-only, exclude-vs-rename decided BY THE COMPILER per module + build-verified (9 excluded, 8 renamed;
  fixed the regex over-match `fromℕ-Wedge` — the lookbehind must exclude `-`). carrier-locality (SKIFaithfulRb
  `_++L_`→`Foundation.List._++_`). Ratchet 94→11=baseline. Deferred 5 def/proof leaves (all imported-by-0):
  Newman{KI,SKI}, CF{Bezout,Matrix}Bridge, SKIGradedTraceChain → need a `.Properties` split. The guard-cleared
  form of S5: the same goal↔artefact move, now MEDIATED per-module through the compiler-as-verifier.

## Fano-probe state (do NOT force standing lines — over-decode is the dual of over-classify)

- **L₁ {100,010,110} positive-closure — COMPLETE.** S1/S2 (100) + S4 (010) + S3 (110) populated ⇒
  mediated-composite reachable. Deliverable extracted: the 91-green migration.
- **L₂ {100,001,101} GS-guard-coverage — GAP on 101.** S2 (100) + S5-guard (001) populated; guard-cleared-GS
  missing. Names next-work: the migration moves need auditing against goal-bypass (the pin was the bypass).
- **L₃ {010,001,011} SA-guard-coverage — GAP on 011.** S4 (010) + S5-guard (001); guard-cleared-SA missing.
  Next-work: the dedup/pin (SA) moves need guard-clearing (verify per module before the artefact lands).
- **L₄ {100,011,111}, L₅ {010,101,111}, L₆ {001,110,111}, L₇ {110,101,011}** — STANDING (≤1 populated point
  each after this registration). Let them stand. Re-check on the next real move; do not supply a third point
  to tidy the picture.

## Residue ledger (realizability-charter coordinates — reference arm noted; nothing discarded)

- **Migration-as-a-whole** @ pre-commit-ratchet: coordinate **level=observable** (constructible+reachable+
  observable clean; 91 build green). Residue @ coverable: the 27 Wedge bare-imports the ratchet won't bound.
  Closed by S6 (the surgical pin). Portable — re-audit after the pin → expected `runtime-valid`.
- **The bulk pin (S5)** @ agda-typecheck: coordinate **level=constructible** (the script ran). Residue @
  reachable: the missed-token edge cases (`Adjunction:118`, `Factoradic:67`, `NuRegistryEntry:41`) → NotInScope.
  NOT a reject — residue portable to the SURGICAL reference arm (per-module, exclude-not-rename), which is
  expected to close it.
- **The 35 bare clusters** @ substrate-namespace: coordinate **level=constructible** (they exist, self-
  contained). Residue @ reachable: no declared home namespace / bare module names collide with the tree's
  path convention. Closed by a homing decision (`Substrate.Parallel.*` candidate — a STANDING line, not forced).

## Deferred gap candidates (next-work; the loop does not plan — user chooses)
DONE: S6/S7 surgical Wedge-pin + carrier-locality (65ffa12); RewriteConfluence + Allegory.Mono landed;
**Ⓜ.baseline-zero (619a671 — import-shape BASELINE=0; every bare colliding import specialized; edge cases
`Wedge.field` + submodule telescope now handled by the corrected rename regex).**
DONE: **Ⓜ.def-proof-5 (+V4FullCocycle) — commit a49c955, full build 1710/1710.** 4 def/proof splits
(Newman{KI,SKI}, CF{Bezout,Matrix}Bridge → module + `.Properties`); SKIGradedTraceChain's `.Properties` import
was dead code (dropped); V4FullCocycle placed. 92/92 substrate-namespaced z47 modules landed.
REMAINING:
DONE: **Ⓜ.v4-unify — commit 5ed4a6b, full build 1710/1710.** V4Full's F₂-bit rep is LOAD-BEARING (chirality-of
   reads the morph bit; every group law refl) — so the resolution was NOT "replace with a center" but the
   substrate's own idiom (V4-as-Z2xZ2's docstring: presentations coexist RELATED BY A WITNESSED ISO): added
   `to₄/from₄ : V4Full ↔ Groups.V4.V₄` (rowSwap↔α, recip↔β, klein↔γ) + both round-trips + the group
   homomorphism `to₄(g·h) ≡ to₄ g ·₄ to₄ h`, all 16 cases refl (Groups.V4._·_ computes on the 4 elements). So
   V4Full is the canonical V₄ in the bit-coordinate CHART, not an orphan. The either/or dissolved into ONE
   group, two charts. (Lesson: for a load-bearing alt-representation, RELATE-via-iso ≻ replace.)
2. **Ⓜ.home-bare** — IN PROGRESS (user chose CONFORM-into-canonical: "the gate-fight is the feature — a clear/strict
   done, clean not haphazard"). NAMESPACE: FU cluster → `Substrate.FUSep.<BareName>`; S5 cluster → `Substrate.S5.<BareName>`.
   DONE: `Substrate.FUSep.FoldUnfold` (conformed + builds, working-tree, uncommitted — archetype). 34 remaining.
   **CONFORM RECIPE (per module, dependency-order, build between batches):**
   (a) `module <Bare>` → `module Substrate.<NS>.<Bare>`;
   (b) DELETE the inlined stdlib defs (`data _≡_`, `data List`, `record Σ`, `_×_`, `data ⊥`, `data Bool`, `sym/trans/cong`);
   (c) ADD Foundation imports — routing map: `_≡_ refl sym trans cong cong₂`→Foundation.Eq; `Σ _,_ _×_`→Foundation.Product;
       `List [] _∷_`→Foundation.List; `Bool true false`→Foundation.Bool; `¬_`→Foundation.Negation; `ℕ zero suc _+_`→Foundation.Nat;
       (`⊥`→Foundation.Empty, `⊤`→Foundation.Unit — VERIFY the exact module on first use);
   (d) inter-cluster imports `open import <ClusterMod> using (…)` → `open import Substrate.<NS>.<ClusterMod> using (<DOMAIN names>)`,
       SPLITTING the stdlib names out of the using-list into the Foundation imports from (c) (dependents import stdlib FROM the
       root today, e.g. `open import FoldUnfold using (_≡_; refl; _×_; _,_; Magma; Gen)`);
   (e) build the module; then gates: import-shape (BASELINE=0 — the inlined-stdlib ambiguities vanish once ALL are conformed),
       def/proof, carrier-locality; COMMIT per cluster.
   ORDER: FU roots (FoldUnfold✓ → ObsBisim, ConversionCongruence, FUDepth, FUEtaObsCoalg[already imports Substrate.*]) →
   FUSepConv{,EtaWitness,ObsBisimWire,Sharpen} → FUSepQ{,Bridge,Confluence,CR,Cyc,Halts,Hexagon,Lambek,Nf,Reduce,SKI};
   then S5Verdict → S5{Carrier,EEA,Fixpoint,Matrix,Nerve,Real,RealConv,Regress,RegressFix,Section,TorsorBridge,TorsorWireV4,TwoFuel,TwoFuelFix}.
3. **Ⓜ.dedup-pass** — ROUND 1 DONE (commit cdb8be2, build 1745/1745). Driven by jea_pysim --clusters (the
   structural-dup tool, NOT name-matching) over FUSep/S5 cores + canonical overlap targets. Collapsed:
   - **KleinV4 ≅ Groups.V4.V₄** witnessed iso (S5TorsorWireV4): the load-bearing-chart case — its DIRECT Cayley
     `_·_` is refl-reducible (torsor proofs rest on it) while Groups.V4._·_ is Coxeter-routed (not refl-reducible
     on abstract args), so RELATE-via-iso not replace (V4FullCocycle precedent). to₄/from₄ + round-trips + group
     hom (concrete cases refl; identity via ε-left). NOTE: categorical-grounding advisory STILL flags it FLOATING
     — the iso is a bridge but not REGISTERED in Category.UniversalProperty.Registry; registering is the closer (non-blocking).
   - **length ×3** → Foundation.List.Length (S5Real/S5TwoFuel/S5TwoFuelFix, byte-identical).
   ROUND 2 DONE (commit 24cf1af, build 1746/1746): **lifted Dedupe** to shared `Substrate.S5.Dedupe` (both
   runners DERIVE from it; ≤-up=Foundation.≤-suc-r deduped in the lift) + **witnessed def-eqs** RIdx≡PIdx,
   PIdx≡QIdx (FUSepQHexagon/Confluence — the "small dups are def-eq demonstrations" reframe).

   **GOVERNING PRINCIPLE (user correction, load-bearing — [[feedback_dedup_preserve_crossdomain_bridges]]):**
   the z47 material is largely EXPLICIT WIRING between subsystems not cleanly connected before. A dedup that
   COLLAPSES a cross-domain duplicate DESTROYS the bridge (Level-1) and the bridge-of-bridges (Level-2: the
   "S5 IS a metacircular reflection of the substrate" story). So classify every jea_pysim dup:
   - **within-domain** (length ×3, ≤-up, the Dedupe copy) → safe COLLAPSE; shared import documents the dep.
   - **cross-domain** → do NOT collapse; WITNESS as a transport (the KleinV4≅V₄ model). These ARE the value.
   REMAINING, RECLASSIFIED:
   - **CROSS-DOMAIN BRIDGES to WITNESS (not collapse!)** — the real prize:
     · ✅ **S5Matrix ↔ CFMatrixBridge** — DONE, commit 7e11ff6 (Substrate.S5.S5MatrixBridge): structural iso +
       algebra morphism (to preserves I/M/_·_/state, all refl) + THEOREM TRANSPORT (S5's matrices inherit
       CFMatrixBridge.Properties's detM=det4 + matrix-det-flip = ◆T3's (−1)ⁿ — the sign story S5Matrix only
       CITED, now machine-checked). Pattern template for the rest. --guardedness INFECTIVE (bridge needs it too).
       Bridge-map names (to/from/detM) intentionally shared with other bridges (Wedge.Adjunction, V4.Bijection,
       NedgeBridge) — that naming consistency IS the Level-2 bridge-of-bridges pattern; collapse-check advisory is expected.
     · ✅ **S5RealConv/S5Real ↔ Algebra.R.Trace** — DONE, commit 21a31b1 (Substrate.S5.S5RealBridge): COINDUCTIVE
       bridge (stream eq = Bisim._~_, finite obs = _≡_). to:CoTrace ℕ→RealTrace + round-trip ~ + observation
       transport (take, convergent-agree: S5's convergents ARE the substrate's) + named-value (to twos~Trace.twos,
       to sqrt2~Trace.sqrt2 — S5's √2 IS the substrate's √2). Pattern: coinductive bridges use Bisim._~_ for streams.
     · ✅ **S5EEA ↔ Algebra.Wedge** — DONE, commit 966a016 (Substrate.S5.S5EEABridge): toDivStr field-for-field +
       DivStr-indexed toWedge/toTrace + shape-agree (S5EEA's quotient-sequence IS Wedge.Shape.shape) +
       reduction-CF-is-wedge-shape ("combinator reduction IS a wedge-zip whose shape is a CF"). Pattern:
       parametrized-record bridges thread the index (DivStr) through each transport.
   **BRIDGE TRIO COMPLETE** (matrix 7e11ff6 / real 21a31b1 / wedge 966a016): the S5 metacircular cluster is now a
   WITNESSED reflection of the substrate across three keystones (2×2 CF matrix / coinductive reals / wedge operator),
   not three silent re-derivations. The shared to/from/toX vocabulary across bridges (+ Wedge.Adjunction, V4.Bijection,
   NedgeBridge) IS the Level-2 bridge-of-bridges structure. (conv-go/convergent/twos/sqrt2/two/four —
     "S5 fuel-evaluation IS the coinductive reals"); **S5EEA ↔ Algebra.Wedge** (shape/DivStr — "combinator
     reduction IS a wedge-zip whose shape is a CF"). Witness each as a KleinV4-style transport. Also the
     PRE-EXISTING tree dups (OrbitFaithful↔OrbitUniversality.cover, OrbitBoundary↔OrbitComplete.cover,
     Cancel.bump↔Ops.addℕ, CFBezoutPrev↔Properties.det4) — audit for cross-domain before collapsing.
   - **trivial within-domain smalls** (symEq ×3 = Foundation.Eq.sym; proj₁/proj₂ = Foundation.Product.proj)
     → witness/collapse, low stakes.
   Cluster evidence: scratch/dedup_clusters.txt (104 clusters, 24 cross-module IDENTICAL/STRONG).
   ✅ **Ⓜ.dedup.registry DONE — commit 89ad4e3** (2 parts): (1) Substrate.S5.BridgeRegistry — the discoverable
   first-class bridge-of-bridges index (imports the 4 witnessed transports; registration=compiling; the
   discoverability fix the whole arc was about; un-orphans the bridge leaves). (2) Grounded S5TorsorWireV4 on the
   CATEGORY spine: the KleinV4≅V₄ iso now does WORK — deloop V₄-Monoid (Groups.V4.Bundle) = BV₄, the Klein
   four-group's one-object groupoid (klein-deloop : CategoryOf). Closed the LAST standing advisory (categorical-
   grounding: "no ungrounded domain algebraic modules"). Lesson: the checker un-floats on `import Substrate.Category`;
   deloop of a Monoid is the clean spine-grounding (CategoryOf lives in Category.CategoryOf, NOT re-exported by Delooping).
   ✅ **Ⓜ.dedup.smalls DONE — commit 8415591**: the 3 small clusters witnessed as def-eqs (RIdx pattern), NOT deleted —
   two≡/four≡ (S5RealConv↔S5Real), symEq≡sym (FUSepQCyc private helper = Foundation.Eq.sym), proj₁≡/proj₂≡
   (FUSepQConfluence local = Foundation.Product.proj). Within-domain dups → witnessed identities.
   ✅ **Ⓜ.dedup.tree DONE — AUDIT, no code action (a negative finding).** All 4 pre-existing jea_pysim "tree dups"
   are FALSE-POSITIVES-FOR-COLLAPSE; collapsing any would have destroyed real structure:
   - **35 bezout-combo↔det4** (both `(p₁*q₀)⊖(p₀*q₁)`): ALREADY a witnessed CROSS-DOMAIN bridge — CFBezoutPrev proves
     `bezout-combo ≡ det4` (Bézout=determinant). The prior author already did the right thing (coexist + theorem). Model.
   - **36 Cancel.bump/unbump ↔ Ops.addℕ**: a PARAMETRIC FAMILY (my first call "genuinely different, leave" was WRONG —
     user corrected). 88%/hole@depth2 = "one parametric concept": shared `head=f(head x)`, hole=tail (recurse vs stop).
     LIFTED (commit 7acb982) → Substrate.Algebra.R.Trace.StreamMap: bump=mapT(k+_), unbump=mapT(_∸k), addℕ=onHead(k+_).
     The generic stream map was genuinely ABSENT (each op reinvented it). CAVEAT banked: the hole isn't a clean function
     param (guardedness rejects corecursion-through-a-function — TESTED); it's a choice between two guarded copattern
     generics sharing the head-fn. Definitionally equal → all proofs/dependents survived.
   - **48 OrbitBoundary↔OrbitComplete.cover / 49 OrbitFaithful↔OrbitUniversality.cover**: ONE shared `cover = ana orbit-coalg`
     defined in OrbitUniversality.OrbitCover, `open`ed by all three orbit modules. Already factored, not re-derived.
   LESSON (reinforces [[feedback_dedup_preserve_crossdomain_bridges]]): jea_pysim clusters are CANDIDATES-requiring-audit,
   NOT auto-collapse targets. On audit, hits resolve to: already-witnessed bridge / already-shared factoring / genuinely-
   distinct function. The substrate already practices the discipline. **Ⓜ.dedup-pass is now FULLY COMPLETE (0 open items).**

## Ⓜ.home-bare FU-cluster — DONE, commit d934069 (full build 1730/1730 PASS)
**FU cluster (20 modules: FoldUnfold + 19) COMMITTED + all gates green** at `agda/Substrate/FUSep/`. Conform recipe applied
tier-by-tier (build-verified each tier). Key patterns that WORKED:
- stdlib→Foundation routing (Eq/Product/List/Empty/Nat/WellFounded); `Σ` needs `renaming (proj₁ to fst; proj₂ to snd)`
  for bodies using fst/snd (FUSepQCR).
- qualified cross-module refs `Mod.X` do NOT resolve after path-change → use module alias `import Substrate.FUSep.Mod as Mod`
  + `open Mod using (domain names)` (ObsBisim/FUDepth/Wire alias ConversionCongruence; FUSepQCyc aliases FUSepQReduce;
  FUSepQSKI aliases FUSepQHalts). OR add the name to the using-list unqualified (ConversionCongruence's `Congruence`).
- split stdlib names OUT of cross-cluster using-lists into Foundation imports (dependents imported ℕ/List/Acc *from*
  the cluster root today; conformed FUSepQSKI imports ℕ from Foundation.Nat non-public, dependents take ℕ from Foundation too).
- **Magma DEDUP done**: FoldUnfold's bundled `record Magma{Carrier;_·_}` → canonical `Algebra.Magma.Magma A` (carrier=module
  param `{Carrier:Set}`, `_·_` via `open Magma M`; body untouched). ConversionCongruence: `ars-magma : Magma Carrier =
  record{_·_=_·_}`. Cleared 24 import-shape flags + un-broke all pre-existing Magma importers. (Mechanism understood:
  at HEAD `record Magma` was defined in EXACTLY ONE place → adding a 2nd differently-shaped def made the NAME ambiguous →
  flagged every bare importer tree-wide. Dedup removes the dup → name unique → collateral clears WITHOUT touching pre-existing.)
- **carrier-locality done**: FUDepth `_++_` → import from Foundation.List. Gate now CLEAN.
- **Two/Setoid pinned-as-distinct done**: FUSepConvSharpen `data Two`→`Bit2`; FUSepConv `record Setoid`→`EqSetoid`
  (fields refl≈/sym≈/trans≈ UNCHANGED; FUSepQ's `FUSepConv.Setoid`→`FUSepConv.EqSetoid` at the 2 record constructions).
  These are genuinely different-shape from canonical (Algebra.Setoid uses ≈-refl explicit-arg) → PIN under distinct name
  (user's "otherwise preserve alternate-paths as pinned"), not force-dedup (which would cascade sig-fixes into FUSepQ).

**REMAINING import-shape (2 names, ~26 flags) — the ONLY thing between FU cluster and commit:**
- **_~_ (23 flags)**: FUSepQCyc defines `record _~_` (Stream bisim, shape 0c3060bd) colliding with canonical
  `Trace.Bisim._~_`. FIX = rename FUSepQCyc's DEF `_~_`→`_~ₛ_`, cascade to importers FUSepQLambek/FUSepConvSharpen/
  FUSepConvEtaWitness (they `using(...;_~_;...)` from FUSepQCyc). SURGICAL: `_~_` token (imports/record/open/LambekFix
  param) AND infix ` ~ ` (space-delimited) → `~ₛ`; but `_~_` ALSO appears in COMMENTS referencing EXTERNAL `Bisim._~_`
  (FUSepQCyc:49, Sharpen:40) — do NOT blind replace_all; targeted edits. Names `~-refl/~-sym/~-trans/hd~/tl~/cyc~const/
  allHeads~const/selfSimilar~cyc/cyc-loop~const` are SEPARATE identifiers — only the `~` OPERATOR (spaces) in their
  SIGNATURES changes, the names stay. Exact code lines: FUSepQCyc 50,52,53,61,65,69,79,83,98,104,127,136;
  FUSepQLambek 29,59,87,90,96,116,136; FUSepConvSharpen 23,37,44,47,84; FUSepConvEtaWitness 21,85.
- **Tm (3 flags)**: importers FUSepQHexagon/FUSepQConfluence/FUSepQNf import bare `Tm` from FUSepQSKI (Tm multi-shape
  tree-wide, unavoidable). FIX = `renaming (Tm to Tm⟦27e68fcc⟧)` (FUSepQSKI.Tm shape=27e68fcc) + replace body `Tm`→
  `Tm⟦27e68fcc⟧` (8/16/12 refs resp; atom/app NOT flagged, stay bare). ⟦⟧ valid in Agda idents (tree has Wedge⟦hash⟧).
  Checker only needs `renaming (Tm to <x>)` present (greps source name); a clean alias would pass but ⟦shape⟧ honors intent.

**FU DONE** (d934069). Reusable patterns proven: Magma-dedup-to-canonical clears collateral at source; distinct-shape
locals PIN via def-rename (Two→Bit2, Setoid→EqSetoid, _~_→_~ₛ_ — protects pre-existing importers); multi-shape imports
shape-specialize via `renaming (X to X⟦hash⟧)` (get hash from the decl's ⟦shape:⟧ tag; checker only needs the renaming
present). Collapse-check leaf/def-name-overlap warnings are ADVISORY (non-blocking) — the parallel η-proofs are the
intended preserved alternate-paths. **Commit's forced full-build takes ~4min — use timeout 600000 on `git commit`.**

**S5 cluster (15 modules) — DONE, commit c3d18a3 (full build 1745/1745 PASS).** Ⓜ.home-bare COMPLETE:
all 35 z47 bare modules conformed (FU d934069 + S5 c3d18a3). Residual advisories (NON-blocking, noted for
Ⓜ.dedup-pass): S5TorsorWireV4's `KleinV4` is a V4 reuse-point (relate to Groups.V4 via iso like V4FullCocycle;
also clears the categorical-grounding FLOATING advisory); many imported-by-0 leaves + def-name overlaps are the
intended preserved alternate-paths (parallel implementations of the same propositions across corpora).

_(historical detail below.)_ DAG: **S5Verdict is the ROOT** (mini-foundation: inlines ℕ/_+_/≡/sym/trans/
cong/List, all dependents pull stdlib from it via `using`). S5Fixpoint provides ⊥/Dec/yes/no; S5Real provides
CoTrace/List/head/tail/take/cycle; S5Regress provides Σ/_,_. Dependents of S5Verdict: ALL 14. Also S5RealConv→S5Real;
S5RegressFix,S5TwoFuelFix→S5Fixpoint; S5Section→S5Regress.
- **DONE: Substrate.S5.S5Verdict** (conformed + builds green, working-tree UNCOMMITTED). Pattern that WORKED and is the
  cluster key: route inlined stdlib to Foundation and **RE-EXPORT publicly** (`open import Foundation.X using(...) public`) —
  so dependents' `open import S5Verdict using (_≡_;refl;sym;trans;cong;ℕ;zero;suc;List;[];_∷_)` keep resolving with only a
  module-path change, no using-list surgery. Kept domain: Progress/Verdict/Machine/sum. `_+_` fixity matches Foundation.Nat (infixl 6).
- **REMAINING 14 — FULL PER-MODULE SPEC (intelligence gathered; execution is mechanical):**
  Foundation routing targets CONFIRMED: Bool→Foundation.Bool(true;false); ⊥→Foundation.Empty; Dec→Foundation.Negation
  (Dec;yes;no — SAME shape as S5Fixpoint's, dedups); List→Foundation.List; ℕ/_+_/≡/etc via S5Verdict re-export.
  **PROVIDERS (conform first, re-export public):**
    · S5Fixpoint (tier-1; provides ⊥/Dec/yes/no + Bool to S5RegressFix,S5TwoFuelFix): delete data ⊥/Dec/Bool + local _+_;
      `open Foundation.Empty using(⊥) public`, `Foundation.Negation using(Dec;yes;no) public`, `Foundation.Bool using(Bool;true;false) public`;
      route _+_→Foundation.Nat if used.
    · S5Real (tier-1; provides CoTrace/head/tail/take/cycle/List to S5RealConv): delete data List; `Foundation.List using(List;[];_∷_) public`;
      CoTrace etc are DOMAIN (keep). --guardedness.
    · S5Regress (tier-1; provides Σ/_,_ to S5Section): local `record Σ`(π₁/π₂,ctor _,_) + `record _×_`(fst/snd,ctor _,_) + `data ⊥` + `¬_`.
      DEDUP both to Foundation.Product `renaming (proj₁ to π₁; proj₂ to π₂)` — BUT its _×_ body uses fst/snd, so normalize
      those to π₁/π₂ OR (cleaner) rename proj→fst/snd and Σ-body π₁/π₂→fst/snd. Pick ONE proj pair per module, align body.
      ⊥→Foundation.Empty; ¬_→Foundation.Negation(¬_). Re-export Σ;_,_ public. Uses `S5Verdict.Machine` qualified → alias S5Verdict.
  **PRODUCT-RECORD dedup rule (the fiddly part):** every S5 `record Σ`/`record _×_` is structurally Foundation.Product but
    with idiosyncratic proj names/ctors — S5RealConv ×=fst/snd; S5Regress Σ=π₁/π₂ ×=fst/snd; S5RegressFix ×=fst/snd;
    S5TwoFuel ×=fst/snd Σ=π₁/π₂ ctor ⟨_,_⟩; S5TwoFuelFix ×=fst/snd; S5TorsorBridge/WireV4 Σ=fst/snd. DEDUP each to
    Foundation.Product with `renaming (proj₁ to <fst|π₁>; proj₂ to <snd|π₂>)` matching the module's dominant name; normalize
    the minority proj-name + any `⟨_,_⟩`→`_,_` in the body. (These ARE structurally identical → dedup, not pin, per the directive.)
  **SIMPLE tier-1 (S5Verdict only):** S5Carrier (delete local `data List`→use re-exported), S5EEA (path-change only),
    S5Matrix (path-change only), S5Nerve (`record Monoid` bundled M/_∙_/ε/assoc/unitˡ/unitʳ — DIFFERENT shape from
    Algebra.Monoid[Semigroup-based] → PIN: rename local Monoid→`MonoidR` or dedup if worth it; leaf, contained),
    S5TorsorBridge/WireV4 (Σ dedup as above; CHECK for Groups.V4 reuse-point — may relate via iso like V4FullCocycle),
    S5TwoFuel (Bool+Σ+× dedup).
  **tier-2:** S5RealConv(→S5Real; ×dedup), S5RegressFix(→S5Fixpoint ⊥/Dec; ×dedup), S5Section(→S5Regress Σ; uses
    S5Regress.Regress+S5Verdict.Machine/resume qualified→alias), S5TwoFuelFix(→S5Fixpoint; Bool+×+List dedup).
  Build tier-by-tier via membudget; then decl_shape_tag/sppf/gates (expect import-shape residuals like FU — resolve by
    dedup-to-canonical/pin); commit (forced full-build ~4min, timeout 600000).

## Drift / L₇ events
- None yet. The migration entailment (S1→S2→S3) is consistent with the user's original request; no forced snap.
