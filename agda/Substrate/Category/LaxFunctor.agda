------------------------------------------------------------------------
-- Substrate.Category.LaxFunctor
--
-- Q7 of the Q-arc. LaxFunctor primitive: preserves identity +
-- composition up to (not-necessarily-invertible) 2-cells, with
-- coherence.
--
-- Dual: OpLaxFunctor — same with 2-cells in the opposite direction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.LaxFunctor where

record LaxFunctor
  {ℓ0 ℓ1 ℓ2 ℓ0' ℓ1' ℓ2' : Level}
  (C : TwoCategory {ℓ0} {ℓ1} {ℓ2})
  (D : TwoCategory {ℓ0'} {ℓ1'} {ℓ2'}) : Set where
  -- User-supplied lax-functor data; substrate names the type.
