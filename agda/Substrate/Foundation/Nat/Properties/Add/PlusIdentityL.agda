------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
--
-- Defines: +ℕ-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add.PlusIdentityL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq



+ℕ-identityˡ : (n : ℕ) → zero ℕ+ n ≡ n
+ℕ-identityˡ _ = refl
