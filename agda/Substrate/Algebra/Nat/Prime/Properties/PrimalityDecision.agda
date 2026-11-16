------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.PrimalityDecision
--
-- Defines: primality-decision
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.PrimalityDecision where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.DividesToLe
open import Substrate.Algebra.Nat.Prime.Properties.LeToLtSumEq
open import Substrate.Algebra.Nat.Prime.Properties.Search



-- n ≥ 2 is prime, or has a proper divisor.
primality-decision : (n : ℕ) → 2 ≤ n →
  IsPrime n ⊎ (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n)))
primality-decision zero       ()
primality-decision (suc zero) (s≤s ())
primality-decision (suc (suc n'')) 2≤n with search (suc (suc n'')) (suc (suc n'')) (≤-refl _)
... | inj₁ found = inj₂ found
... | inj₂ none  = inj₁ (2≤n , prime-proof)
  where
    prime-proof : (d : ℕ) → d ∣ suc (suc n'') → 2 ≤ d → d ≡ suc (suc n'')
    prime-proof d d∣n 2≤d with ≤→<⊎≡ d (suc (suc n'')) (∣→≤ d (suc n'') d∣n)
    ... | inj₁ d<n = ⊥-elim (none d 2≤d d<n d∣n)
    ... | inj₂ d≡n = d≡n
