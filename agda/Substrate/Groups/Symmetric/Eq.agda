------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Eq
--
-- Pointwise equality of permutations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Eq (A : Set) where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Symmetric.Permutation A

infix 4 _≈_

_≈_ : Permutation → Permutation → Set
σ ≈ τ = (x : A) → apply σ x ≡ apply τ x
