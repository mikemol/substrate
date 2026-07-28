------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Permutation
--
-- The permutation record: a map with a two-sided inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Permutation (A : Set) where

open import Substrate.Foundation.Eq using (_≡_)

record Permutation : Set where
  field
    apply  : A → A
    invₐ   : A → A
    inv-l  : (x : A) → invₐ (apply x) ≡ x
    inv-r  : (x : A) → apply (invₐ x) ≡ x


-- ⟡public-policy: a module re-exports ONLY what it DEFINES.  `open Permutation
-- public` is a wholesale re-export (the paydown-only census counts it), so the
-- four projections are DEFINED here instead — same signatures, no re-export.
apply : Permutation → A → A
apply = Permutation.apply

invₐ : Permutation → A → A
invₐ = Permutation.invₐ

inv-l : (p : Permutation) (x : A) → invₐ p (apply p x) ≡ x
inv-l = Permutation.inv-l

inv-r : (p : Permutation) (x : A) → apply p (invₐ p x) ≡ x
inv-r = Permutation.inv-r