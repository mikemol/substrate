------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInjective.ConsHead
--
-- Defines: ∷-head
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInjective; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInjective.ConsHead where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2



∷-head : {x y : ℕ} {xs ys : List ℕ} → x ∷ xs ≡ y ∷ ys → x ≡ y
∷-head refl = refl
