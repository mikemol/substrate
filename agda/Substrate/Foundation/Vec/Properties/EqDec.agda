------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.EqDec
--
-- Defines: ≡-dec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.EqDec where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Vec.Properties.Private2



------------------------------------------------------------------------
-- ≡-dec: lift decidable equality on elements to decidable equality on
-- length-indexed vectors.
------------------------------------------------------------------------

≡-dec :
  {A : Set} {n : ℕ} →
  ((x y : A) → Dec (x ≡ y)) →
  (xs ys : Vec A n) → Dec (xs ≡ ys)
≡-dec _≟_ []       []       = yes refl
≡-dec _≟_ (x ∷ xs) (y ∷ ys) with x ≟ y | ≡-dec _≟_ xs ys
... | yes refl | yes refl = yes refl
... | no  ¬x≡y | _        = no λ p → ¬x≡y (∷-injective-head p)
... | _        | no  ¬eq  = no λ p → ¬eq (∷-injective-tail p)
