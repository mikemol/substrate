------------------------------------------------------------------------
-- Substrate.Category.Limit
--
-- S2 of the S-arc. Limit primitive (generic version subsuming Cone).
-- For a diagram D : J → C, a limit is a universal cone over D.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Limit where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record Limit
  {ℓOC ℓMC ℓOJ ℓMJ : Level}
  {ObjJ : Set ℓOJ} {MorJ : ObjJ → ObjJ → Set ℓMJ}
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  (J : CategoryOf ObjJ MorJ)
  (C : CategoryOf ObjC MorC)
  (D : Functor J C) : Set (ℓOC ⊔ ℓMC ⊔ ℓOJ ⊔ ℓMJ) where
  field
    limit-obj : ObjC
    -- Universal cone data + universal property: user obligations.
