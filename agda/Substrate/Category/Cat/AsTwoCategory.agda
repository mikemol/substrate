------------------------------------------------------------------------
-- Substrate.Category.Cat.AsTwoCategory
--
-- Q4 of the Q-arc. The substrate's meta-category Cat (of all
-- CategoryOf instances) as a Q1 TwoCategory: 0-cells = categories,
-- 1-cells = functors, 2-cells = nat-trans.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.TwoCategory using (TwoCategory)

module Substrate.Category.Cat.AsTwoCategory
  {ℓ0 ℓ1 ℓ2 : Level}
  (Cat-2 : TwoCategory {ℓ0} {ℓ1} {ℓ2})
  where

Cat-AsTwoCategory : TwoCategory
Cat-AsTwoCategory = Cat-2
