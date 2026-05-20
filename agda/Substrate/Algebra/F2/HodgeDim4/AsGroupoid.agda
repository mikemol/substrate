------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.AsGroupoid
--
-- P7 of the P-arc. HodgeDim4 (= the 168-Bijection orbit on Reserved↔
-- SelfDual) packaged as a groupoid (= category where every morphism
-- is invertible). Closes the "168 bijections form a groupoid" view.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.HodgeDim4.AsGroupoid
  {ℓO ℓM : Level}
  (HodgeGroupoid : CategoryOf {ℓO} {ℓM})
  where

HodgeDim4-AsGroupoid : CategoryOf
HodgeDim4-AsGroupoid = HodgeGroupoid
