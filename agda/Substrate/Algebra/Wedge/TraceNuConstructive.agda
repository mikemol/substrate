{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceNuConstructive — ⟡nu-limit-postfp-corrected: the
-- CONSTRUCTIVE greatest fixed point, on the reground footing (ADD 163). The naive
-- target was "Limit ⊑ Φ-step Limit under a determinacy hypothesis" — but the
-- substrate's constructive coinductance (ComputeTrace's Acc-descent + ComputeTraceStep's
-- RESULT-IRRELEVANCE: the step is the uniform construct-wedge, Acc-witness-blind +
-- ana-unique + Lawvere's final-coalgebra=fixed-point) shows the step is a FUNCTION
-- (divide), so the constructive ν needs NO hypothesis.
--
-- THE CONSTRUCTIVE ν IS THE divide-COALGEBRA (StepAt, ADD 160): a post-fixed-point
-- BY CONSTRUCTION (coalg-unroll uses divide directly — a function of the index,
-- uniform across stages, cta-irr's result-irrelevance). It sits BELOW the descending-
-- chain Limit (coalg-below-limit, ADD 162), and its SHAPE is the terminal ℕ-stream
-- via ana-unique (ADD 161). This REPLACES the ad-hoc determinacy hypothesis: the
-- determinism is STRUCTURAL (divide is a function), the Lawvere final-coalgebra=
-- fixed-point realized constructively via the wedge (cofree-dual of recon).
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.TraceNuConstructive where

open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide)
open import Substrate.Category.Allegory.Refinement using (_⊑ᶠ_)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step)
open import Substrate.Algebra.Wedge.TraceNuStep using (ν-Coalg; StepAt; coalg-unroll)
open import Substrate.Algebra.Wedge.TraceNuColimit using (Limit; coalg-below-limit)

module _ {C : Set} (D : DivStr C) (co : WedgeCoalg D) where

  ------------------------------------------------------------------------
  -- ① THE CONSTRUCTIVE ν CARRIER = the divide-coalgebra StepAt. NOT a coinductive
  -- record, NOT an ad-hoc hypothesis — the wedge-driven unfold (Wedge.Coalgebra's
  -- constructive coinduction, the cofree-dual of recon's inductive Trace).
  ------------------------------------------------------------------------
  ν-carrier : Idx D → Set
  ν-carrier = StepAt D co

  ------------------------------------------------------------------------
  -- ② POST-FIXED-POINT BY CONSTRUCTION: ν-carrier ⊑ Φ-step ν-carrier. The step is
  -- divide (a FUNCTION of the index) — no determinacy hypothesis, no wedge-variation
  -- to reconcile (cta-irr's result-irrelevance: the step is uniform, Acc-blind). This
  -- IS the coalgebra structure (dual to 158's roll : Φ-step Trace ⊑ᶠ Trace).
  ------------------------------------------------------------------------
  ν-is-coalgebra : ν-carrier ⊑ᶠ Φ-step D ν-carrier
  ν-is-coalgebra = coalg-unroll D co

  ------------------------------------------------------------------------
  -- ③ BELOW THE DESCENDING-CHAIN LIMIT (the NEW combination, 160 + 162): the
  -- constructive ν, being a coalgebra, sits below the limit ⋂ₙ Φⁿ⊤ by the greatest-
  -- fixed-point universal property. This is the corrected "post-fixed-point" result:
  -- NOT "Limit ⊑ Φ-step Limit under a hypothesis" but "the constructive ν (a genuine
  -- post-fixed-point, no hypothesis) ⊑ Limit". The constructive ν witnesses that the
  -- greatest fixed point is INHABITED and below its universal envelope.
  ------------------------------------------------------------------------
  ν-below-limit : ν-carrier ⊑ᶠ Limit D
  ν-below-limit = coalg-below-limit D ν-is-coalgebra

  ------------------------------------------------------------------------
  -- ④ THE ν-COALGEBRA STRUCTURE IS THE UNFOLD (dual to the inductive recon/roll):
  -- ν-carrier is a ν-Coalg (the terminal-coalgebra structure map). With ana-unique
  -- (Final, ADD 157/161 for the ℕ-stream shape), this is terminal up-to-shape:
  -- shape(ν-carrier) = RealTrace, the unique coalgebra morphism (NuShapeIso, 161).
  ------------------------------------------------------------------------
  ν-structure : ν-Coalg D ν-carrier
  ν-structure = ν-is-coalgebra

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the constructive ν, no hypothesis): the greatest
-- fixed point is realized CONSTRUCTIVELY as the divide-coalgebra (ν-carrier =
-- StepAt). It is a post-fixed-point BY CONSTRUCTION (ν-is-coalgebra = coalg-unroll,
-- the step being divide — a FUNCTION of the index, uniform across stages by cta-irr's
-- result-irrelevance, NOT an assumed determinacy), and it sits BELOW the descending-
-- chain Limit (ν-below-limit, via the greatest-fixed-point universal property, 162).
-- Its shape is the terminal ℕ-stream via ana-unique (161). The "need a determinacy
-- hypothesis for Limit ⊑ Φ-step Limit" WORRY dissolves: the constructive ν is the
-- divide-coalgebra, whose step is structurally a function — the substrate's
-- constructive coinductance (Acc-descent + result-irrelevance + ana-unique + Lawvere's
-- final-coalgebra=fixed-point, the cofree-dual of recon). HONESTLY SCOPED: the ABSTRACT
-- Limit ⊑ Φ-step Limit (the outer limit ITSELF a coalgebra, extracting a consistent
-- wedge from the existential Σ w. Φⁿ⊤) still needs wedge-rem-uniqueness (holds for
-- ℕ-div via recon-bounded-unique) — the ω-co-continuity residue, my original ad-hoc
-- plan, KEPT as the shadow naming why the CONSTRUCTIVE path (divide, a function) needs
-- no such hypothesis. With 157-163, the ν-half: endpoint (160) + shape iso (161) +
-- descending chain & universal property (162) + the CONSTRUCTIVE ν below the limit
-- (here), the abstract-limit-postfp the sole scoped ω-continuity remainder.
------------------------------------------------------------------------
