------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.Crumb
--
-- Defines: Crumb
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.Crumb where

open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Eq



-- Atomic types.
data Crumb : Set where      -- ⟦shape:16b523ba c₀ c₁ c₂ c₃⟧
  c₀ c₁ c₂ c₃ : Crumb
