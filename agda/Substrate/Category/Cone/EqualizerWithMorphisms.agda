------------------------------------------------------------------------
-- Substrate.Category.Cone.EqualizerWithMorphisms
--
-- Equalizer-Of f g as a ConeWithMorphisms instance: the parallel
-- pair (f, g : A → B) is first-class in the base diagram, and the
-- cone's leg-commutativity captures the equalizing condition.
--
-- The base diagram:
--   * 2 objects: A (at Fin 2's zero), B (at Fin 2's suc zero).
--   * 2 morphisms: f and g, both from A to B.
--
-- The cone:
--   * Apex = Equalizer-Of f g.
--   * leg 0 = equalizer-incl.
--   * leg 1 = f ∘ equalizer-incl.
--   * Commutativity for f: f (leg 0 e) ≡ leg 1 e — refl by definition.
--   * Commutativity for g: g (leg 0 e) ≡ leg 1 e — by sym (equalizer-eq).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.EqualizerWithMorphisms where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)

open import Substrate.Category.Cone.WithMorphisms
open import Substrate.Category.Equalizer
  using (Equalizer-Of; equalizer-incl; equalizer-eq)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: The parallel-pair base diagram.
--
-- 2 objects (A at index 0, B at index 1) and 2 morphisms (f and g,
-- both A → B). We use Bool as the BaseMor name-type: false names f,
-- true names g.
------------------------------------------------------------------------

eq-Base : (A B : Set ℓ) → Fin 2 → Set ℓ
eq-Base A B zero       = A
eq-Base A B ₁ = B

eq-mor-src : Bool → Fin 2
eq-mor-src _ = zero

eq-mor-tgt : Bool → Fin 2
eq-mor-tgt _ = suc zero

eq-mor-apply : {A B : Set ℓ} (f g : A → B) →
               (m : Bool) → A → B
eq-mor-apply f g false = f
eq-mor-apply f g true  = g

------------------------------------------------------------------------
-- N-2: The cone's commute proof per base morphism.
--
-- For "false" (= f): f (leg 0 e) = f (equalizer-incl e) = leg 1 e
--                    by definition of leg 1. Refl.
-- For "true"  (= g): g (leg 0 e) = g (equalizer-incl e), and
--                    leg 1 e = f (equalizer-incl e). The cone's
--                    commute requires g (equalizer-incl e) ≡
--                    f (equalizer-incl e) = sym (equalizer-eq e).
------------------------------------------------------------------------

eq-commute :
  {A B : Set ℓ} (f g : A → B) (m : Bool) (e : Equalizer-Of f g) →
  eq-mor-apply f g m (equalizer-incl e) ≡ f (equalizer-incl e)
eq-commute f g false e = refl
eq-commute f g true  e = sym (equalizer-eq e)

------------------------------------------------------------------------
-- N-3: Equalizer-Of as ConeWithMorphisms.
------------------------------------------------------------------------

equalizer-as-cone-with-morphisms :
  {A B : Set ℓ} (f g : A → B) →
  ConeWithMorphisms 2 (eq-Base A B) Bool
                    eq-mor-src eq-mor-tgt
                    (eq-mor-apply f g)
                    (Equalizer-Of f g)
equalizer-as-cone-with-morphisms f g = record
  { leg = λ where
      zero       → equalizer-incl
      ₁ → λ e → f (equalizer-incl e)
  ; commute = eq-commute f g
  }
