------------------------------------------------------------------------
-- Substrate.Category.PseudoFunctor
--
-- Q6 of the Q-arc. PseudoFunctor primitive: like M1 Functor but
-- preserves identity + composition up to specified isomorphism
-- (not strict equality).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.PseudoFunctor where

record PseudoFunctor
  {ℓ0 ℓ1 ℓ2 ℓ0' ℓ1' ℓ2' : Level}
  (C : TwoCategory {ℓ0} {ℓ1} {ℓ2})
  (D : TwoCategory {ℓ0'} {ℓ1'} {ℓ2'}) : Set where
  -- User-supplied pseudo-functor data (object map + 1-cell map +
  -- coherent invertible 2-cells witnessing preservation up to iso).
  -- Substrate names the type; concrete data downstream.
