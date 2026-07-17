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
  {ObjC : Set ℓ0} {MorC : ObjC → ObjC → Set ℓ1}
  {TwoCellC : {a b : ObjC} → MorC a b → MorC a b → Set ℓ2}
  {ObjD : Set ℓ0'} {MorD : ObjD → ObjD → Set ℓ1'}
  {TwoCellD : {a b : ObjD} → MorD a b → MorD a b → Set ℓ2'}
  (C : TwoCategory ObjC MorC TwoCellC)
  (D : TwoCategory ObjD MorD TwoCellD) : Set where
  -- User-supplied lax-functor data; substrate names the type.
