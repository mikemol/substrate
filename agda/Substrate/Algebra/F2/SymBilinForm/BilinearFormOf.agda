------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.BilinearFormOf
--
-- bilinear-form-of M v w = Σᵢ vᵢ · Σⱼ M(i,j) · wⱼ.
-- Generic double-sum evaluation; works on any BilinForm.
-- Per-dim definitions (SymBilinForm-3.bilinear-form-of,
-- SymBilinForm-4.bilinear-form-of-4) are pattern-expanded
-- versions at fixed n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.BilinearFormOf where

open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Algebra.F2 using (F₂; _·_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)

bilinear-form-of : ∀ {n} → BilinForm n → Vector n → Vector n → F₂
bilinear-form-of {n} M v w =
  sum-F₂ {n} (λ i → lookup v i · sum-F₂ {n} (λ j → M i j · lookup w j))
