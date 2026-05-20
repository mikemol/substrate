------------------------------------------------------------------------
-- Substrate.Category.Limit
--
-- S2 of the S-arc. Limit primitive (generic version subsuming Cone).
-- For a diagram D : J → C, a limit is a universal cone over D.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Limit where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record Limit
  {ℓOC ℓMC ℓOJ ℓMJ : Level}
  (J : CategoryOf {ℓOJ} {ℓMJ})
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : Functor J C) : Set (lsuc (ℓOC ⊔ ℓMC ⊔ ℓOJ ⊔ ℓMJ)) where
  field
    limit-obj : CategoryOf.Obj C
    -- Universal cone data + universal property: user obligations.
