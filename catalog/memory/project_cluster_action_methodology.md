---
name: cluster-action-methodology
description: "How to translate a high-similarity cluster from agda_similarity.py into structurally-meaningful action — the SPPF lens, delegate-to-existing rule, and the four kinds of extraction the substrate has actually produced. Distilled from the 2026-05 cluster sweep (19 commits across 3 arcs)."
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

This memory captures the **methodology pattern** that ran through the 2026-05 cluster sweep. Use it before any future cluster-driven refactor.

## The end-to-end loop

1. **Run cluster mode.** `python3 scripts/agda_similarity.py --glob 'agda/Substrate/**/*.agda' --cluster --cluster-percentile 99 --cluster-min-score 0.40 --cluster-min-cohesion 0.40 --cluster-min-size 3`. Yields ~20–25 clusters of mutually-near-neighbour files; singletons are filtered out.

2. **Survey, don't dismiss.** For every cluster, the FIRST guess is wrong as often as it's right. "Heterogeneous" / "already at minimum" / "needs new content" were each wrong twice in the 2026-05 sweep. Re-walk every cluster with the SPPF lens before declaring it inert. (See "Verdict retractions" below.)

3. **SPPF lens: look at sub-trees, not whole files.**
   - `--typed-holes --skeleton` on the cluster's members: shows per-position holes when residue counts align.
   - When `--typed-holes` falls back to single-hole (residue counts differ across files), use `git diff --no-index --word-diff=plain --word-diff-regex='[A-Za-z][A-Za-z0-9_₁₂₃₄₅₆₇₈₉αβγδ-]*'` between pairs. This surfaces sub-TOKEN deltas — the "what breaks the symmetry" content (per the user's phenotypical-naming framing).
   - The shared parse sub-trees across the cluster are the structurally-meaningful entropy; the deltas are the case-specific content.

4. **Goal-type analysis.** When the proof BODIES differ wildly but the signatures all share the same shape `∀ ... → P (something) ≡ ...`, that signature shape IS the shared sub-tree — give it a name. This was Cluster 6: every Hom file had a different (N, H) and proof technique, but the goal type was always `∀ v₁ v₂ → f (v₁ · v₂) ≡ f v₁ · f v₂` = `IsHomomorphism f`. One-line predicate definition, 6 leg files refactored.

5. **Delegate to existing primitives FIRST.** Before designing a new abstraction, search the substrate for an already-extracted form. The c-pos migration was 90% migration / 10% verification: the parametric `c-pos k` had existed in `Coxeter.Cyclic.Existential` since the original Cyclic module was written; the per-Z_n `c-ε / c-a / c-aa` ladder was orphan-duplication of work the substrate had already paid for. Same for Fin.Cover's `fin×fin-cover` — already there, but `is-symmetric-bridged-{3,4}` were inlining their own 9-/16-case dispatchers.

6. **If extraction is needed, classify by shape.** Four kinds the substrate has produced:

   | Shape | When it fires | Substrate-named example |
   |---|---|---|
   | **1:N cone witness** (AsNamed) | Same record-naming structure used at N sites with a substrate-renaming on the output | `Category.Functor.AsNamed`, `Category.DaggerCategory.AsNamed`, `Category.SymmetricMonoidal.AsNamed` |
   | **K-parametric wrapper** | N sites apply the same universal-of-the-substrate with their own deltas | `JointGenWrapper`, `cyclic-Linear` / `cyclic-HasOrder`, `iter-pow` |
   | **Arity-step combinator** | Inductive ladder (Triple → Quad → Quint → Sext → Sept) where each step has the SAME shape | `normalize-cons` in `Coxeter/Core/HigherArity/Step.agda` |
   | **Sub-chain extraction** | Long proof chain where a sub-sequence of rewrites recurs across multiple proofs | `rot-pow-compose-chain` in `S3-on-V4/Composition/` |
   | **Predicate naming** | N goal-types share the same shape (parametric in site-specific arguments) | `IsHomomorphism` |

7. **Mass migration: scripts + verify-loop.** When the cluster has 10+ leg files, write a Python heredoc that does the substitution mechanically. Verify each affected file compiles. Fix import statements per-file. Don't try to do the migration as 10+ separate `Edit` operations.

8. **Commit per arc with detailed message.** Each session-arc gets its own commit; the message explains the COMMON micropattern that was named, the DELTAS that remained at each callsite, and any retracted earlier verdict.

## Verdict retractions in the 2026-05 sweep

Each is a case where my first-pass classification was wrong:

- **Cluster 1 / Cluster 2 "intentional design"** → mostly correct, but used wrong vocabulary ("intentional design" should be "S2G orbit-cataloguing where the universal is already extracted"). The 21 As* files and 18 Raven stanzas are indeed at minimum, but for the SPECIFIC reason that `Category.X.AsNamed` and `mk-stanza` are already the universals.
- **Cluster 6 "needs generic V₄-automorphism theorem, real new content"** → wrong. The shared sub-tree was the goal-type, not the proof body. `IsHomomorphism f` is a 1-line predicate, not new content.
- **Cluster 9 "Vec-parametric forces consumer-side conversion"** → wrong. The correct quotient was `normalize-cons` (an arity-step combinator), not Vec-parametric.
- **Cluster 13 "case-analysis IS the work"** → wrong twice. First attempt (full LHS-chain extraction) was correctly blocked by Agda normalize-idem, but second attempt at sub-chain-after-the-boundary (`rot-pow-compose-chain`) worked. The lesson: when an extraction "fails," look for a SUB-CHAIN that doesn't cross the problematic boundary.

The pattern: **first-pass dismissals were wrong as often as they were right.** Re-walk every cluster with the SPPF lens; check whether the substrate has already paid the design cost; consider goal-type-shape extraction; consider sub-chain extraction within proof bodies.

## When NOT to extract

Discipline rules that defended valid no-extract decisions in the sweep:

- **Orbit-saturation (rule 6 from `regroup-from-shadows` skill).** When the N instances all have the form `<universal> <site-args>`, and `<universal>` is already named, the N instances are S2G orbit-cataloguing, not RFS record-extraction. The 21 As* projection files and 18 Raven stanzas are this case. Extracting a wrapper would add a layer with no structural payoff.
- **Coalgebraic deferral (per [[feedback-coalgebraic-not-consumer-driven]]).** Chirality solos like `bilinear-modify-linear-right` have an explicit "lands when a consumer needs it" deferral. Respect it.
- **Substrate-named-constant definitions** (e.g. `v4nz-γ = suc (suc zero)` or `b₀₃ = suc (suc zero)`). The explicit RHS bridges a domain name to a Fin position — substituting `₂` would obscure the bridge.
- **Agda-expressive-ceiling blockers.** Sometimes the extraction is genuinely blocked by Agda's expressivity (no polymorphic pattern synonyms across data types — Fin.Literals' `₀` only matches `Fin.zero`, not `Nat.zero`). When this happens, recognize it explicitly and DON'T force.

