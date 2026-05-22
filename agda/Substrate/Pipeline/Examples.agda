------------------------------------------------------------------------
-- Substrate.Pipeline.Examples
--
-- Concrete bricks from the eliza codec, modeled as instances of the
-- Brick framework. File-per-example:
--
--   Examples.RotateCrumb        — pure V₄ transform (D⇒S trivial)
--   Examples.PredictorUpdate    — state update (D⇒S non-trivial)
--   Examples.PredictorSurprise  — state query (S⇒D)
--   Examples.ChooseRotation     — compute selection (D⇒C)
--
-- Each example covers one of the four main witnessing types of the
-- Brick schema. Remaining types (S⇒C, C⇒S, C⇒D) sketched in comments
-- in the per-example files.
--
-- Module-parametric on the runtime types (Char, Counts, Window,
-- RotIdx, Predictor, Cache) + the runtime operation hooks. Concrete
-- runtime implementations live in scratch/eliza/eliza/. This
-- replaces the prior `postulate`-using surface, which forced
-- --without-K but excluded --safe; the parametric form is fully
-- --safe-compatible.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_)

module Substrate.Pipeline.Examples
  (Char      : Set)
  (Counts    : Set)
  (Window    : Set)
  (RotIdx    : Set)
  (Predictor : Set)
  (Cache     : Set)
  (update-counts        : Counts → Char → Counts)
  (surprise-bits        : Counts → Char → ℕ)
  (choose-rotation-impl :
     Window → (Predictor × Cache) → (RotIdx × (Predictor × Cache)))
  where

open import Substrate.Pipeline.Examples.RotateCrumb       public
open import Substrate.Pipeline.Examples.PredictorUpdate Char Counts update-counts
  public
open import Substrate.Pipeline.Examples.PredictorSurprise Char Counts surprise-bits
  public
open import Substrate.Pipeline.Examples.ChooseRotation Window RotIdx Predictor Cache
                                                       choose-rotation-impl
  public
