------------------------------------------------------------------------
-- Substrate.Category.Cat.AsTwoCategory
--
-- Q4 of the Q-arc. The substrate's meta-category Cat (of all
-- CategoryOf instances) as a Q1 TwoCategory: 0-cells = categories,
-- 1-cells = functors, 2-cells = nat-trans.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.Cat.AsTwoCategory
  {ℓ0 ℓ1 ℓ2 : Level}
  {Obj : Set ℓ0} {Mor : Obj → Obj → Set ℓ1}
  {TwoCell : {a b : Obj} → Mor a b → Mor a b → Set ℓ2}
  (Cat-2 : TwoCategory Obj Mor TwoCell)
  where

Cat-AsTwoCategory : TwoCategory Obj Mor TwoCell
Cat-AsTwoCategory = Cat-2
