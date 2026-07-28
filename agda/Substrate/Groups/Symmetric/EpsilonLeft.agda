------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.EpsilonLeft
--
-- ε is a left identity for composition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.EpsilonLeft (A : Set) where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)
open import Substrate.Groups.Symmetric.Identity A using (ε)

ε-left : (σ : Permutation) → (ε · σ) ≈ σ
ε-left _ _ = refl
