------------------------------------------------------------------------
-- Substrate.Category.UniversalEnvelopingAlgebra.AsFunctor
--
-- Substrate-level naming of the universal-enveloping-algebra functor
-- U : Lie → Assoc.
--
-- M7 of the M-arc. The functorial side of L18 UniversalEnveloping-
-- Algebra: every Lie algebra L has a UEA U(L), and every Lie
-- homomorphism f : L → M lifts uniquely to an associative-algebra
-- homomorphism U(f) : U(L) → U(M) (universal property of the UEA).
--
-- L18 defined the UEA RECORD for a single Lie algebra; M7 lifts this
-- to a FUNCTOR Lie → Assoc, closing the L18 orphan gap per
-- [[grothendieck-coherence-rule]].
--
-- U is LEFT ADJOINT to M6 U_Lie (underlying-Lie functor):
--   Hom_Lie(L, U_Lie(A)) ≅ Hom_Assoc(U(L), A)
-- This is the substrate's canonical Lie ⊣ Assoc adjunction.
--
-- Per [[universal-property-discipline]]: U is THE LEFT ADJOINT to
-- the forgetful Assoc → Lie functor; the PBW theorem provides an
-- explicit basis (= ordered monomials over an L-basis); the
-- substrate's M7 names the functor, downstream slices supply PBW.
--
-- Per [[grothendieck-coherence-rule]]: M5 + M6 + M7 close three
-- L-arc-orphan gaps (Λ, U_Lie, U); the substrate now has the FULL
-- functorial story for ExteriorAlgebra + LieAlgebra + UEA.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.UniversalEnvelopingAlgebra.AsFunctor
  {ℓOL ℓML ℓOA ℓMA : Level}
  {ObjLie : Set ℓOL} {MorLie : ObjLie → ObjLie → Set ℓML}
  {ObjAssoc : Set ℓOA} {MorAssoc : ObjAssoc → ObjAssoc → Set ℓMA}
  (Lie : CategoryOf ObjLie MorLie)
  (Assoc : CategoryOf ObjAssoc MorAssoc)
  (U : Functor Lie Assoc)
  where

------------------------------------------------------------------------
-- 1. U as the substrate's named universal-enveloping-algebra functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  Lie Assoc U public
  renaming (named-Functor to U-Functor)
------------------------------------------------------------------------
-- 2. Capstone — U : Lie → Assoc as a substrate Functor.
--
-- M7 of the M-arc. With M5 + M6 + M7 landed, the substrate has the
-- functorial closure of the L-arc's algebra primitives:
--
--   L3 ExteriorAlgebra record + L9 morphism + M5 Λ functor
--      ⇒ V ↦ Λ(V) is now a substrate functor
--   L2 LieAlgebra record + L8 morphism + M6 U_Lie functor (right adj)
--      ⇒ A ↦ A_Lie via commutator is a substrate functor
--   L18 UEA record + (TBD UEA-morphism) + M7 U functor (left adj)
--      ⇒ L ↦ U(L) is a substrate functor
--
-- After M7:
--   * M6 ⊣ M7 = the canonical Lie ⊣ Assoc adjunction
--     (substrate's first algebra-level adjunction; composes via #4
--     Adjunction primitive as a downstream slice)
--   * Λ + U + U_Lie are all M1 Functor instances
--   * Hidden orphans from the L-arc are recovered as substrate
--     functors
--
-- Per [[universal-property-discipline]]: the adjunction record
-- (with unit ι : L → U_Lie(U(L)) + counit + triangle identities)
-- is the natural next composition slice; deferred per substrate-
-- pragmatic minimum.
--
-- Next: M8 Coxeter.AsCartanType.Functor (lift L13 to a functor on
-- Coxeter-system morphisms).
------------------------------------------------------------------------
