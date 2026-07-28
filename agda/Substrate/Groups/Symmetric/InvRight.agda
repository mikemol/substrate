------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.InvRight
--
-- _⁻¹ is a right inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.InvRight (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)
open import Substrate.Groups.Symmetric.Identity A using (ε)
open import Substrate.Groups.Symmetric.Permutation.Inverse A using (_⁻¹)

inv-right : (σ : Permutation) → (σ · (σ ⁻¹)) ≈ ε
inv-right σ x = inv-r σ x
