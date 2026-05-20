------------------------------------------------------------------------
-- Substrate.Category.TwoNaturalTransformation
--
-- Q8 of the Q-arc. 2-natural transformation between Q6 PseudoFunctors
-- / Q7 LaxFunctors. Components are 1-cells; naturality is a 2-cell.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

module Substrate.Category.TwoNaturalTransformation where

record TwoNaturalTransformation : Set where
  -- User-supplied data; substrate names the carrier type. Concrete
  -- usage requires fixing source/target 2-functors + the component
  -- 1-cells + naturality 2-cells.
