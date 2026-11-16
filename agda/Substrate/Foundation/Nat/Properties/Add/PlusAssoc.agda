------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add.PlusAssoc
--
-- Defines: +ℕ-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add.PlusAssoc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



+ℕ-assoc : (m n k : ℕ) → (m ℕ+ n) ℕ+ k ≡ m ℕ+ (n ℕ+ k)
+ℕ-assoc zero    _ _ = refl
+ℕ-assoc (suc m) n k = cong suc (+ℕ-assoc m n k)
