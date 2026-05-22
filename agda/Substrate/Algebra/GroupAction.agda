------------------------------------------------------------------------
-- Substrate.Algebra.GroupAction
--
-- A left action of a Group on a set. Substrate-native (built over
-- Substrate.Algebra.Group, not stdlib's Algebra.Bundles.Group).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GroupAction where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)
open import Substrate.Algebra.Group using (Group; monoid)

------------------------------------------------------------------------
-- A left action of G on a set B.
------------------------------------------------------------------------

record Action {A : Set} (G : Group A) (B : Set) : Set where
  field
    act     : A → B → B
    act-id  : (b : B) → act (ε (monoid G)) b ≡ b
    act-∙   :
      (g h : A) (b : B) →
      let _·_ = Magma._·_ (magma (semigroup (monoid G)))
      in act (g · h) b ≡ act g (act h b)

open Action public
