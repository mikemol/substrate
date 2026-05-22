------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.PairEqFamily
--
-- pair-eq-family M w v : the per-w equalizer of
--   u ↦ bilinear-form-of M u w   vs.   const 𝟘
-- A categorical-primitive expression of "v pairs to 𝟘 with this w".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.PairEqFamily where

open import Substrate.Foundation.Function using (const)
open import Substrate.Algebra.F2 using (𝟘)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf using (bilinear-form-of)
open import Substrate.Category.Equalizer using (IsEqualised)

pair-eq-family : ∀ {n} → BilinForm n → Vector n → Vector n → Set
pair-eq-family {n} M w v =
  IsEqualised (λ u → bilinear-form-of M u w) (const 𝟘) v
