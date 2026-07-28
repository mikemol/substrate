------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.EqTrans
--
-- _≈_ is transitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.EqTrans (A : Set) where

open import Substrate.Foundation.Eq using (trans)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)

≈-trans : {σ τ ρ : Permutation} → σ ≈ τ → τ ≈ ρ → σ ≈ ρ
≈-trans σ≈τ τ≈ρ x = trans (σ≈τ x) (τ≈ρ x)
