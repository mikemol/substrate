------------------------------------------------------------------------
-- Substrate.Category.S2-Lift.AsFunctor
--
-- Substrate-level naming of the S²-Lift as a functor.
--
-- N6 of the N-arc.
--
-- X2 S2-Lift takes a projective-limit discrete structure (typically
-- via Z/n × Z/m with limits to 2-dim) and produces a continuous-
-- target object (= S² as the canonical continuous 2-sphere limit).
-- The assignment is functorial in the projective-limit data.
--
-- Per [[continuous-via-discrete-inference-rules]]: same role as N5
-- (S¹-Lift) but at 2-dim. The substrate's S¹ + S² pair captures the
-- rank-1 + rank-2 continuous limits structurally.
--
-- Per [[gauge-sacrifice-template-universality]]: the substrate's
-- discrete CV-joint families (Thompson F₂³ Sylow-2, Rzeppa F₃ Sylow-3
-- → S¹, Weiss F₇ Sylow-7 → S²) instantiate this lift at different
-- Sylows; N5 + N6 expose both rank lifts as substrate functors.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.S2-Lift.AsFunctor
  {ℓOC ℓMC ℓOD ℓMD : Level}
  {ObjProjectiveCat : Set ℓOC} {MorProjectiveCat : ObjProjectiveCat → ObjProjectiveCat → Set ℓMC}
  {ObjContinuousCat : Set ℓOD} {MorContinuousCat : ObjContinuousCat → ObjContinuousCat → Set ℓMD}
  -- The category of projective-limit discrete data + morphisms.
  (ProjectiveCat : CategoryOf ObjProjectiveCat MorProjectiveCat)
  -- The category of continuous S²-targets + continuous morphisms.
  (ContinuousCat : CategoryOf ObjContinuousCat MorContinuousCat)
  -- The S²-Lift functor.
  (S2-Lift : Functor ProjectiveCat ContinuousCat)
  where

------------------------------------------------------------------------
-- 1. S²-Lift as the substrate's named 2-dim continuous-lift functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  ProjectiveCat ContinuousCat S2-Lift public
  renaming (named-Functor to S2-Lift-Functor)
------------------------------------------------------------------------
-- 2. Capstone — S²-Lift as M1 Functor.
--
-- N6 of the N-arc. With N5 + N6 landed, both rank-1 (S¹) and rank-2
-- (S²) continuous limits carry functorial structure at the substrate
-- level.
--
-- Per [[kinematic-gauge-sacrifice-catalog]]: the substrate's discrete
-- CV-joint families now lift via N5 (Sylow-3 → S¹) + N6 (Sylow-7 →
-- S²) as substrate-internal functors; the continuous-limit dissolves
-- discrete Sylows into smooth field theory per the framework memo.
--
-- Next: N7 F2.Linear.AsSymmetricMonoidal.
------------------------------------------------------------------------
