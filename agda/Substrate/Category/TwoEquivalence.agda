------------------------------------------------------------------------
-- Substrate.Category.TwoEquivalence
--
-- Q9 of the Q-arc. Equivalence in a 2-category: pair of 1-cells +
-- invertible-up-to-2-cell composites.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

module Substrate.Category.TwoEquivalence where

record TwoEquivalence : Set where
  -- User-supplied data: forward + backward 1-cells + invertible-2-cell
  -- witnesses + triangle coherence. Substrate names the carrier.
