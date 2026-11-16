------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.PrimeDivisor
--
-- Defines: prime-divisor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.PrimeDivisor where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.WellFounded
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.Divides.Refl
open import Substrate.Algebra.Nat.Divides.Trans
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Nat.Prime.Properties.PrimalityDecision



-- every n ≥ 2 has a PRIME divisor (recurse a proper divisor down to a prime).
prime-divisor : (n : ℕ) → Acc _<_ n → 2 ≤ n → Σ ℕ (λ p → IsPrime p × (p ∣ n))
prime-divisor n (acc rec) 2≤n with primality-decision n 2≤n
... | inj₁ n-prime              = n , n-prime , ∣-refl
... | inj₂ (d , 2≤d , d<n , d∣n) =
      let ih = prime-divisor d (rec d d<n) 2≤d
      in proj₁ ih , proj₁ (proj₂ ih) , ∣-trans (proj₂ (proj₂ ih)) d∣n
