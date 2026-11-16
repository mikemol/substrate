------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntIdentityL
--
-- Defines: *ℤ-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntIdentityL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Sub
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- 2. Identity and zero.
------------------------------------------------------------------------

*ℤ-identityˡ : (x : ℤ) → (+ 1) *ℤ x ≡ x
*ℤ-identityˡ (+ n)    = cong +_ (+ℕ-identityʳ n)
*ℤ-identityˡ (-suc n) = cong (λ z → -ℤ (+ z)) (+ℕ-identityʳ (suc n))
