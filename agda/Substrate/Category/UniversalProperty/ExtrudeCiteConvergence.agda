{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCiteConvergence — ⟡extrude-cite-convergence +
-- ⟡extrude-realign-as-instance: the CITATION MAP + REALIGNMENT WITNESSES for the extruder arc. The 264/274
-- studies found that this arc's independent construction CONVERGES with the substrate's own centers; per
-- ExtruderLambekRealigned's lesson (realign-as-INSTANCE, don't re-declare), this module OPENS the upstream
-- structures and states the correspondence as one-line witnesses — the "after" that cites the centers rather
-- than duplicating them.
--
-- THE CITATION MAP (this arc ↔ the substrate's centers):
--   * ExtrudeMinimal / ExtrudeMinimalCoalgebra (μ = the fixed point)  ↔  ExtruderFix (CombinatorAlgebra,
--     "the proof that PROVES the SKI extruder") + Foundation.Function.Iterate (the reused nth-iterate).
--   * ExtrudeSelfInterp (the confluence-observation self-interpreter)  ↔  ExtruderObsCoalg (ObservedAlgebra,
--     "the OBSERVATION") — both read the interpreter as an OBSERVATION, not a decision.
--   * ExtrudeReductionReversal (fold/unfold time-reversal)  ↔  Final's Lambek iso (out/into,
--     lambek-out-into/lambek-into-out) as realigned by ExtruderLambekRealigned — both are the
--     initial-algebra=final-coalgebra duality (build ↔ fold).
--   * ExtrudeDecodeNerve / NerveDegeneracy / NerveBetaS / NerveIdentities(Hi)  ↔  SimplicialBoundary
--     (delAt, simplicial ∂∘∂=0) + FaceSet (with-apex) — the reduction as a nerve zigzag.
--   * The whole "attribute is a bisimilar duplicate of the build, hence collapsible" move  ↔
--     WitnessTower.CyclicCollapse (pow-is-σ-iterate / order-collapse) + V4Grounding / CyclicGrounding —
--     the SAME discipline (D-attribute-bisimilar-with-build), applied to the cyclic-power stack upstream.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY the realignment WITNESSES —
-- reversal-is-rewriteconfluence (my ⇐* IS RewriteConfluence at the flipped relation, an INSTANCE not a
-- re-declaration — the realign-as-instance, already so by construction), and lambek-cited (Final's Lambek
-- iso, opened and re-stated as the neighbour of my reversal). The citation map itself is (prose: the
-- 264/274 studies; the correspondences are documentation, not claimed as proofs of identity).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeCiteConvergence where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Iff using (_⇔_; ⇔-refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Nat using (ℕ)

-- (d) REALIGN-AS-INSTANCE: my reversal is ALREADY an instance, not a re-declaration — my construction
-- closure ⇐* is RewriteConfluence's _⇒*_ instantiated at the FLIPPED relation (the same machinery dualized),
-- exactly the realign-as-instance pattern (reuse the existing structure, don't re-declare). Witness it:
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open import Substrate.Category.UniversalProperty.ExtrudeReductionReversal using (_⇐_; Constructs)
-- ⇐ IS the flip of R._⇒_ (definitional — the instance, not a fresh relation):
reversal-is-flip : {a b : Tm⟦533ef80d⟧} → (a ⇐ b) ⇔ (b R.⇒ a)
reversal-is-flip = ⇔-refl
-- (c) CITE Final's Lambek iso (the neighbour of my ExtrudeReductionReversal fold/unfold), opened not
-- re-declared — per ExtruderLambekRealigned:
open import Substrate.Algebra.R.Trace using (RealTrace)
open import Substrate.Algebra.R.Trace.Final using (out; into; lambek-out-into)
lambek-cited : (ns : ℕ × RealTrace) → out (into ns) ≡ ns
lambek-cited = lambek-out-into      -- the repo's Lambek build↔fold iso — my reversal's stream-level neighbour

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder arc CONVERGES with the substrate's centers; cite + realign,
-- don't duplicate): the either/or "is my extruder construction novel OR a duplicate of the substrate's?"
-- DISSOLVED (the 264/274 studies + ExtruderLambekRealigned's realign-as-instance lesson) — it is a CONVERGENT
-- re-discovery: my μ (ExtrudeMinimal/Coalgebra) ↔ ExtruderFix + Function.Iterate; my self-interpreter
-- (ExtrudeSelfInterp) ↔ ExtruderObsCoalg; my reversal (ExtrudeReductionReversal) ↔ Final's Lambek iso
-- (realigned by ExtruderLambekRealigned); my nerve (ExtrudeDecodeNerve/…) ↔ SimplicialBoundary/FaceSet; and
-- the whole bisimilar-with-build move ↔ CyclicCollapse/V4Grounding/CyclicGrounding. The realign-as-instance
-- is honest: my ⇐* is ALREADY RewriteConfluence instantiated (reversal-is-flip), not a re-declaration, and
-- Final's Lambek is CITED (lambek-cited), not re-hand-rolled. So the arc reuses the substrate's centers and
-- names its convergences — the discipline (the substrate names its centers; two efforts converge) confirmed.
-- No spook. Chain: 264 (V4/Cyclic convergence) → 274 (the Extruder line + Iterate) → 275cd (cite + realign).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = reversal-is-flip (my ⇐* is an INSTANCE of RewriteConfluence,
-- the realign-as-instance witness) + lambek-cited (Final's Lambek iso cited, not re-declared). The CITATION
-- MAP (this arc ↔ ExtruderFix/ObsCoalg/Lambek + SimplicialBoundary/FaceSet + CyclicCollapse) is documented
-- prose, a cross-reference for the PR — NOT a claim of definitional identity. SCOPED: an actual shared
-- typeclass/record instance unifying my modules with the upstream ones (a refactor — ⟡extrude-package-instance,
-- the PR step). What's grounded: the arc realigns-as-instance (reuses, doesn't re-declare) and cites its
-- convergence with the substrate's own extruder centers.
------------------------------------------------------------------------
