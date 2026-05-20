------------------------------------------------------------------------
-- Substrate.Category.GaloisAdjunction.UnitCounit
--
-- Substrate-level naming of the GaloisAdjunction's unit + counit as
-- M2 NaturalTransformation instances.
--
-- N9 of the N-arc.
--
-- T4 GaloisAdjunction packages the forward / backward functor pair
-- bridging the bottom-up (PresentedGroup) and top-down (Conjugation-
-- Coalgebra) views of a group. Per categorical convention, every
-- adjunction F ⊣ G comes with:
--   * unit η : Id_C ⇒ G ∘ F  (a natural transformation)
--   * counit ε : F ∘ G ⇒ Id_D  (a natural transformation)
-- + triangle identities.
--
-- N9 makes the unit + counit explicit M2 NaturalTransformation
-- instances, closing the M-arc OrphanAudit row "GaloisAdjunction's
-- unit + counit are implicit in the functor pair; lift to M2."
--
-- Per [[grothendieck-coherence-rule]]: the unit + counit are the
-- 2-cell witnesses for the adjunction; without M2 instantiation,
-- they are latent. N9 makes them structural.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Category.GaloisAdjunction.UnitCounit
  {ℓOC ℓMC ℓOD ℓMD : Level}
  -- The two categories joined by the adjunction.
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : CategoryOf {ℓOD} {ℓMD})
  -- The forward + backward functors (F ⊣ G).
  (F : Functor C D)
  (G : Functor D C)
  -- The unit η : Id_C ⇒ G ∘ F.
  (η : NaturalTransformation (id-Functor C) (compose-Functor G F))
  -- The counit ε : F ∘ G ⇒ Id_D.
  (ε : NaturalTransformation (compose-Functor F G) (id-Functor D))
  where

------------------------------------------------------------------------
-- 1. Unit + counit as substrate-named NaturalTransformations.
------------------------------------------------------------------------

GaloisAdjunction-unit :
  NaturalTransformation (id-Functor C) (compose-Functor G F)
GaloisAdjunction-unit = η

GaloisAdjunction-counit :
  NaturalTransformation (compose-Functor F G) (id-Functor D)
GaloisAdjunction-counit = ε

------------------------------------------------------------------------
-- 2. Capstone — GaloisAdjunction's η + ε as M2 instances.
--
-- N9 of the N-arc. With N9 landed, the substrate's T4 GaloisAdjunction
-- + Y-arc bottom-up/top-down bridge are structurally complete at the
-- 2-cell layer: unit + counit are explicit M2 NaturalTransformation
-- values, not implicit functor-pair attributes.
--
-- Per [[universal-property-discipline]]: the FULL adjunction record
-- requires the triangle identities
--   (ε F) ∘ (F η) = id_F
--   (G ε) ∘ (η G) = id_G
-- These are downstream specialisation slices (composes via the
-- substrate's #4 Adjunction primitive); N9 supplies the η + ε
-- foundation.
--
-- After N9: the substrate's 5 substrate-internal views of the
-- Monster + their bridges have full 2-cell witnesses (where
-- adjunctions are involved).
--
-- Next: N10 capstone (refresh PrimitivesAll + PrimitiveInstances +
-- OrphanAudit).
------------------------------------------------------------------------
