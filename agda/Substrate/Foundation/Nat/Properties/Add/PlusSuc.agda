------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add.PlusSuc
--
-- Defines: +ℕ-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add.PlusSuc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



+ℕ-suc : (m n : ℕ) → m ℕ+ suc n ≡ suc (m ℕ+ n)
+ℕ-suc zero    _ = refl
+ℕ-suc (suc m) n = cong suc (+ℕ-suc m n)
