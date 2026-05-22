------------------------------------------------------------------------
-- Substrate.Category.Adjunction.AsTwoCellStructure
--
-- Q5 of the Q-arc. Lift the substrate's Adjunction primitive (#4) to
-- carry explicit 2-cell structure (= unit + counit as 2-cells in a
-- Q1 TwoCategory ambient).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.Adjunction.AsTwoCellStructure
  {ℓ0 ℓ1 ℓ2 : Level}
  (Ambient2Cat : TwoCategory {ℓ0} {ℓ1} {ℓ2})
  where

Adjunction-AsTwoCellStructure-Ambient : TwoCategory
Adjunction-AsTwoCellStructure-Ambient = Ambient2Cat
