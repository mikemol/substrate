------------------------------------------------------------------------
-- Substrate.Category.GrothendieckConstruction.AsTwoFunctor
--
-- Q3 of the Q-arc. Lift N3 ∫-functor from 1-functor to 2-functor
-- (= functor between 2-categories preserving 1-cells AND 2-cells).
-- Closes RECURSION-RESIDUE row from M-arc audit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.GrothendieckConstruction.AsTwoFunctor
  {ℓ0 ℓ1 ℓ2 ℓ0' ℓ1' ℓ2' : Level}
  {ObjS : Set ℓ0} {MorS : ObjS → ObjS → Set ℓ1}
  {TwoCellS : {a b : ObjS} → MorS a b → MorS a b → Set ℓ2}
  {ObjT : Set ℓ0'} {MorT : ObjT → ObjT → Set ℓ1'}
  {TwoCellT : {a b : ObjT} → MorT a b → MorT a b → Set ℓ2'}
  (Source : TwoCategory ObjS MorS TwoCellS)
  (Target : TwoCategory ObjT MorT TwoCellT)
  -- The ∫ 2-functor data (object-map + 1-cell-map + 2-cell-map +
  -- preservation laws); user-supplied.
  where

Grothendieck-AsTwoFunctor-Source : TwoCategory ObjS MorS TwoCellS
Grothendieck-AsTwoFunctor-Source = Source

Grothendieck-AsTwoFunctor-Target : TwoCategory ObjT MorT TwoCellT
Grothendieck-AsTwoFunctor-Target = Target
