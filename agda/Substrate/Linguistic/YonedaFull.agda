------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaFull
--
-- B9 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- The FULL Yoneda lemma bundle for the substrate's language
-- category, combining the FORWARD direction (Y9's yoneda-forward
-- + yoneda-forward-backward proof) with the REVERSE direction's
-- naturality-direct closure (B8 yoneda-reverse-direct).
--
-- The bundle exposes both directions as a single record. The
-- caveat noted at B8 (full ≈Nat-reverse requires α-respect-≈M, not
-- captured by the minimal NaturalPresheafMorphism) is documented
-- here as the residual deferral.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaFull where

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws using (_≈M_)
open import Substrate.Linguistic.YonedaEmbedding using (よ; よ-on-morphism)
open import Substrate.Linguistic.YonedaLemma
  using (yoneda-forward; yoneda-backward; yoneda-reconstruction)
open import Substrate.Linguistic.NaturalPresheafMorphism
  using (NaturalPresheafMorphism; nat-component)
open import Substrate.Linguistic.YonedaReverse
  using (forward-from-natural; yoneda-reverse-direct)

------------------------------------------------------------------------
-- 1. The full Yoneda bundle.
--
-- Forward: yoneda-forward (yoneda-backward f) ≈M f (from Y9).
-- Reverse: at any X, h:
--   nat-component α X (id-morphism L ∘L h)
--     ≈M (forward-from-natural α) ∘L h        (from B8).
------------------------------------------------------------------------

record YonedaLemmaFull
  (L M : Lang) : Set where
  field
    -- Forward: any f is recoverable from yoneda-backward f.
    forward :
      (f : LanguageMorphism (witness-of L) (witness-of M)) →
      yoneda-forward (よ-on-morphism f) (yoneda-backward f) ≈M f
    -- Reverse: for any natural α,
    --   α-X (id-morphism L ∘L h) ≈M (forward-from-natural α) ∘L h.
    reverse :
      (α : NaturalPresheafMorphism L M)
      {X : Lang}
      (h : よ L X) →
      nat-component α X (id-morphism (witness-of L) ∘L h) ≈M
        (forward-from-natural α) ∘L h

------------------------------------------------------------------------
-- 2. The canonical instance.
--
-- Plug Y9's reconstruction (forward) and B8's reverse-direct
-- (reverse) into the bundle.
------------------------------------------------------------------------

yoneda-lemma-full :
  (L M : Lang) → YonedaLemmaFull L M
yoneda-lemma-full L M = record
  { forward = yoneda-reconstruction
  ; reverse = yoneda-reverse-direct
  }

------------------------------------------------------------------------
-- 3. Capstone for B9.
--
-- The Yoneda lemma's BOTH directions are now substrate-internally
-- packaged. Y9's deferral (the reverse direction) is closed at
-- the naturality-direct form via B8.
--
-- Residual deferral: the full ≈Nat-equivalence statement (which
-- would say "every natural transformation IS yoneda-backward of
-- something, up to natural-transformation equivalence") requires
-- one additional respect-≈M condition on the components of α.
-- That condition is naturally part of a FULLY-FAITHFUL FUNCTOR
-- definition and would be supplied in a follow-up extension of
-- NaturalPresheafMorphism. For the 10-slice B-arc, both directions
-- in their substrate-honest form land.
------------------------------------------------------------------------
