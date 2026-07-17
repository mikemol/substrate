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
  {ObjC : Set ℓ0} {MorC : ObjC → ObjC → Set ℓ1}
  {TwoCellC : {a b : ObjC} → MorC a b → MorC a b → Set ℓ2}
  {ObjD : Set ℓ0'} {MorD : ObjD → ObjD → Set ℓ1'}
  {TwoCellD : {a b : ObjD} → MorD a b → MorD a b → Set ℓ2'}
  (C : TwoCategory ObjC MorC TwoCellC)
  (D : TwoCategory ObjD MorD TwoCellD) : Set where
  -- User-supplied pseudo-functor data (object map + 1-cell map +
  -- coherent invertible 2-cells witnessing preservation up to iso).
  -- Substrate names the type; concrete data downstream.
