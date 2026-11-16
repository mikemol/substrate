------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Total
--
-- Defines: total-𝟎
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Total where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- The A-side of Φ_p(σ_p) = A: total of a basis vector is 𝟙, so A(eₖ) = ones.
------------------------------------------------------------------------

total-𝟎 : ∀ {n} → total (𝟎ⱽ {n}) ≡ 𝟘
total-𝟎 {zero}  = refl
total-𝟎 {suc n} = total-𝟎 {n}
