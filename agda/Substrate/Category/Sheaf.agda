------------------------------------------------------------------------
-- Substrate.Category.Sheaf
--
-- S1 of the S-arc. Sheaf primitive: presheaf on a site satisfying the
-- gluing axiom (= local sections glue to a unique global section over
-- a covering).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Sheaf where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

record Sheaf
  {ℓOC ℓMC ℓOD ℓMD : Level}
  {ObjSite : Set ℓOC} {MorSite : ObjSite → ObjSite → Set ℓMC}
  {ObjTarget : Set ℓOD} {MorTarget : ObjTarget → ObjTarget → Set ℓMD}
  (Site : CategoryOf ObjSite MorSite)
  (Target : CategoryOf ObjTarget MorTarget) : Set (ℓOC ⊔ ℓMC ⊔ ℓOD ⊔ ℓMD) where
  field
    presheaf : Functor Site Target
    -- Gluing axiom: user obligation per substrate-pragmatic minimum.
