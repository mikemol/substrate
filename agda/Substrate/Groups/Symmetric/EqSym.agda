------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.EqSym
--
-- _≈_ is symmetric.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.EqSym (A : Set) where

open import Substrate.Foundation.Eq using (sym)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)

≈-sym : {σ τ : Permutation} → σ ≈ τ → τ ≈ σ
≈-sym σ≈τ x = sym (σ≈τ x)
