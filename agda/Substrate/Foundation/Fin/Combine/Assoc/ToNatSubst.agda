------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.ToNatSubst
--
-- Defines: toℕ-subst
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.ToNatSubst where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 1. toℕ bridges: the value of a Fin under the block maps.
------------------------------------------------------------------------

-- toℕ is invariant under a grade-transport (eq-induction).
toℕ-subst : ∀ {m m'} (eq : m ≡ m') (x : Fin m) → toℕ (subst Fin eq x) ≡ toℕ x
toℕ-subst refl x = refl
