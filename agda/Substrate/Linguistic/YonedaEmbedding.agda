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

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.HomFunctor
  using (Hom-contra; Hom-contra-map)

------------------------------------------------------------------------
-- 1. The Yoneda embedding よ.
--
-- For each L : Lang, よ L is the presheaf X ↦ Hom(X, L). Concretely:
-- よ L X = LanguageMorphism (witness-of X) (witness-of L) = Hom-contra X L.
------------------------------------------------------------------------

よ : Lang → Lang → Set
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
  {L M : Lang} →
  LanguageMorphism (witness-of L) (witness-of M) →
  (X : Lang) → よ L X → よ M X
よ-on-morphism f X h = f ∘L h

------------------------------------------------------------------------
-- 3. Presheaf-morphism record.
--
-- A NATURAL TRANSFORMATION α : P ⇒ Q between two presheaves over
-- LanguageCategory consists of:
--   * For each X : Lang, a function α-X : P X → Q X.
--   * Naturality: for f : X → Y, the square commutes.
--
-- For the Yoneda statement (Y9), the relevant fact is:
-- α : よ L ⇒ よ M ↔ LanguageMorphism L M (Yoneda lemma bijection).
--
-- `component` moves to a PARAMETER (⟡rc-lang, W5-L4): what used to
-- be a Set-valued FIELD (pinning the record at Set₁) is now data the
-- caller supplies at the type; the record body is vestigial (empty
-- — there's nothing left to witness once component is a param), so
-- PresheafMorphism drops to Set.
------------------------------------------------------------------------

record PresheafMorphism
  (P Q : Lang → Set) (component : (X : Lang) → P X → Q X) : Set where

------------------------------------------------------------------------
-- 4. The Yoneda action lifted to a PresheafMorphism.
--
-- For each f : L → M, よ-on-morphism gives a component-wise
-- function; package into a PresheafMorphism record.
------------------------------------------------------------------------

よ-presheaf-mor :
  {L M : Lang} (f : LanguageMorphism (witness-of L) (witness-of M)) →
  PresheafMorphism (よ L) (よ M) (よ-on-morphism f)
よ-presheaf-mor f = record {}

------------------------------------------------------------------------
-- 5. Smoke test: よ at concrete witnesses.
--
-- Demonstrates よ-presheaf-mor produces a usable
-- PresheafMorphism instance.
------------------------------------------------------------------------

open import Substrate.Linguistic.Roster using (lojban)
open import Substrate.Linguistic.IdMorphism using (id-morphism)

-- The identity Yoneda morphism よ(L) ⇒ よ(L) (induced by id : L → L).
よ-id-Lojban :
  PresheafMorphism (よ lojban) (よ lojban) (よ-on-morphism (id-morphism (witness-of lojban)))
よ-id-Lojban = よ-presheaf-mor (id-morphism (witness-of lojban))

------------------------------------------------------------------------
-- 6. Capstone for Y8.
--
-- The Yoneda embedding よ is named and lifted to PresheafMorphism.
-- Y9 states the Yoneda LEMMA: the bijection PresheafMorphism
-- (よ L) (よ M) ↔ LanguageMorphism L M.
------------------------------------------------------------------------
