------------------------------------------------------------------------
-- Substrate.Category.Topos
--
-- S8 of the S-arc. Elementary topos: cartesian-closed category with
-- finite limits + subobject classifier Ω.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Topos where

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.SubobjectClassifier
  using (SubobjectClassifier)

record Topos
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (C : CategoryOf Obj Mor) : Set ℓO where
  field
    Ω-data : SubobjectClassifier C
    -- Finite limits + cartesian-closed structure: user obligations.
