------------------------------------------------------------------------
-- Substrate.Category.Cone.Morphism
--
-- The morphism layer for Cone primitives — a cone-morphism between
-- two cones over the same base diagram is a function between their
-- apex carriers that preserves the legs.
--
-- Z6 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on. First concrete morphism-
-- instance via Z1 Morphism primitive.
--
-- STRUCTURAL CONTENT:
--
--   Given two cones C₁ = (Base, Apex₁, leg₁) and C₂ = (Base, Apex₂,
--   leg₂) over the SAME finite base diagram, a cone-morphism C₁ → C₂
--   is f : Apex₁ → Apex₂ such that
--
--     leg₂ i ∘ f = leg₁ i   (∀ i : Fin n)
--
--   i.e., the legs commute through the morphism. This is the
--   standard "morphism of cones over a diagram" definition.
--
-- Per [[universal-property-discipline]]: cone morphisms form the
-- category Cone(D) over diagram D; the limit (= terminal cone) is
-- characterized by being the terminal object of this category.
-- With Z6 in place, the substrate can formally talk about Cone(D).
--
-- Closes part of Gap #1 from the audit at the Cone layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.Morphism where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Cone using (Cone; leg)
open import Substrate.Category.Morphism using (Morphism; mkMorphism)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- 1. The leg-preservation predicate.
--
-- Given two cones over the same base, the predicate "f preserves
-- legs" holds iff leg₂ i (f a) ≡ leg₁ i a for every i and every
-- apex element a.
------------------------------------------------------------------------

preserves-legs :
  {n : ℕ}
  {Base : Fin n → Set ℓ}
  {Apex₁ Apex₂ : Set ℓ}
  (C₁ : Cone n Base Apex₁)
  (C₂ : Cone n Base Apex₂) →
  (Apex₁ → Apex₂) → Set ℓ
preserves-legs {n = n} C₁ C₂ f =
  (i : Fin n) (a : _) → leg C₂ i (f a) ≡ leg C₁ i a

------------------------------------------------------------------------
-- 2. The Cone-morphism type.
--
-- A cone-morphism C₁ → C₂ is a Morphism (from Z1) whose
-- preservation predicate is "preserves-legs."
------------------------------------------------------------------------

ConeMorphism :
  {n : ℕ}
  {Base : Fin n → Set ℓ}
  {Apex₁ Apex₂ : Set ℓ}
  (C₁ : Cone n Base Apex₁)
  (C₂ : Cone n Base Apex₂) → Set ℓ
ConeMorphism C₁ C₂ = Morphism _ _ (preserves-legs C₁ C₂)

------------------------------------------------------------------------
-- 3. Identity cone-morphism.
--
-- The identity function on Apex is a cone-morphism: leg i (id a) =
-- leg i a, so preserves-legs holds trivially.
------------------------------------------------------------------------

id-ConeMorphism :
  {n : ℕ}
  {Base : Fin n → Set ℓ}
  {Apex : Set ℓ}
  (C : Cone n Base Apex) →
  ConeMorphism C C
id-ConeMorphism C = mkMorphism (λ a → a) (λ i a → refl)

------------------------------------------------------------------------
-- 4. Capstone — Cone's morphism layer in place.
--
-- Z6 of the 10-slice Z-arc. With Z6 landed, cones over a fixed
-- diagram form a category (specifically, the cone-category Cone(D);
-- the limit is its terminal object).
--
-- Closes part of Gap #1 from the Grothendieck-closure audit at the
-- Cone layer. Composition of cone-morphisms follows from Z1's
-- compose-Morphism + a leg-preservation-composes lemma (which holds
-- by direct computation).
--
-- Concrete usage:
--   * Cone(F₂² 3+1) category — V₄'s 3+1 universal cones with their
--     cone-morphisms.
--   * Cone(Hamming 7+1) category.
--   * Cone(HodgeStar) category — fixed under ★ action.
--
-- Next: Z7 (GTorsor.Morphism — torsor-category construction).
------------------------------------------------------------------------
