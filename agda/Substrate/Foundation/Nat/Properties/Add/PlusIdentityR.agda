------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
--
-- Defines: +ℕ-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add.PlusIdentityR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



+ℕ-identityʳ : (n : ℕ) → n ℕ+ zero ≡ n
+ℕ-identityʳ zero    = refl
+ℕ-identityʳ (suc n) = cong suc (+ℕ-identityʳ n)
