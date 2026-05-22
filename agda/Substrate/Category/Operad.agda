------------------------------------------------------------------------
-- Substrate.Category.Operad
--
-- R7 of the R-arc. Operad primitive: collection of operations of
-- specified arities + composition + identity + equivariance under
-- arity-permutations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Operad where

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Nat using (ℕ)

record Operad : Set₁ where
  field
    Ops : ℕ → Set
    id-op : Ops 1
    -- Composition + arity-permutation equivariance + associativity:
    -- user obligations per substrate-pragmatic minimum.
