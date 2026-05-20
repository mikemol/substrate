------------------------------------------------------------------------
-- Substrate.Category.KanExtension
--
-- S4 of the S-arc. Left + right Kan extensions: universal way to
-- extend a functor F : A → C along K : A → B to a functor B → C.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.KanExtension where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record LeftKanExtension
  {ℓOA ℓMA ℓOB ℓMB ℓOC ℓMC : Level}
  (A : CategoryOf {ℓOA} {ℓMA})
  (B : CategoryOf {ℓOB} {ℓMB})
  (C : CategoryOf {ℓOC} {ℓMC})
  (K : Functor A B)
  (F : Functor A C) : Set (lsuc (ℓOB ⊔ ℓMB ⊔ ℓOC ⊔ ℓMC)) where
  field
    Lan : Functor B C

record RightKanExtension
  {ℓOA ℓMA ℓOB ℓMB ℓOC ℓMC : Level}
  (A : CategoryOf {ℓOA} {ℓMA})
  (B : CategoryOf {ℓOB} {ℓMB})
  (C : CategoryOf {ℓOC} {ℓMC})
  (K : Functor A B)
  (F : Functor A C) : Set (lsuc (ℓOB ⊔ ℓMB ⊔ ℓOC ⊔ ℓMC)) where
  field
    Ran : Functor B C
