------------------------------------------------------------------------
-- Substrate.Category.KleisliCategory
--
-- R5 of the R-arc. Kleisli category of a Monad M : same objects as
-- base C, morphisms a → b are C-morphisms a → T(b).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.KleisliCategory where

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)

module _
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (M : Monad C)
  -- User supplies the Kleisli CategoryOf instance directly per the
  -- substrate-pragmatic parametric pattern.
  (Kleisli : CategoryOf {ℓO} {ℓM})
  where

  KleisliCategory : CategoryOf
  KleisliCategory = Kleisli
