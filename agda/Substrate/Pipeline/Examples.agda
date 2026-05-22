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
-- below.
--
-- Postulates stand in for runtime types (Char, Counts, Window, ...);
-- runtime implementations live in scratch/eliza/eliza/. The
-- postulate use means this surface module cannot be --safe.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples where

open import Substrate.Pipeline.Examples.RotateCrumb       public
open import Substrate.Pipeline.Examples.PredictorUpdate   public
open import Substrate.Pipeline.Examples.PredictorSurprise public
open import Substrate.Pipeline.Examples.ChooseRotation    public
