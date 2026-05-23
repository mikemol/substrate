------------------------------------------------------------------------
-- Substrate.Category.Cone.PullbackInstance
--
-- The Pullback-Of f g IS a Cone instance over a 3-element base
-- {A, B, C} where f : A → C and g : B → C is the cospan.
--
-- The cone has 3 legs:
--   * leg-A : Pullback-Of f g → A (= pullback-π₁)
--   * leg-B : Pullback-Of f g → B (= pullback-π₂)
--   * leg-C : Pullback-Of f g → C (= f ∘ π₁ which equals g ∘ π₂ at
--     the pullback)
--
-- The cospan morphisms aren't first-class in the discrete Cone, but
-- the pullback condition (f ∘ leg-A ≡ g ∘ leg-B) is implicit in
-- Pullback-Of's Σ-witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.PullbackInstance where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.Cone
open import Substrate.Category.Pullback
  using (Pullback-Of; pullback-π₁; pullback-π₂)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: Pullback's base diagram = {A, B, C} as Fin 3 → Set.
------------------------------------------------------------------------

pullback-Base : (A B C : Set ℓ) → Fin 3 → Set ℓ
pullback-Base A B C zero             = A
pullback-Base A B C (suc zero)       = B
pullback-Base A B C ₂ = C

------------------------------------------------------------------------
-- N-2: Pullback's Cone — apex is Pullback-Of f g.
--
-- Three legs: π₁ to A, π₂ to B, f ∘ π₁ to C (which equals g ∘ π₂ by
-- the pullback condition, captured in Pullback-Of's witness).
------------------------------------------------------------------------

pullback-as-Cone :
  {A B C : Set ℓ} (f : A → C) (g : B → C) →
  Cone 3 (pullback-Base A B C) (Pullback-Of f g)
pullback-as-Cone {A = A} {B = B} {C = C} f g = record
  { leg = λ where
      zero             → pullback-π₁
      (suc zero)       → pullback-π₂
      ₂ → λ p → f (pullback-π₁ p)
  }

------------------------------------------------------------------------
-- N-3: Capstone — Pullback is a (3, 1)-shape Cone instance.
--
-- The cospan morphisms (f : A → C, g : B → C) aren't tracked in the
-- discrete Cone, but the pullback's universal property (f ∘ π₁ ≡
-- g ∘ π₂) is captured in Pullback-Of's Σ-witness.
--
-- Together with EqualizerInstance, this shows Cone (#9) subsumes
-- both Equalizer (#2) and Pullback (#3) as 2-base and 3-base
-- instances respectively.
------------------------------------------------------------------------
