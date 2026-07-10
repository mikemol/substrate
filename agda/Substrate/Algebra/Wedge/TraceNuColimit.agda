{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceNuColimit — ⟡nu-descending-colimit: the DESCENDING
-- chain ⋂ₙ Φⁿ⊤ and the GREATEST-fixed-point universal property, the dual of 159's
-- ascending Kleene colimit ⋃ₙ Φⁿ⊥ ≅ Trace. The LAST piece of the ν-half (157-161).
--
-- 159 (μ): Colim = ⋃ Φⁿ⊥ ("present at SOME stage") ≅ Trace = μΦ, the LEAST fixed
-- point. Here (ν): Limit = ⋂ Φⁿ⊤ ("present at EVERY stage"), the GREATEST fixed
-- point. The descending chain Φⁿ⁺¹⊤ ⊑ Φⁿ⊤ is Refinement.chain (the DESCENDING
-- direction) with the trivial pre-fixed-point Φ⊤ ⊑ ⊤.
--
-- DELIVERED (the TRUE dual): every ν-coalgebra X ⊑ Φ-step X sits BELOW the limit
-- (X ⊑ Limit) — the greatest-fixed-point UNIVERSAL PROPERTY (dual to μ's: μ below
-- every pre-fixed-point). HONESTLY SCOPED: Limit ⊑ Φ-step Limit (the limit is
-- itself a post-fixed-point/coalgebra) needs the done/step choice to STABILIZE
-- across stages (ω-co-continuity); for a general D the step-wedge at each stage may
-- differ, so this + the full Limit ≅ νΦ-step are the scoped remainder.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceNuColimit where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Category.Allegory.Refinement
  using (Fam; _⊑ᶠ_; ⊑ᶠ-refl; ⊑ᶠ-trans; Refinement; iterate; chain)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; Φ-step-mono; step-refinement)

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE TOP family ⊤ and the DESCENDING chain. ⊤-fam is present everywhere;
  -- Φⁿ⊤ is the descending chain (each stage prunes to "has a run of length ≥ n").
  ------------------------------------------------------------------------
  ⊤-fam : Fam (Idx D)
  ⊤-fam _ = ⊤

  -- ⊤ is a pre-fixed-point: Φ ⊤ ⊑ ⊤ (trivially — everything maps to tt).
  ⊤-pre : Φ-step D ⊤-fam ⊑ᶠ ⊤-fam
  ⊤-pre _ _ = tt

  -- THE DESCENDING CHAIN (dual of 159's ascending): Φⁿ⁺¹⊤ ⊑ Φⁿ⊤ — each stage
  -- refines. This is Refinement.chain (the descending direction) at ⊤.
  descending-chain : (n : ℕ) →
    iterate (step-refinement D) (suc n) ⊤-fam ⊑ᶠ iterate (step-refinement D) n ⊤-fam
  descending-chain = chain (step-refinement D) ⊤-pre

  ------------------------------------------------------------------------
  -- ② THE LIMIT ⋂ₙ Φⁿ⊤ = "present at EVERY stage n". The greatest-fixed-point
  -- candidate (dual of 159's Colim = "present at SOME stage").
  ------------------------------------------------------------------------
  Limit : Fam (Idx D)
  Limit i = (n : ℕ) → iterate (step-refinement D) n ⊤-fam i

  -- the limit projects to every stage (Limit ⊑ Φⁿ⊤ for each n).
  limit-projects : (n : ℕ) → Limit ⊑ᶠ iterate (step-refinement D) n ⊤-fam
  limit-projects n i l = l n

  ------------------------------------------------------------------------
  -- ③ THE GREATEST-FIXED-POINT UNIVERSAL PROPERTY (the TRUE dual of 159): every
  -- ν-coalgebra X ⊑ Φ-step X sits BELOW the limit. By induction on the stage n:
  -- X ⊑ ⊤ (base), and X ⊑ Φ-step X ⊑ Φ-step (Φⁿ⊤) = Φⁿ⁺¹⊤ (step, via co + mono + IH).
  -- So X ⊑ Φⁿ⊤ for all n, i.e. X ⊑ Limit. This is ν's universal property: the
  -- greatest fixed point is ABOVE every post-fixed-point (coalgebra).
  ------------------------------------------------------------------------
  coalg-below-stage : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) →
                      (n : ℕ) → X ⊑ᶠ iterate (step-refinement D) n ⊤-fam
  coalg-below-stage co zero    i x = tt
  coalg-below-stage {X} co (suc m) =
    ⊑ᶠ-trans co (Φ-step-mono D (coalg-below-stage co m))

  -- THE UNIVERSAL PROPERTY: any ν-coalgebra is below the limit.
  coalg-below-limit : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) → X ⊑ᶠ Limit
  coalg-below-limit co i x n = coalg-below-stage co n i x

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ν-half's descending mirror, HONESTLY): the
-- greatest fixed point is characterized by the DESCENDING chain ⋂ₙ Φⁿ⊤ (Limit),
-- dual to 159's ascending ⋃ₙ Φⁿ⊥ (Colim) for μ. The descending chain Φⁿ⁺¹⊤ ⊑ Φⁿ⊤
-- is Refinement.chain at ⊤. The TRUE dual result: every ν-coalgebra X ⊑ Φ-step X
-- sits BELOW the limit (coalg-below-limit) — the greatest-fixed-point UNIVERSAL
-- PROPERTY (ν is above every post-fixed-point), exactly dual to μ being below every
-- pre-fixed-point. The μ-vs-ν either/or dissolves fully into the Kleene duality:
-- μΦ = ⋃ Φⁿ⊥ = Trace (least, below every pre-fp, 159) ; νΦ = ⋂ Φⁿ⊤ = Limit
-- (greatest, above every post-fp/coalgebra, here) — ONE Φ-step, the two colimits
-- from ⊥ and ⊤. HONESTLY SCOPED: Limit ⊑ Φ-step Limit (the limit is itself a
-- coalgebra/post-fixed-point) needs the done/step choice + the step-wedge to
-- STABILIZE across stages (ω-co-continuity); for a general D the per-stage wedge may
-- differ, so this direction + the full Limit ≅ νΦ-step (⟡nu-limit-postfp) stay the
-- honest remainder. The universal property (every coalgebra below) IS delivered.
------------------------------------------------------------------------
