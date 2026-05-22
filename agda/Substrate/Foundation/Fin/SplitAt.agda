------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt
--
-- splitAt : ∀ a {b} → Fin (a + b) → Fin a ⊎ Fin b.
-- Partition a Fin (a + b) into "the first a slots" + "the rest b slots".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)

splitAt : ∀ a {b} → Fin (a + b) → Fin a ⊎ Fin b
splitAt zero    {b} i        = inj₂ i
splitAt (suc a) {b} zero     = inj₁ zero
splitAt (suc a) {b} (suc i) with splitAt a {b} i
... | inj₁ k = inj₁ (suc k)
... | inj₂ k = inj₂ k
