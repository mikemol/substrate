------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.UipNat
--
-- Defines: uipℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.UipNat where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.Private


uipℕ : {i j : ℕ} (p q : i ≡ j) → p ≡ q
uipℕ = Decidable⇒UIP _≟_
