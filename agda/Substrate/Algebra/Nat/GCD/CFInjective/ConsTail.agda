------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInjective.ConsTail
--
-- Defines: ∷-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInjective; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInjective.ConsTail where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2


∷-tail : {x y : ℕ} {xs ys : List ℕ} → x ∷ xs ≡ y ∷ ys → xs ≡ ys
∷-tail refl = refl
