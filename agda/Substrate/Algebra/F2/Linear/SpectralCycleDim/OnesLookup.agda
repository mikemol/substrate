------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OnesLookup
--
-- Defines: ones-lookup
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OnesLookup where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Foundation.Eq



-- ones is all-𝟙.
ones-lookup : ∀ {n} (j : Fin n) → lookup (ones {n}) j ≡ 𝟙
ones-lookup {suc n} zero    = refl
ones-lookup {suc n} (suc j) = ones-lookup j
