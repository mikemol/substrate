------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Permutation.Compose
--
-- Composition of permutations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Permutation.Compose (A : Set) where

open import Substrate.Foundation.Eq using (cong-trans)
open import Substrate.Groups.Symmetric.Permutation A

_·_ : Permutation → Permutation → Permutation
σ · τ = record
  { apply = λ x → apply σ (apply τ x)
  ; invₐ  = λ x → invₐ τ (invₐ σ x)
  ; inv-l = λ x →
      cong-trans (invₐ τ) (inv-l σ (apply τ x)) (inv-l τ x)
  ; inv-r = λ x →
      cong-trans (apply σ) (inv-r τ (invₐ σ x)) (inv-r σ x)
  }
