------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.Private2
--
-- Defines: ∷-injective-head, ∷-injective-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.Private2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Vec.Properties.Private



------------------------------------------------------------------------
-- ∷ is injective in both arguments.
------------------------------------------------------------------------

∷-injective-head : {A : Set} {n : ℕ} {x y : A} {xs ys : Vec A n} →
                   (x ∷ xs) ≡ (y ∷ ys) → x ≡ y
∷-injective-head refl = refl

∷-injective-tail : {A : Set} {n : ℕ} {x y : A} {xs ys : Vec A n} →
                   (x ∷ xs) ≡ (y ∷ ys) → xs ≡ ys
∷-injective-tail refl = refl
