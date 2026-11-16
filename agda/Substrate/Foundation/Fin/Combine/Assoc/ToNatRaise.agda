------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise
--
-- Defines: toℕ-raise
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



-- raise shifts the value by the offset.
toℕ-raise : ∀ n {k} (x : Fin k) → toℕ (raise n x) ≡ n ℕ+ toℕ x
toℕ-raise zero    x = refl
toℕ-raise (suc n) x = cong suc (toℕ-raise n x)
