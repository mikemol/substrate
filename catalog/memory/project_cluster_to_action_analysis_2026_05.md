---
name: cluster-to-action-analysis-2026-05
description: "First post-decomposition similarity-cluster sweep + iterative SPPF-walk through every cluster. Catalogues which clusters yielded quotients, which were deferred, which had verdicts retracted, and why — for future passes. Methodology distilled separately in [[project-cluster-action-methodology]]."
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

**Status: SPPF-walk complete (2026-05-22).** Originally a first-pass cluster sweep that classified 22 clusters into 4 buckets (yielded / minimum / heterogeneous / new-content-needed). After the user's pointer to look at parse sub-trees instead of whole files — and via three follow-on commits applying the SPPF lens — six of the "deferred" or "heterogeneous" verdicts were retracted and produced extractions. Methodology now lives in [[project-cluster-action-methodology]].

After the section-then-lemma decomposition round (Cluster 5/7/9/15 from this session's own work, see commits ff4b0fe..62f7404), ran `--cluster --cluster-percentile 99 --cluster-min-cohesion 0.40` over the 1195-file corpus. 22 clusters surfaced. Outcomes:

**Yielded parametric quotient:**
- Cluster 16 (`Cycle{3,4,5}`, plus `Cycle2`/`Cycle7`, commit 455ff7e): `cyclic-Linear` + `cyclic-HasOrder` lifted into `Cyclic.agda` as parametric. All five Cycle{N} collapsed to 4-line thin renamings. Cycle2/Cycle7 gained the Linear + HasOrder lifts (chirality completion).
- Cluster 14 (`RotPow` / `SwapPow`, commit 455ff7e): new `Generators/IterPow.agda` exposes `iter-pow : (V₄ → V₄) → Word G → V₄ → V₄`. Both `*-pow` files collapsed to one-line renamings; downstream `RotPowSwapTwist` typechecks unchanged (definitional equality preserved).
- Cluster 9 (`HigherArity/{Triple, Quad, Quint, Sext, Sept}`): the EARLIER first-pass dismissal was wrong. The correct quotient was NOT Vec-parametric (which would have hit a consumer-cost objection); it was a single `normalize-cons` arity-step combinator in `HigherArity/Step.agda`. Every leaf reduces to `normalize-cons a (previous-arity ...)` — consumer surfaces preserved. Diagnostic for catching this kind of dismissal: when leaf bodies are ALL exactly the same `trans (X-helper a _) (Y-cong (f a) _)` shape, that shape literally IS a combinator; not extracting it is rigidification, not pragmatism.
- Cluster 3 (`Category/*/AsFunctor`, ~10 files, plus JordanAlgebra/UnderlyingCNAA, Coxeter/AsCartanType/Functor, CartanType/AsCoxeter/Functor): new `Category/Functor/AsNamed.agda` is the missing 1:N cone witness for substrate-level naming of a Functor, mirror of the existing `DaggerCategory/AsNamed` and `SymmetricMonoidal/AsNamed`. Each AsFunctor leg now `open import Functor.AsNamed S T F public renaming (named-Functor to X-Functor)`, parallel to how HodgeStar/AsDaggerEndomap opens DaggerCategory.AsNamed. Plus chirality completion: new `CartanType/AsCoxeter/Functor.agda` mirrors `Coxeter/AsCartanType/Functor.agda` (the latter's comment explicitly listed the backward functor as "downstream slices").

**Structural orbit but quotient deferred — REASON saved so we don't re-investigate:**
- Cluster 13 (`S3-on-V4/Composition/Block{00, 01, 10, 11}`): commit 38a3cac. Two earlier dismissals retracted — the second attempt's "Agda normalize-idem reduction blocks extraction" was correct IN THE SCOPE I TRIED (extracting the full chain including the H-side `act → act-on-canonical` step) but wrong as a general claim. The right factoring splits the chain at the natural seam: the H-side `act-equals-pow` step happens per-callsite (with its specific h₂-canonical witness), then the N₁-side 3-step rot-pow chain `(cong normalize-idem) ∘ (sym rot-pow-normalize-eq) ∘ rot-pow-append` extracts cleanly as `rot-pow-compose-chain n₁ n₂' v'` parameterised by both `n₂'` (which carries the dihedral-twist delta: `Z₃.normalize n₂` vs `Z₃.inv (Z₃.normalize n₂)`) and `v'` (which carries the right-swap delta: `v` vs `swap-αβ v`).

  All 4 Blocks now go through the helper. Each Block's LHS-to-pow is now `trans (act-equals-pow ...) (trans (rot-pow-compose-chain n₁ n₂' v') <case-specific-delta-tail>)`. Block00's tail is just `sym (cong rot-pow-normalize-eq n₂)`; Block01 has the same with `swap-αβ v`; Block10/11 add `Z₃.canonical-is-fixed` + `rot-pow-swap-twist` + (Block11 only) `swap-αβ²-id` — every one of those is already a named primitive. After this slice the deltas are visible AT THE CALL SITE as the symmetry-breaking content of each case; the boilerplate has a substrate-level name.

  Methodology diagnostic for the next pass: when extraction "fails" at first attempt, look for a SUB-CHAIN within the chain that doesn't cross the problematic boundary. Here the boundary was the H-side normalize-idem; pulling the helper to start AFTER that boundary side-steps it entirely.

  Tool note: `git diff --no-index --word-diff=plain --word-diff-regex='[A-Za-z][A-Za-z0-9_₁₂₃₄₅₆₇₈₉αβγδ-]*'` is the right intra-line diff invocation when line-level `--typed-holes` falls back to single-hole.
- Cluster 6 (`S3-on-V4/Hom{Rotations, Swaps}`): same `v4×v4-cover (16 refls)` shape across 5 files. Generic quotient requires a proof that `act-on-canonical N H` is a V₄-automorphism for ALL canonical (N, H) — that proof doesn't exist yet. Adding it is REAL NEW CONTENT, not a refactor. Defer until a consumer needs the generic.
- Cluster 1 (`As*` category-instance, 21 files): per the skill's orbit-saturation diagnostic (rule 6), this is S2G classification (orbit-cataloguing) not RFS extraction. The universals are already extracted: `Category/X/AsNamed` for the AsNamed family (DaggerCategory, SymmetricMonoidal), and the bundled `F2LinearCategoryStructures` record for the F2.Linear projections. Each leg is at minimum line count: `open + rename` or single-field-access. The 21 files ARE the canonical projections; per-file granularity gives consumers single-import access.
- Cluster 2 (Raven `Stanza{I..XVIII}`, 18 files): same orbit-saturation classification. Universal `mk-stanza` already extracted (in Raven.Grammar); each leg is `stanza-N = mk-stanza ( <site-specific-6-line-sequence> )`. Consumed BOTH as the bundled `raven : Vec Stanza 18` (Raven/Poem/Raven.agda) AND individually by `Semantics/Cotypes.agda` (`cN = interpret-stanza stanza-N cN-prev`). The per-file granularity is load-bearing.

**Not quotient candidates (content stubs / intentional test cases):**
- Cluster 4 (`Category/HC/*`): all 9 are 4-line placeholder stubs awaiting future content. No quotient smaller than current.
- Cluster 11 (`Lojban/Fragment/Example*`): concrete sentence demonstrations. Different content; uniform shape is intentional.
- Cluster 22 (`Pipeline/Examples/*`): demo Brick instances with different runtime types. Each is a parametric module; the "parametric" stays at the module level.
- Cluster 2 (Raven `Stanza{I..XVIII}`): 18 poetic stanzas with parallel structure. Content, not quotient.

**Chirality solos found across whole codebase, both deferred:**
- `bilinear-modify-linear-right` in `TokiPona/ModifierBilinear/WithBasisAction.agda`: explicit coalgebraic-deferral comment ("lands when a consumer needs it" per [[feedback-coalgebraic-not-consumer-driven]]).
- `shift-to-suc-on-left` in `F2/Polynomial.agda`: NOT a true chirality marker — it's a type-level cast through `+-comm`. The `-left` suffix describes the direction of the shift, not a missing mirror.

**How to apply:** When running cluster mode in the future and seeing one of these clusters resurface, refer here BEFORE attempting a refactor — the deferral reason is recorded. If the deferral reason has changed (e.g. a generic V₄-automorphism is now available), revisit.

**Cluster 12 (JointGen × 4)**: commit c70b274. The four sites each inlined the same 7-line body `joint-gen-from-presentation-≡ gen _·_ ε Sylow-pred gen-sylow represent represent-correct`, varying only in (carrier, nSylow, nGen). The K-parametric wrapper was IMPLICIT — buried as `Generic-Descent` inside HappyFamily/JointGenViaDescent. Extracted to `Substrate.Category.PrimeFactoredGauge.JointGenWrapper`; each site now `open + rename`. Z6: (2, 2). Z30: (3, 3). Monster: (15, 16). HappyFamily descent: abstract.

**Phenotypical-naming methodology (internalized).** The criterion is NOT "the cluster has visible duplication" — it's "what's the smallest unnamed structurally-meaningful entropy here?" Procedure:
1. Use `git diff --no-index --word-diff=plain --word-diff-regex='[A-Za-z][A-Za-z0-9_₁₂₃₄₅₆₇₈₉αβγδ-]*'` between cluster members to see sub-expression deltas
2. Identify what's CONSTANT across members (the common micropattern) and what VARIES (the symmetry-breaking deltas)
3. If the common pattern has no substrate-level name → that's the extraction target
4. If the deltas all map to already-named primitives → those are the case-content; nothing further to name
5. When an extraction "fails" at first attempt due to definitional-equality obstacles, look for a SUB-CHAIN within the chain that doesn't cross the problematic boundary

**Re-walked clusters in this session (post-systematic application):**

*Cleanly extracted:*
- Cluster 3 (AsFunctor × 13): `Functor.AsNamed` cone witness — commit aba3894
- Cluster 9 (HigherArity × 5): `normalize-cons` arity-step — commit afc9216
- Cluster 12 (JointGen × 4): `JointGenWrapper` K-parametric — commit c70b274
- Cluster 13 (Block grid × 4): `RotPowComposeChain` 3-step shared chain — commit 38a3cac
- Cluster 14 (Pow × 2): `iter-pow` — commit 455ff7e
- Cluster 16 (Cycle{N} × 5): `cyclic-Linear` / `cyclic-HasOrder` — commit 455ff7e

*At minimum form (orbit-saturation; universal already extracted, deltas are intentional):*
- Cluster 1 (As* × 21): universals are `Category.X.AsNamed` family + `F2LinearCategoryStructures`
- Cluster 2 (Raven Stanzas × 18): universal `mk-stanza`; consumed individually by Cotypes
- Cluster 4 (HC stubs × 9): placeholders awaiting proof content
- AsField/AsModule/AsLinearAlgebra across F1/F2/Q: each record-instantiates LinearAlgebra/Field/Module per field; record-syntax IS the form

*Genuinely heterogeneous (similarity from boilerplate, not substructure):*
- Cluster 17 (Probability): different specific theorems/abstractions
- Cluster 18 (UP Powerset/Sheaf/InternalHom): different topos UP signatures
- Cluster 19 (Z2-on-Z3 Act*): different action-property proofs
- Cluster 21 (Linguistic 2-cat ops): different bicategorical operations
- Cluster 22 (Pipeline Examples): different demo bricks
- Cluster 8 (Sporadic × 5): different sporadic-group algebraic structures
- Cluster 11 (Lojban Examples): different concrete sentences

*Real common micropattern but extraction has substantial cost:*
- Cluster 20 (Capabilities × 3): each has different `from-coxeter-data` signature for different capability records. The common meta-pattern "every Zₙ Coxeter supplies a capability of each kind" could become a `CoxeterSystem` record + capability-instance derivation, but this is architectural work.

**Cluster 6 (Hom × 5) — VERDICT RETRACTED, NOW EXTRACTED**: commit a82e1d6. The earlier "needs generic V₄-automorphism theorem, real new content" was wrong. The shared sub-tree across the 6 Hom files (HomId + 5 v4×v4-cover proofs) was the GOAL TYPE — `∀ v₁ v₂ → f (v₁ V4.· v₂) ≡ f v₁ V4.· f v₂` — which is just `IsHomomorphism f`, a 1-line predicate definition. Extracted to `Substrate.Groups.V4.IsHomomorphism`; every Hom file's signature now reads `hom-X : IsHomomorphism (act-on-canonical N H)`, making the (N, H) pair the visible delta and the predicate shape a single named sub-tree.

**Cluster 10 (Z_n-Coxeter × 5) — SPPF-level shared sub-tree extracted**: commit 546cfc3. The 2-line `gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂); gen-≟ a a = yes refl` was inlined identically in all 5 Z_n-Coxeter files. Lifted to `Coxeter/Cyclic/Base.agda` (where Gen lives); every Z_n inherits via the existing `open import Cyclic n public`. Five-way duplication → one source.

**SPPF methodology (user's deepest framing).** The criterion is not "the cluster has visible duplication at the file level" — it's "imagine parsing all the Agda code and taking the maximally-shared parse forest. Every sub-tree shared across multiple sites is a candidate node-merge. Name them all." Procedure:
1. Compare cluster members with `git diff --no-index --word-diff=plain --word-diff-regex='[A-Za-z][A-Za-z0-9_₁₂₃₄₅₆₇₈₉αβγδ-]*'` — shows sub-token deltas, not just line deltas.
2. Look at goal TYPES specifically — often shared predicate-shapes even when proof bodies differ. The Cluster 6 fix was exactly this.
3. Look at SMALL recurring sub-trees (2-line functions, single-pattern-match dispatchers) — not just whole files. The Cluster 10 gen-≟ fix was exactly this.
4. "Boilerplate" is the lazy verdict. Every recurring sub-tree is a candidate name. The "heterogeneous" classification is suspect until each cluster has been SPPF-walked.
5. The genuine blocker condition is Agda's expressive ceiling (no polymorphic pattern synonyms, no source-level macros, definitional reduction limits at problematic boundaries) — not "would be new content," not "preserves intentional design," not "differs in proof technique."

See also: [[feedback-section-then-lemma-for-parametric]], [[feedback-chirality-pair-completeness]], [[project-named-categorical-structure-skeletons]].
