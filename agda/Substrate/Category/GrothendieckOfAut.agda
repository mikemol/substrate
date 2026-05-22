------------------------------------------------------------------------
-- Substrate.Category.GrothendieckOfAut
--
-- O2 of the O-arc. The composed functor ∫ ∘ Aut taking a carrier
-- category to the total category of automorphism actions.
--
-- Per [[grothendieck-coherence-rule]]: N1 (Aut as functor) + N3 (∫
-- as functor) compose; O2 names the composite as a substrate-level
-- functor. EMERGENT orphan from N-arc audit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; compose-Functor)

module Substrate.Category.GrothendieckOfAut
  {ℓOS ℓMS ℓOG ℓMG ℓOC ℓMC : Level}
  (CarrierCat : CategoryOf {ℓOS} {ℓMS})
  (GroupCat : CategoryOf {ℓOG} {ℓMG})
  (TotalCat : CategoryOf {ℓOC} {ℓMC})
  (Aut : Functor CarrierCat GroupCat)
  (∫ : Functor GroupCat TotalCat)
  where

GrothendieckOfAut-Functor : Functor CarrierCat TotalCat
GrothendieckOfAut-Functor = compose-Functor ∫ Aut

------------------------------------------------------------------------
-- ∫ ∘ Aut as substrate-level composed functor; downstream consumers
-- supply Aut + ∫ in concrete categories.
------------------------------------------------------------------------
