------------------------------------------------------------------------
-- Substrate.Algebra.Z.NatDec
--
-- Defines: ℕ-≟
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.NatDec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Algebra.Z.Int
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 4. Decidable equality.
--
-- ℤ has decidable equality (both ℕ-indexed branches are
-- injective constructors). Useful for the ℚ canonical-form
-- comparisons in Q3.
------------------------------------------------------------------------

ℕ-≟ : (m n : ℕ) → Dec (m ≡ n)
ℕ-≟ zero    zero    = yes refl
ℕ-≟ zero    (suc _) = no (λ ())
ℕ-≟ (suc _) zero    = no (λ ())
ℕ-≟ (suc m) (suc n) with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })
