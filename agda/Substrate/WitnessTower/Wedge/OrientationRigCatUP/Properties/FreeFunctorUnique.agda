------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctorUnique
--
-- Defines: freeFunctorₛ-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctorUnique where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctor
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.ObjCanon
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.UipNat



freeFunctorₛ-unique :
  (F : RigFunctor orientationRigCatₛ orientationRigCatₛ) →
  RigFunctor≈ F freeFunctorₛ
freeFunctorₛ-unique F = record
  { obj≈ = λ a → trans (objₛ-canon (F-obj F a)) (sym (objₛ-canon a))
  ; hom≈ = λ h → uipℕ _ h
  }
