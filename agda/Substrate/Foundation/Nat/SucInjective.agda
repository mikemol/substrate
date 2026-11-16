------------------------------------------------------------------------
-- Substrate.Foundation.Nat.SucInjective
--
-- Defines: suc-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.SucInjective where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- Decidable equality ℕ+ comparison.
------------------------------------------------------------------------

suc-injective : {m n : ℕ} → suc m ≡ suc n → m ≡ n
suc-injective refl = refl
