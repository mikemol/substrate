------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.EqRefl
--
-- _≈_ is reflexive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.EqRefl (A : Set) where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)

≈-refl : (σ : Permutation) → σ ≈ σ
≈-refl _ _ = refl
