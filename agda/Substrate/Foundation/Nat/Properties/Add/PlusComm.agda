------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add.PlusComm
--
-- Defines: +ℕ-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add.PlusComm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



+ℕ-comm : (m n : ℕ) → m ℕ+ n ≡ n ℕ+ m
+ℕ-comm zero    n = sym (+ℕ-identityʳ n)
+ℕ-comm (suc m) n = trans (cong suc (+ℕ-comm m n)) (sym (+ℕ-suc n m))
