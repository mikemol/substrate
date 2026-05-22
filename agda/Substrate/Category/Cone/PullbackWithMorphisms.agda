------------------------------------------------------------------------
-- Substrate.Category.Cone.PullbackWithMorphisms
--
-- Pullback-Of f g as a ConeWithMorphisms instance: the cospan
-- (f : A → C, g : B → C) is first-class in the base diagram.
--
-- The base diagram:
--   * 3 objects: A (index 0), B (index 1), C (index 2).
--   * 2 morphisms: f : A → C, g : B → C.
--
-- The cone:
--   * Apex = Pullback-Of f g.
--   * leg 0 = pullback-π₁, leg 1 = pullback-π₂, leg 2 = f ∘ pullback-π₁.
--   * Commutativity for f: f (π₁ p) ≡ f (π₁ p) — refl.
--   * Commutativity for g: g (π₂ p) ≡ f (π₁ p) — by sym (pullback-square).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.PullbackWithMorphisms where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)

open import Substrate.Category.Cone.WithMorphisms
open import Substrate.Category.Pullback
  using (Pullback-Of; pullback-π₁; pullback-π₂; pullback-square)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: The cospan base diagram.
--
-- 3 objects (A=0, B=1, C=2) and 2 morphisms (f : A → C, g : B → C).
-- Bool names the morphisms: false names f, true names g.
------------------------------------------------------------------------

pb-Base : (A B C : Set ℓ) → Fin 3 → Set ℓ
pb-Base A B C zero             = A
pb-Base A B C (suc zero)       = B
pb-Base A B C (suc (suc zero)) = C

pb-mor-src : Bool → Fin 3
pb-mor-src false = zero               -- f : A → C
pb-mor-src true  = suc zero           -- g : B → C

pb-mor-tgt : Bool → Fin 3
pb-mor-tgt _ = suc (suc zero)         -- both target C

pb-mor-apply :
  {A B C : Set ℓ} (f : A → C) (g : B → C) →
  (m : Bool) → pb-Base A B C (pb-mor-src m) → pb-Base A B C (pb-mor-tgt m)
pb-mor-apply f g false = f
pb-mor-apply f g true  = g

------------------------------------------------------------------------
-- N-2: Pullback-Of as ConeWithMorphisms.
--
-- commute case-matches on m inline so that the leg's lambda is
-- reduced at each case (avoids Agda's reluctance to reduce the leg
-- lambda when given an abstract m).
------------------------------------------------------------------------

pullback-as-cone-with-morphisms :
  {A B C : Set ℓ} (f : A → C) (g : B → C) →
  ConeWithMorphisms 3 (pb-Base A B C) Bool
                    pb-mor-src pb-mor-tgt
                    (pb-mor-apply f g)
                    (Pullback-Of f g)
pullback-as-cone-with-morphisms f g = record
  { leg = λ where
      zero             → pullback-π₁
      (suc zero)       → pullback-π₂
      (suc (suc zero)) → λ p → f (pullback-π₁ p)
  ; commute = λ where
      false p → refl
      true  p → sym (pullback-square p)
  }
