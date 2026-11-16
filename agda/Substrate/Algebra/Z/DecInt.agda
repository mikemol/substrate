------------------------------------------------------------------------
-- Substrate.Algebra.Z.DecInt
--
-- Defines: _≟ℤ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.DecInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.NatDec
open import Substrate.Foundation.Eq



_≟ℤ_ : (a b : ℤ) → Dec (a ≡ b)
(+ m)    ≟ℤ (+ n)    with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })
(+ _)    ≟ℤ (-suc _) = no (λ ())
(-suc _) ≟ℤ (+ _)    = no (λ ())
(-suc m) ≟ℤ (-suc n) with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })
