---
name: project_session_handoff_2026_06
description: "HANDOFF — what landed in the memory-architecture/opacity session, what's DONE (don't rebuild), what's deferred. Read this first to avoid re-deriving finished work."
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Purpose: the root cost the user cares about is DISCOVERABILITY — past
sessions blow context near wrap-up before recording what got built, so the
next session re-derives it (this session nearly rebuilt `act-hom` and the
AsFunctor cone, both already done — see
[[discipline/feedback_cluster_means_find_apex]]). This note is the cheap
index so that doesn't repeat.

ALL WORK IS COMMITTED on branch `session/memory-arch-and-policy` (11 commits,
47ebf28..9fad09f). Tree clean, `make check` green. NOT merged to main; NOT
in All.agda (never build All.agda — [[feedback_never_build_all_agda]]).

**DONE — do NOT rebuild (verify with git log / the named module):**
- Realizability Charter §4+§5 ([[project_realizability_charter_arc]]).
- def/proof separation policy + linter + git pre-commit hook (core.hooksPath
  .githooks) + `make check` aggregate gate. ([[feedback_def_proof_separation_lever]])
- Memory-confined per-dir Makefile build (gen_build_makefiles.py; one agda
  process per file, capped). ([[project_makefile_per_dir_build]])
- OOM root cause = super-linear normalization (powers), NOT load inflation.
  ([[project_oom_load_bound_finding_2026_06]], [[project_cyclen_opacity_fix]])
- Sealed: linear-from-images (d436788, fan-in 213), cyclic-Linear/HasOrder
  (48933ab). FreeLinearization inherits the seal (no action needed).
- SingerOrder: regression from the seal PAID DOWN structurally (Point-bridge,
  304db5c) + decomposed per theorem-per-file into SingerOrder/ (3445d07).
- AsNamed family COMPLETE: Functor/Dagger/SymmetricMonoidal/NaturalTransformation.
- HigherArity ladder collapsed to generic normalize-chain (9fad09f).
- ALREADY-EXISTING (found, not built): S3-on-V4 `act-hom` (the general
  S₃→Aut(V₄) homomorphism law, live); AsFunctor cone (Functor.AsNamed).

**POLICIES (enforcement state):**
- BLOCKING (hook + make check): def/proof separation, makefile-sync.
- ADVISORY (make advise): file-size / theorem-per-file pressure (~58 files).
- DOCUMENTED, not gated: super-linear opacity (seal ×/^/tetration; +
  transparent — [[feedback_opacity_tracks_blowup_not_layer]]); the offensive
  sparse-by-construction + transparent-metadata frame
  ([[feedback_sparse_concrete_transparent_metadata]]).

**DEFERRED / open (genuine next work, NOT yet done):**
- Fielded-schema prose cleanup of the ~12 AsFunctor projection files
  (designed, only LieAlgebra trimmed). Cosmetic, low-variance.
- Super-linear-opacity MIGRATION of existing *-Linear defs (high-variance,
  per-case-verify, never batch). Policy exists; sweep doesn't.
- Sparse-by-construction operators / dense materialized opaque-on-demand
  (the offensive architecture; real arc, not started).
- SingerOrder-style decomposition of other multi-theorem files (advise list:
  Charter 42 sigs, ShadowArchitecture cluster, etc.) — judgment per file.

**METHOD lessons this session (all recorded):** verify cold-vs-cold (warm
caching invalidates A/B); a cluster means FIND THE APEX before building;
needing targeted edits = file too large; opacity HIDES blow-up while sparse
ELIMINATES it; in Agda `opaque` = lazy-eval-with-metadata-interface, and a
consumer needing `unfolding` = a metadata-interface gap.
