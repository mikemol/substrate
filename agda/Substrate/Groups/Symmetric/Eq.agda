------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Eq
--
-- Pointwise equality of permutations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Eq (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Foundation.Eq

infix 4 _≈_

_≈_ : Permutation → Permutation → Set
σ ≈ τ = (x : A) → apply σ x ≡ apply τ x
