------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Injective
--
-- A permutation's apply is injective.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Injective (A : Set) where

open import Substrate.Foundation.Eq using (_≡_; cong-trans; sym-trans)
open import Substrate.Groups.Symmetric.Permutation A

σ-injective :
  (σ : Permutation) (x y : A) → apply σ x ≡ apply σ y → x ≡ y
σ-injective σ x y eq =
  sym-trans (inv-l σ x)
            (cong-trans (invₐ σ) eq (inv-l σ y))
