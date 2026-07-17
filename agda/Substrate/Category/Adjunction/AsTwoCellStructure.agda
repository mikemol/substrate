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
  {Obj : Set ℓ0} {Mor : Obj → Obj → Set ℓ1}
  {TwoCell : {a b : Obj} → Mor a b → Mor a b → Set ℓ2}
  (Ambient2Cat : TwoCategory Obj Mor TwoCell)
  where

Adjunction-AsTwoCellStructure-Ambient : TwoCategory Obj Mor TwoCell
Adjunction-AsTwoCellStructure-Ambient = Ambient2Cat
