------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctor
--
-- Defines: freeFunctorₛ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctor where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeObj



------------------------------------------------------------------------
-- THE CONSTRUCTION as a RigFunctor, for the concrete skeletal free object.
-- The skeletal rig-category orientationRigCatₛ is its own free object; the
-- free functor onto it is the identity endofunctor (freeObj orientationRig
-- Catₛ n = ⋆, and the identity realises it).
------------------------------------------------------------------------

freeFunctorₛ : RigFunctor orientationRigCatₛ orientationRigCatₛ
freeFunctorₛ = id-RigFunctor orientationRigCatₛ
