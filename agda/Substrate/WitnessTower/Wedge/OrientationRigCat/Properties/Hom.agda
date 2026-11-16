------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.Hom
--
-- Defines: Homₛ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCat.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.Hom where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans



Homₛ : {i j : ℕ} → Objₛ i → Objₛ j → Set
Homₛ {i} {j} _ _ = i ≡ j

-- UIP on ℕ specialised: any two grade-equalities coincide.
