------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.ObjCanon
--
-- Defines: objₛ-canon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.ObjCanon where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.Private


objₛ-canon : {n : ℕ} (x : Objₛ n) → x ≡ ⋆
objₛ-canon ⋆ = refl

-- UIP on ℕ specialised: any two grade-equalities coincide (thin homs).
