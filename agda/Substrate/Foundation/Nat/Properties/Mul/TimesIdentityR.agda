------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesIdentityR
--
-- Defines: *-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesIdentityR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



*-identityʳ : (n : ℕ) → n * suc zero ≡ n
*-identityʳ zero    = refl
*-identityʳ (suc n) = cong suc (*-identityʳ n)
