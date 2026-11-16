------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesIdentityL
--
-- Defines: *-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesIdentityL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Eq



*-identityˡ : (n : ℕ) → suc zero * n ≡ n
*-identityˡ n = +ℕ-identityʳ n
