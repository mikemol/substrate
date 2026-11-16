------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus
--
-- Defines: toℕ-inject+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



-- inject+ (the low injection) preserves the value.
toℕ-inject+ : ∀ {n} k (x : Fin n) → toℕ (inject+ k x) ≡ toℕ x
toℕ-inject+ k zero    = refl
toℕ-inject+ k (suc x) = cong suc (toℕ-inject+ k x)
