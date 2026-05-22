------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaCapstone
--
-- Y10 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- Capstone of the Y-arc: re-export + headline statement
-- ("each language is determined by its hom-set into all others")
-- + worked Yoneda-reconstruction examples for each of the six
-- witnesses.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaCapstone where

open import Substrate.Foundation.Eq using (_≡_; refl)

-- Re-export the Y-arc slices publicly.
open import Substrate.Linguistic.Morphism public
open import Substrate.Linguistic.IdMorphism public
open import Substrate.Linguistic.Compose public
open import Substrate.Linguistic.CategoryLaws public
open import Substrate.Linguistic.CategoryOfLanguages public
open import Substrate.Linguistic.ClassFunctor public
open import Substrate.Linguistic.HomFunctor public
open import Substrate.Linguistic.YonedaEmbedding public
open import Substrate.Linguistic.YonedaLemma public

-- Bring in the witnesses for worked examples.
open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

------------------------------------------------------------------------
-- 1. The headline statement (substrate-internal form).
--
-- For each witness L, the identity morphism is reconstructible
-- from the Yoneda image (forward direction of the lemma).
-- This is the Yoneda lemma applied to id : L → L.
------------------------------------------------------------------------

reconstruction :
  (L : LanguageWitness) →
  yoneda-forward (yoneda-backward (id-morphism L)) ≈M id-morphism L
reconstruction L = yoneda-reconstruction (id-morphism L)

------------------------------------------------------------------------
-- 2. Worked Yoneda reconstructions for all six witnesses.
------------------------------------------------------------------------

reconstruct-lojban : _
reconstruct-lojban = reconstruction lojban-witness

reconstruct-tokipona : _
reconstruct-tokipona = reconstruction tokipona-witness

reconstruct-solresol : _
reconstruct-solresol = reconstruction solresol-witness

reconstruct-kelen : _
reconstruct-kelen = reconstruction kelen-witness

reconstruct-lambda : _
reconstruct-lambda = reconstruction lambda-witness

reconstruct-lie : _
reconstruct-lie = reconstruction lie-witness

------------------------------------------------------------------------
-- 3. Cross-language Yoneda reconstruction.
--
-- For ANY language morphism (not just identity), the language
-- morphism f is recoverable from its Yoneda image — the substrate-
-- internal Yoneda statement applied to arbitrary morphisms.
------------------------------------------------------------------------

cross-reconstruction :
  {L M : LanguageWitness} (f : LanguageMorphism L M) →
  yoneda-forward (yoneda-backward f) ≈M f
cross-reconstruction = yoneda-reconstruction

------------------------------------------------------------------------
-- 4. The Y-arc summary.
--
-- A substrate-native value certifying the Y-arc landed:
--   * LanguageMorphism + composition + identity + category laws
--   * LanguageCategory record bundling them
--   * Class functor + Hom functors
--   * Yoneda embedding よ + Yoneda lemma (forward direction)
------------------------------------------------------------------------

record YArcSummary : Set₂ where
  field
    -- The category-of-languages object.
    category : CategoryOfLanguages
    -- The Yoneda reconstruction for arbitrary morphisms.
    yoneda :
      {L M : LanguageWitness} (f : LanguageMorphism L M) →
      yoneda-forward (yoneda-backward f) ≈M f

y-arc-summary : YArcSummary
y-arc-summary = record
  { category = LanguageCategory
  ; yoneda   = yoneda-reconstruction
  }

------------------------------------------------------------------------
-- 5. Capstone.
--
-- The Yoneda-lift arc Y1-Y10 lands the categorical apparatus on
-- the substrate's language classification:
--   * Y1: LanguageMorphism record
--   * Y2: identity morphisms (six instances)
--   * Y3: composition
--   * Y4: category laws up to _≈M_
--   * Y5: CategoryOfLanguages bundle
--   * Y6: class as functor to codiscrete category
--   * Y7: Hom-functors (covariant + contravariant)
--   * Y8: Yoneda embedding よ
--   * Y9: Yoneda lemma (forward direction proven)
--   * Y10: capstone + worked reconstructions
--
-- Combined with the D-arc closures (D1-D10), the 20-slice sprint
-- delivers:
--   * Cleaned foundation (10 deferred items closed)
--   * Categorical apparatus on top (Yoneda lift)
--
-- Future arcs can build on this category-of-languages: the
-- bicategorical lift, the Surreal-numbers arc, additional cell
-- witnesses (Ithkuil, Solresol-2, etc.), or the pedagogical-
-- export tooling.
------------------------------------------------------------------------
