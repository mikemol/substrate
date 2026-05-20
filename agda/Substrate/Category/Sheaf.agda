------------------------------------------------------------------------
-- Substrate.Category.Sheaf
--
-- S1 of the S-arc. Sheaf primitive: presheaf on a site satisfying the
-- gluing axiom (= local sections glue to a unique global section over
-- a covering).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Sheaf where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record Sheaf
  {ℓOC ℓMC ℓOD ℓMD : Level}
  (Site : CategoryOf {ℓOC} {ℓMC})
  (Target : CategoryOf {ℓOD} {ℓMD}) : Set (lsuc (ℓOC ⊔ ℓMC ⊔ ℓOD ⊔ ℓMD)) where
  field
    presheaf : Functor Site Target
    -- Gluing axiom: user obligation per substrate-pragmatic minimum.
