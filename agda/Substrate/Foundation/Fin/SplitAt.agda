------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt
--
-- splitAt : ∀ a {b} → Fin (a ℕ+ b) → Fin a ⊎ Fin b.
-- Partition a Fin (a ℕ+ b) into "the first a slots" ℕ+ "the rest b slots".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Sum.Sum

splitAt : ∀ a {b} → Fin (a ℕ+ b) → Fin a ⊎ Fin b
splitAt zero    {b} i        = inj₂ i
splitAt (suc a) {b} zero     = inj₁ zero
splitAt (suc a) {b} (suc i) with splitAt a {b} i
... | inj₁ k = inj₁ (suc k)
... | inj₂ k = inj₂ k
