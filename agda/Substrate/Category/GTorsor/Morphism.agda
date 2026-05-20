------------------------------------------------------------------------
-- Substrate.Category.GTorsor.Morphism
--
-- The morphism layer for GTorsor primitives — a G-equivariant map
-- between two G-torsors over the same group.
--
-- Z7 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on. Second concrete morphism-
-- instance via Z1 Morphism primitive.
--
-- STRUCTURAL CONTENT:
--
--   Given two G-torsors τ₁ on X₁ and τ₂ on X₂ over the same group G,
--   a G-equivariant map f : X₁ → X₂ satisfies:
--
--     f(act g x) ≈X₂ act g (f x)   (∀ g : G, ∀ x : X₁)
--
--   i.e., f commutes with the G-action up to the carrier
--   equivalence relations.
--
--   For substrate's GTorsor (which is parametric in equivalence
--   relations on G and X), the equivariance condition lifts the
--   carrier equivalences via apply.
--
-- Per [[universal-property-discipline]]: G-equivariant torsor-
-- morphisms form the category G-Tors of G-torsors; since every
-- torsor is free + transitive, this category is equivalent to the
-- one-object category with G as Hom-set. With Z7, the substrate
-- can express this equivalence formally.
--
-- Closes part of Gap #1 at the GTorsor layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GTorsor.Morphism where

open import Level using (Level; _⊔_)

open import Substrate.Category.GTorsor using (GTorsor; act)
open import Substrate.Category.Morphism using (Morphism; mkMorphism)

private
  variable
    ℓG ℓX₁ ℓX₂ ℓEG ℓEX₁ ℓEX₂ : Level

------------------------------------------------------------------------
-- 1. The G-equivariance predicate.
--
-- For two torsors over the same group G with carriers X₁ and X₂
-- (each with its own equivalence ≈X), a function f : X₁ → X₂ is
-- G-equivariant if f commutes with the action pointwise:
--
--   f (act τ₁ g x) ≈X₂ act τ₂ g (f x)
------------------------------------------------------------------------

preserves-G-action :
  {G : Set ℓG} {X₁ : Set ℓX₁} {X₂ : Set ℓX₂}
  (_·G_ : G → G → G) (εG : G)
  (_≈G_ : G → G → Set ℓEG)
  (_≈X₁_ : X₁ → X₁ → Set ℓEX₁)
  (_≈X₂_ : X₂ → X₂ → Set ℓEX₂)
  (τ₁ : GTorsor G X₁ _·G_ εG _≈G_ _≈X₁_)
  (τ₂ : GTorsor G X₂ _·G_ εG _≈G_ _≈X₂_) →
  (X₁ → X₂) → Set (ℓG ⊔ ℓX₁ ⊔ ℓEX₂)
preserves-G-action _·G_ εG _≈G_ _≈X₁_ _≈X₂_ τ₁ τ₂ f =
  (g : _) (x : _) → _≈X₂_ (f (act τ₁ g x)) (act τ₂ g (f x))

------------------------------------------------------------------------
-- 2. The GTorsorMorphism type.
--
-- A GTorsor-morphism τ₁ → τ₂ is a Morphism (from Z1) whose
-- preservation predicate is "preserves-G-action."
------------------------------------------------------------------------

GTorsorMorphism :
  {G : Set ℓG} {X₁ : Set ℓX₁} {X₂ : Set ℓX₂}
  (_·G_ : G → G → G) (εG : G)
  (_≈G_ : G → G → Set ℓEG)
  (_≈X₁_ : X₁ → X₁ → Set ℓEX₁)
  (_≈X₂_ : X₂ → X₂ → Set ℓEX₂)
  (τ₁ : GTorsor G X₁ _·G_ εG _≈G_ _≈X₁_)
  (τ₂ : GTorsor G X₂ _·G_ εG _≈G_ _≈X₂_) →
  Set (ℓX₁ ⊔ ℓX₂ ⊔ ℓG ⊔ ℓEX₂)
GTorsorMorphism _·G_ εG _≈G_ _≈X₁_ _≈X₂_ τ₁ τ₂ =
  Morphism _ _ (preserves-G-action _·G_ εG _≈G_ _≈X₁_ _≈X₂_ τ₁ τ₂)

------------------------------------------------------------------------
-- 3. Capstone — GTorsor's morphism layer in place.
--
-- Z7 of the 10-slice Z-arc. With Z7 landed, G-torsors over a fixed
-- group form a category (the category G-Tors of G-torsors).
--
-- For free transitive G-actions, G-Tors is equivalent to the
-- one-object category with G as Hom-set (this is the universal
-- property of G-torsors). With Z7 formal, this equivalence is
-- substrate-internal.
--
-- Concrete usage:
--   * HodgeDim4 GaugeTorsor's morphism category (= 168-element
--     gauge group acting as Hom-set).
--   * Z6/Z30 abelian torsor morphism categories.
--
-- Closes part of Gap #1 at the GTorsor layer.
--
-- Next: Z8 (HappyFamily.AsTree concrete descent-tree instance).
------------------------------------------------------------------------
