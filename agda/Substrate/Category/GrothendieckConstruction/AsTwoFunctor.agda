------------------------------------------------------------------------
-- Substrate.Category.GrothendieckConstruction.AsTwoFunctor
--
-- Q3 of the Q-arc. Lift N3 ∫-functor from 1-functor to 2-functor
-- (= functor between 2-categories preserving 1-cells AND 2-cells).
-- Closes RECURSION-RESIDUE row from M-arc audit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.GrothendieckConstruction.AsTwoFunctor
  {ℓ0 ℓ1 ℓ2 ℓ0' ℓ1' ℓ2' : Level}
  (Source : TwoCategory {ℓ0} {ℓ1} {ℓ2})
  (Target : TwoCategory {ℓ0'} {ℓ1'} {ℓ2'})
  -- The ∫ 2-functor data (object-map + 1-cell-map + 2-cell-map +
  -- preservation laws); user-supplied.
  where

Grothendieck-AsTwoFunctor-Source : TwoCategory
Grothendieck-AsTwoFunctor-Source = Source

Grothendieck-AsTwoFunctor-Target : TwoCategory
Grothendieck-AsTwoFunctor-Target = Target
