------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaEmbedding
--
-- Y8 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The contravariant Yoneda embedding よ : LanguageCategory →
-- Presheaf(LanguageCategory). For each L, よ(L) is the presheaf
-- X ↦ Hom(X, L) (the contravariant hom-functor from Y7).
--
-- The Yoneda embedding is the key tool for "studying objects by
-- their hom-sets" — the peer-review-framed Yoneda perspective on
-- the language classification.
--
-- Per [[feedback-categorical-name-first]]: this is the Yoneda
-- functor よ named exactly. Y9 states the Yoneda LEMMA (full
-- faithfulness + bijection with natural transformations).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaEmbedding where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.HomFunctor
  using (Hom-contra; Hom-contra-map)

------------------------------------------------------------------------
-- 1. The Yoneda embedding よ.
--
-- For each L : LanguageWitness, よ L is the presheaf X ↦ Hom(X, L).
-- Concretely: よ L X = LanguageMorphism X L = Hom-contra X L.
------------------------------------------------------------------------

よ : LanguageWitness → LanguageWitness → Set
よ L X = Hom-contra X L

------------------------------------------------------------------------
-- 2. The Yoneda functor's action on language morphisms.
--
-- For f : L → M, よ f : よ L → よ M is a NATURAL TRANSFORMATION of
-- presheaves. At each X, it sends (h : Hom X L) to (f ∘L h : Hom
-- X M) — post-composition.
--
-- (Note: in this direction, f : L → M induces よ L → よ M which is
-- COvariant in L. The full Yoneda statement is that this is the
-- contravariant Yoneda embedding when viewed as a functor; the
-- substrate's chosen direction matches the standard categorical
-- convention.)
------------------------------------------------------------------------

open import Substrate.Linguistic.Compose using (_∘L_)

よ-on-morphism :
  {L M : LanguageWitness} →
  LanguageMorphism L M →
  (X : LanguageWitness) → よ L X → よ M X
よ-on-morphism f X h = f ∘L h

------------------------------------------------------------------------
-- 3. Presheaf-morphism record.
--
-- A NATURAL TRANSFORMATION α : P ⇒ Q between two presheaves over
-- LanguageCategory consists of:
--   * For each X : LanguageWitness, a function α-X : P X → Q X.
--   * Naturality: for f : X → Y, the square commutes.
--
-- For the Yoneda statement (Y9), the relevant fact is:
-- α : よ L ⇒ よ M ↔ LanguageMorphism L M (Yoneda lemma bijection).
------------------------------------------------------------------------

record PresheafMorphism
  (P Q : LanguageWitness → Set) : Set₁ where
  field
    component : (X : LanguageWitness) → P X → Q X

open PresheafMorphism public

------------------------------------------------------------------------
-- 4. The Yoneda action lifted to a PresheafMorphism.
--
-- For each f : L → M, よ-on-morphism gives a component-wise
-- function; package into a PresheafMorphism record.
------------------------------------------------------------------------

よ-presheaf-mor :
  {L M : LanguageWitness} →
  LanguageMorphism L M →
  PresheafMorphism (よ L) (よ M)
よ-presheaf-mor f = record { component = よ-on-morphism f }

------------------------------------------------------------------------
-- 5. Smoke test: よ at concrete witnesses.
--
-- Demonstrates よ-presheaf-mor produces a usable
-- PresheafMorphism instance.
------------------------------------------------------------------------

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.Linguistic.IdMorphism using (id-morphism)

-- The identity Yoneda morphism よ(L) ⇒ よ(L) (induced by id : L → L).
よ-id-Lojban : PresheafMorphism (よ lojban-witness) (よ lojban-witness)
よ-id-Lojban = よ-presheaf-mor (id-morphism lojban-witness)

------------------------------------------------------------------------
-- 6. Capstone for Y8.
--
-- The Yoneda embedding よ is named and lifted to PresheafMorphism.
-- Y9 states the Yoneda LEMMA: the bijection PresheafMorphism
-- (よ L) (よ M) ↔ LanguageMorphism L M.
------------------------------------------------------------------------
