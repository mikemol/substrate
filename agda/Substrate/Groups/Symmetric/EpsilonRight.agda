------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.EpsilonRight
--
-- ε is a right identity for composition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.EpsilonRight (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)
open import Substrate.Groups.Symmetric.Identity A using (ε)
open import Substrate.Foundation.Eq

ε-right : (σ : Permutation) → (σ · ε) ≈ σ
ε-right _ _ = refl
