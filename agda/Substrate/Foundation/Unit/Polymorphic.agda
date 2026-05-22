------------------------------------------------------------------------
-- Substrate.Foundation.Unit.Polymorphic
--
-- Universe-polymorphic unit type. Distinguished from
-- Substrate.Foundation.Unit (mono-universe, ⊤ : Set) for use in
-- higher-universe contexts (categories, polynomial functors, etc.)
-- where ⊤ : Set ℓ is needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Unit.Polymorphic where

open import Substrate.Foundation.Level using (Level)

private
  variable
    ℓ : Level

record ⊤ {ℓ} : Set ℓ where
  constructor tt
