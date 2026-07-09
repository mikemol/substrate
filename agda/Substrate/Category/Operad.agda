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

-- ⟡set1-paydown: parameterize Ops (the ℕ-indexed operation family). `Ops : ℕ → Set` was the
-- indexed-family FIELD forcing Operad : Set₁; take it as a module parameter and the record lives
-- in Set. Consumers write `Operad Ops`.
module _ (Ops : ℕ → Set) where
  record Operad : Set where
    field
      id-op : Ops 1
      -- Composition + arity-permutation equivariance + associativity:
      -- user obligations per substrate-pragmatic minimum.
