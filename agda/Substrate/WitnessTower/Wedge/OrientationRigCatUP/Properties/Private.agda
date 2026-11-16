------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.Private where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctor



------------------------------------------------------------------------
-- FULL uniqueness for the concrete free object (RigFunctor≈, NO Σ). Every
-- endofunctor of orientationRigCatₛ agrees with freeFunctorₛ:
--   * objects — Objₛ n is a singleton (⋆), so any object map is ⋆ ↦ ⋆;
--   * morphisms — Homₛ i j = (i ≡ j) is a mere proposition (UIP on ℕ,
--     Hedberg from decidable _≟_), so any two thin morphisms are equal.
------------------------------------------------------------------------

-- every object of grade n is ⋆ (Objₛ is the grade-indexed singleton).
