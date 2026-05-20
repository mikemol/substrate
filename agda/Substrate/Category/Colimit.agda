------------------------------------------------------------------------
-- Substrate.Category.Colimit
--
-- S3 of the S-arc. Colimit primitive (dual of S2): for a diagram
-- D : J → C, a colimit is a universal cocone.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Colimit where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record Colimit
  {ℓOC ℓMC ℓOJ ℓMJ : Level}
  (J : CategoryOf {ℓOJ} {ℓMJ})
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : Functor J C) : Set (lsuc (ℓOC ⊔ ℓMC ⊔ ℓOJ ⊔ ℓMJ)) where
  field
    colimit-obj : CategoryOf.Obj C
