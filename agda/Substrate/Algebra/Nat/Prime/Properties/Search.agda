------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.Search
--
-- Defines: search
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.Search where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.StepCandidate
open import Substrate.Category.BWTEmergence



-- search all candidates below `bound` for a proper divisor of n.
search : (n bound : ℕ) → bound ≤ n →
  (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n))) ⊎
  ((d : ℕ) → 2 ≤ d → d < bound → ¬ (d ∣ n))
search n zero    _     = inj₂ (λ d _ ())
search n (suc b) sb≤n with search n b (≤-trans (≤-suc-r (≤-refl b)) sb≤n)
... | inj₁ found = inj₁ found
... | inj₂ none  = step-candidate n b sb≤n none
