---
name: feedback_graded_set1_dissolution_playbook
description: "the operational playbook for dissolving a Set₁ tier by the graded move — the census rule, the orphan-.agdai gotcha, and reuse-verifies-the-plan (from the ⟡C2g arc)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Dissolving a Set₁ record tier (the ⟡C2g arc: `BackedUP`/`UPArrow`/`Interop`/backings → graded `BackedUPᴳ`/
`UPArrowᴳ`/`GradedProductOver`; 697→653 Set₁ over ~15 commits) has a repeatable operational shape. The
strategy is [[set1-is-grade-collapse]] / [[set1-carrier-always-parameterize]] / [[feedback_route_through_witness_tower]];
these are the EXECUTION lessons that recurred and are non-obvious.

**Why:** each lesson cost a failed-commit cycle or a wrong-plan step until learned, and they generalize to any
graded-migration / dead-code-retirement in this repo.

**How to apply:**
- **The census rule (what `set1_ratchet_cores.py` counts):** a `: Set₁` RECORD, and a TERM whose type is a Set₁
  record (e.g. `theLimit : LimitUP`, `x-backed : BackedUP`) — these count. A def RETURNING `Set` (a `…→Set`
  family/predicate, e.g. `Admμ : ℕ×ℕ→ℕ×ℕ→Set`) does NOT count, nor does a term over a `…→Set` record
  (`b : BackedUPᴳ`, since `BackedUPᴳ … : Set`). CONSEQUENCE: to keep a graded module net-neutral, INLINE any
  Set₁-typed helper (`mediate (product-LimitUP …)` not `theLimit : LimitUP`); predicate families are free.
- **The orphan-.agdai gotcha:** deleting a source `X.agda` leaves `agda/_build/2.8.0/agda/…/X.agdai` — the
  ratchet reads it and REFUSES to certify ("incomplete census; rebuild cores"). `rm` the orphan cores before
  measuring/committing every deletion, else the paydown doesn't register (and the full build won't clean them —
  `full_build_check` walks SOURCES).
- **Reuse-search-VERIFIES-the-plan (plan = hypothesis):** an agent's "delete these N orphaned modules" repeatedly
  had a hidden pin caught only by a fresh `open import` grep — `NuRegistryEntry` was NOT pure-cons (its
  `nu-backed-ℕ`/`ℕ-coalg` fed the nu riders); the x8a chain carries an UN-MIGRATED uniqueness theorem so it stays.
  Before every deletion set, grep the ACTUAL importers (open-import, not comments) of each module AND confirm the
  survivors don't import the to-delete set. Retire is theorem-safe only for modules whose theorems were migrated.
- **The migration IS instantiation, not re-proof:** the µ⊣ν uniqueness re-homed by instantiating the witness
  tower's tier-free engines (`foldR-initial`, `trace-fold-unique`, `recon-bounded-unique`, `ana-unique`,
  `UniquenessStencil`, `Lawvere.TorsorAtom`/`prove-or-correct`) — never by porting the flat `solver-unique`. Sweep
  the witness tower + rig FIRST; the reusable center almost always exists ([[reuse-search-before-feasibility-conclusions]]).
- **Also:** the import-shape ratchet forces `renaming (Name to Name⟦shape⟧)` for colliding cross-tier imports
  (e.g. `Wedge → Wedge⟦478f66a6⟧`) — check `scratch/sppf_collision_index.md`; hit twice this arc.

**THE ⟡UPArrow-dissolve EXTENSION (2026-07-15, 641→565 −76, flat `record UPArrow : Set₁` DELETED):** dissolving a
record that is USED AS AN OBJECT TYPE (quantified over, stored, indexed by) across a large component has ONE
generator — **a Set-carrier is never a FIELD; it is a PARAMETER/INDEX/FAMILY** — at three arities, plus one gotcha set:
- **QUANTIFIER** (`{U : UPArrow}`, `F : UPArrow→Set`) → the TELESCOPE `{S T : Set}{W : S→T→Set}{U : UPArrowP S T W}`;
  projections `Source U`→`SourceP U` shims. Nearly all consumers are this (uncounted `…→Set` — they migrate only to
  UNBLOCK the record deletion, they don't themselves pay down).
- **SINGLE stored object** (`UPArrow².L0-Source : UPArrow` field) → **field→INDEX**: the objects become carrier PARAMS,
  only the genuine field stays ⇒ the record drops (UPArrow² Set₂→**Set₀**); the ex-fields become shim accessors.
- **FAMILY of stored objects** (`UPCover.source-UP : Idx→UPArrow`) → **carrier-FAMILIES** `Sc Tc : Idx→Set`,
  `Wc : (i)→Sc i→Tc i→Set`; the object at i is the trivial `mkUP {Sc i}{Tc i}{Wc i}`. **NO Σ-bundle** — the bundle
  (`Σ Set λ S→…`) IS the collapse the mission fights (rejected twice by the user as "the wall").
GOTCHAS: (a) UPArrowP is an ETA record (no fields) ⇒ Agda REFUSES `variable`-generalization over `{U : UPArrowP …}`
("Cannot generalize over U of eta-expandable type") — put S/T/W in the `variable` block but bind the OBJECTS
explicitly per signature. (b) A DATA family (`UPGen`/`UPTerm`) indexed by objects STAYS Set₁ even over the telescope
— the constructor re-quantifies `{W : S→T→Set}` (type Set₁) ⇒ `ConstructorDoesNotFitInData`; dropping it needs a
Set₀ index = ℕ-CODES (`data UPGen : ℕ→ℕ→Set` + `obj : ℕ→SpanData` MODULE param), the toN/fromN enumeration — a
SEMANTIC restriction to enumerable objects, defer it (`⟡UPGen-ℕ-index`). (c) define an `ObjRel` synonym for a fold's
binary-object motive to avoid telescope-explosion. (d) LEVEL RIPPLE: when a record drops a level (Set₂→Set₁),
consumers with explicit `Set₂`/`Set₃` annotations over it fail (`Set₁ != Set₂`, no cumulativity) — lower them; a
`… → SetN` function type over Setₙ things is itself Setₙ. (e) bulk-rename `\bSource\b` HITS `L0-Source` (the `-` is a
regex word-boundary but part of the Agda name) — scope renames.
THE METHOD that made the ~27-file topos migration tractable: `scratch/uparrow_refactor_path.py` decodes the current
`.agdai` cores (`jea_agdai.decode_core`, mirrors mat230 `gen_warrants.py`), harvests the real dependency edges, and
computes the consumer subgraph's SCCs + topological LAYERS = the mechanical migration order (it found **0 cycles** ⇒
layerable, NOT a flag-day). Re-run it to watch the consumer count → 0. `scratch/telescope_migrate.py` = the per-file
binder→telescope migrator (records still need hand field→index).

Relates to [[set1-carrier-always-parameterize]] (the generator), [[set1-is-grade-collapse]],
[[feedback_declaring_a_wall_is_the_rebuild_reflex]] (the wall-reflex fired ~4× this arc — "unavoidable bundle",
"genuinely Set₂", "flag-day", "~5-def core" — each a lowering in disguise), [[adjunction-is-the-wedge-residue-counit]]
and [[feedback_reuse_search_before_feasibility_conclusions]].
