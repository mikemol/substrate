------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.InvLeft
--
-- _⁻¹ is a left inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.InvLeft (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)
open import Substrate.Groups.Symmetric.Identity A using (ε)
open import Substrate.Groups.Symmetric.Permutation.Inverse A using (_⁻¹)

inv-left : (σ : Permutation) → ((σ ⁻¹) · σ) ≈ ε
inv-left σ x = inv-l σ x
