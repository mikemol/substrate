------------------------------------------------------------------------
-- Substrate.Linguistic.NaturalPresheafMorphism
--
-- B6 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Refines Y8's PresheafMorphism with a NATURALITY witness. A
-- natural transformation between contravariant presheaves
-- P, Q : LanguageCategory^op → Set consists of:
--   * Component α-X : P X → Q X for each object X
--   * Naturality: for f : X → Y, the square commutes:
--       α-X ∘ P(f) ≡ Q(f) ∘ α-Y     (contravariant action)
--
-- For our specific case P = よ L (= λ X → Hom(X, L)), the
-- contravariant action of f : X → Y is post-composition:
--   よ L (f) : Hom(Y, L) → Hom(X, L), h ↦ h ∘L f
--
-- Closing the Y9 deferral requires this naturality witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.NaturalPresheafMorphism where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws using (_≈M_)
open import Substrate.Linguistic.HomFunctor using (Hom-contra)
open import Substrate.Linguistic.YonedaEmbedding using (よ; PresheafMorphism)

------------------------------------------------------------------------
-- 1. Naturality predicate.
--
-- For α : よ L ⇒ よ M (where component α-X : Hom(X, L) → Hom(X, M)),
-- naturality says: for f : X → Y and h : Hom(Y, L),
--   α-X (h ∘L f) ≡ (α-Y h) ∘L f
--
-- (The "square" commutes after expanding よ's contravariant action.)
------------------------------------------------------------------------

-- Naturality up to _≈M_ (extensional equivalence on
-- LanguageMorphism). Substrate-honest given that ∘L produces
-- η-coherence witnesses that differ between associated
-- compositions; _≈M_ is the right equivalence here.
IsNatural :
  {L M : Lang}
  (α : (X : Lang) → よ L X → よ M X) →
  Set
IsNatural {L} {M} α =
  {X Y : Lang}
  (f : LanguageMorphism (witness-of X) (witness-of Y))
  (h : よ L Y) →
  α X (h ∘L f) ≈M (α Y h) ∘L f

------------------------------------------------------------------------
-- 2. Natural-presheaf-morphism record.
--
-- Bundles the component-wise function with the naturality witness.
------------------------------------------------------------------------

record NaturalPresheafMorphism
  (L M : Lang) : Set where
  field
    nat-component : (X : Lang) → よ L X → よ M X
    nat-witness   : IsNatural {L} {M} nat-component

open NaturalPresheafMorphism public

------------------------------------------------------------------------
-- 3. Forgetting naturality: a NaturalPresheafMorphism is in
-- particular a PresheafMorphism.
------------------------------------------------------------------------

forget-naturality :
  {L M : Lang} (α : NaturalPresheafMorphism L M) →
  PresheafMorphism (よ L) (よ M) (nat-component α)
forget-naturality α = record {}

------------------------------------------------------------------------
-- 4. Capstone for B6.
--
-- Naturality is now part of the morphism record. B7 shows that
-- the yoneda-backward from Y9 (i.e., よ-presheaf-mor) PRODUCES
-- natural transformations; B8 uses naturality to close Y9's
-- reverse-direction deferral.
------------------------------------------------------------------------
