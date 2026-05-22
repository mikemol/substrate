------------------------------------------------------------------------
-- Substrate.Category.Colimit
--
-- S3 of the S-arc. Colimit primitive (dual of S2 Limit): for a
-- diagram D : J → C, a colimit is a universal cocone.
--
-- Semantically: `Colimit J C D ≡ Limit (Opposite J) (Opposite C) D^op`
-- via the Substrate.Category.Opposite witness. The two records share
-- a one-field skeleton (the apex/colimit object) because the
-- substrate-pragmatic minimum defers the universal-property content
-- to user obligations.
--
-- A future expansion that promotes the universal property to first-
-- class content should consider replacing Colimit with the type-alias
-- form once the Functor-on-Opposite coercion lands (currently the
-- alias would require a Functor C J ↔ Functor (Opposite C) (Opposite J)
-- iso that the substrate doesn't yet have).
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
