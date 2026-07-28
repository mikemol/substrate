------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Permutation.Inverse
--
-- The inverse permutation (swap apply and invₐ).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Permutation.Inverse (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A

_⁻¹ : Permutation → Permutation
σ ⁻¹ = record
  { apply = invₐ σ
  ; invₐ  = apply σ
  ; inv-l = inv-r σ
  ; inv-r = inv-l σ
  }
