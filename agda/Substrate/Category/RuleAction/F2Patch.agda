------------------------------------------------------------------------
-- Substrate.Category.RuleAction.F2Patch
--
-- F₂Patch: sparse F₂-correction list of (index, replacement) pairs.
-- Subsumes fuzzy-match via Hodge-bivector flip patterns.
-- Identity patch = empty list. Sparsity = list length.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.F2Patch where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; [])
open import Substrate.Foundation.Product using (_×_)

F₂Patch : Set
F₂Patch = List (ℕ × ℕ)

identity-patch : F₂Patch
identity-patch = []
