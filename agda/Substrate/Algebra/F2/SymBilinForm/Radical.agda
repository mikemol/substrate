------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.Radical
--
-- Radical M : the Wide-Meet over w of the per-w pair-eq-family.
-- "v pairs to 𝟘 with EVERY w." Expressed in categorical primitives
-- (Wide-Meet of IsEqualised).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.Radical where

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.PairEqFamily using (pair-eq-family)
open import Substrate.Category.Pullback using (Wide-Meet)

Radical : ∀ {n} → BilinForm n → Vector n → Set
Radical {n} M = Wide-Meet (pair-eq-family M)