## Companion arcs and their cross-links

This methodology was distilled from three arcs that landed in 2026-05:

- [[project_cluster_to_action_analysis_2026_05]] — the original 22-cluster sweep with per-cluster classifications, methodology-evolution notes, and the diagnostic procedure for re-walking
- [[project_cpos_migration_arc]] — the migration of all 28 Z_n-Coxeter consumers from the legacy named ladder to `c-pos k`
- [[project_fin_literals_arc]] — `Foundation.Fin.Literals` subscript pattern synonyms + `fin×fin-cover` migrations

Related disciplines applied:
- [[feedback-section-then-lemma-for-parametric]] — for parametric modules: section split first, then file-per-lemma
- [[feedback-chirality-pair-completeness]] — solo `*-right` / `*-left` is a rigidification flag
- [[feedback-coalgebraic-not-consumer-driven]] — defer gauge structure unfolds until a consumer needs them
- [[project-named-categorical-structure-skeletons]] — the AsNamed pattern this session extended to `Functor.AsNamed`

## The user's framings that crystallized the methodology

Two pointers from the user that shaped the discipline:

1. **"What's the delta between cases is the load-bearing content; what's common is itself a substrate-level micropattern worth naming."** → led to RotPowComposeChain extraction (commit 38a3cac) and is the underlying logic for IsHomomorphism (a82e1d6).

2. **"We don't delegate enough to the term algebra."** → led to the c-pos migration (which discovered the substrate had already paid the design cost) and the Fin.Literals arc (using the substrate's own subscript-naming convention as the literal mechanism). The substrate's own primitives — `c-pos`, `cyclic-Linear`, `joint-gen-from-presentation-≡`, `fin×fin-cover`, `n-refls`, `copies`, `canonical-cover-ex` — are usually underused, not missing.

3. **"Take an SPPF of the parse forest of all the Agda code — that's the level of decomposition I'm driving at."** → reframed "heterogeneous" as a lazy verdict. Every shared parse sub-tree is a candidate name; the only genuine blockers are Agda's expressive ceiling, not file-level dissimilarity.

4. **"Extracting those kinds of common components will allow new clusters to form across the repo where recurrent patterns themselves get identified."** → iterated-SPPF: use typed-holes *within* enumeration-of-content clusters to find shared sub-expressions, extract them as named Foundation primitives, and re-run the similarity script. The adoption sites of the new primitive form the next round's clusters. See [[cong-trans-extraction]] for the worked instance (`trans (cong f X) Y` → `cong-trans f X Y`, 338 occurrences across 124 files; 6-file Lookup cohort migrated as seed; skeleton dump now shows literal 18/20-line identity across Swap/Cyclic siblings post-migration).
