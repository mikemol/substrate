------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Assoc
--
-- Composition is associative.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Assoc (A : Set) where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)

·-assoc : (σ τ ρ : Permutation) → ((σ · τ) · ρ) ≈ (σ · (τ · ρ))
·-assoc _ _ _ _ = refl
