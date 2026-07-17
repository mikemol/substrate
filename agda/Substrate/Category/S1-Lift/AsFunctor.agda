------------------------------------------------------------------------
-- Substrate.Category.S1-Lift.AsFunctor
--
-- Substrate-level naming of the S¹-Lift as a functor.
--
-- N5 of the N-arc. Continuous-side functorial closure.
--
-- X1 S1-Lift takes a cyclic group (or cyclic-like discrete structure)
-- and produces a continuous-target object (= S¹ as the canonical
-- continuous limit of Z/n as n → ∞). The assignment "cyclic ↦
-- continuous-S¹-target" is functorial.
--
-- Per [[continuous-via-discrete-inference-rules]]: the substrate
-- formalises the discrete inference rules CONSTRUCTING continuous
-- embeddings; the functor itself is the substrate's structural
-- handle on "continuous limits of discrete structures."
--
-- Per [[grothendieck-coherence-rule]]: N5 closes the S1-Lift orphan
-- documented in the M-arc's OrphanAudit (MEDIUM priority).
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.S1-Lift.AsFunctor
  {ℓOC ℓMC ℓOD ℓMD : Level}
  {ObjCyclicCat : Set ℓOC} {MorCyclicCat : ObjCyclicCat → ObjCyclicCat → Set ℓMC}
  {ObjContinuousCat : Set ℓOD} {MorContinuousCat : ObjContinuousCat → ObjContinuousCat → Set ℓMD}
  -- The category of cyclic / cyclic-limit discrete data + their
  -- morphisms.
  (CyclicCat : CategoryOf ObjCyclicCat MorCyclicCat)
  -- The category of continuous S¹-targets + continuous morphisms.
  (ContinuousCat : CategoryOf ObjContinuousCat MorContinuousCat)
  -- The S¹-Lift functor.
  (S1-Lift : Functor CyclicCat ContinuousCat)
  where

------------------------------------------------------------------------
-- 1. S¹-Lift as the substrate's named continuous-lift functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  CyclicCat ContinuousCat S1-Lift public
  renaming (named-Functor to S1-Lift-Functor)
------------------------------------------------------------------------
-- 2. Capstone — S¹-Lift as M1 Functor.
--
-- N5 of the N-arc. With N5 landed, the substrate's S¹-Lift X-arc
-- primitive carries functorial structure; the discrete→continuous
-- lift becomes a substrate functor rather than a per-instance
-- construction.
--
-- Per [[continuous-limit-lift-framework]]: this is the formal
-- functor underlying the substrate's discrete↔continuous bridge at
-- S¹. Concrete instances (Cyclic = Z/n; ContinuousCat = topological
-- S¹) compose via N5 to lift discrete actions to continuous ones.
--
-- Next: N6 S2-Lift.AsFunctor (S² analog).
------------------------------------------------------------------------
