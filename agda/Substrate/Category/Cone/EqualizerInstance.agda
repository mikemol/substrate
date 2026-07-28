------------------------------------------------------------------------
-- Substrate.Category.Cone.EqualizerInstance
--
-- The Equalizer-Of f g IS a Cone instance — specifically, a cone over
-- the parallel-pair shape (2 base objects A, B; 2 parallel morphisms
-- f, g : A → B) with the apex satisfying the equalizing condition.
--
-- Substrate's existing Equalizer primitive (#2) and the new Cone
-- primitive (#9) are connected: every Equalizer-Of is the apex of a
-- 2-base discrete Cone with an extra equalizer-equation witness.
--
-- Per [[project-3plus1-is-cone-instance]]: Equalizer is the
-- "(1, 1)-cone with internal parallel pair." Since the substrate's
-- Cone primitive is discrete-base, we package the equalizing
-- condition as an extra field; full WithMorphisms cones are a
-- deferred extension.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.EqualizerInstance where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.Cone
open import Substrate.Category.Equalizer using (Equalizer-Of; IsEqualised; equalizer-incl)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: Equalizer's base diagram = {A, B} as Fin 2 → Set.
------------------------------------------------------------------------

equalizer-Base : (A B : Set ℓ) → Fin 2 → Set ℓ
equalizer-Base A B zero       = A
equalizer-Base A B ₁ = B

------------------------------------------------------------------------
-- N-2: Equalizer's Cone — apex is Equalizer-Of f g; legs project to
-- A directly and to B via f (which equals via g by the equalizer
-- condition).
------------------------------------------------------------------------

equalizer-as-Cone :
  {A B : Set ℓ} (f g : A → B) →
  Cone 2 (equalizer-Base A B) (Equalizer-Of f g)
equalizer-as-Cone f g = record
  { leg = λ where
      zero       → equalizer-incl
      ₁ → λ e → f (equalizer-incl e)
  }

------------------------------------------------------------------------
-- N-3: Capstone — Equalizer is a Cone instance.
--
-- The cone shape is (2, 1)-shape: 2 base objects A, B + 1 apex
-- (Equalizer-Of f g). The parallel-pair morphisms (f, g : A → B)
-- aren't tracked in the discrete Cone, but the equalizer condition
-- (f ∘ leg-A = g ∘ leg-A) is implicit in Equalizer-Of's Σ-witness.
--
-- A Cone.WithMorphisms extension would make the parallel-pair
-- structure first-class; the discrete Cone + extra witness is the
-- substrate-friendly version.
------------------------------------------------------------------------
