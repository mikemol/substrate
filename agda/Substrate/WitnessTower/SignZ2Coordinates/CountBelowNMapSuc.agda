------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountBelowNMapSuc
--
-- Defines: countBelowN-map-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountBelowNMapSuc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowN



countBelowN-map-suc : (t : ℕ) {m k : ℕ} (v : Vec (Fin m) k) →
                      countBelowN (suc t) (map suc v) ≡ countBelowN t v
countBelowN-map-suc t []       = refl
countBelowN-map-suc t (x ∷ xs) =
  cong (boolToℕ (toℕ x <ᵇ t) ℕ+_) (countBelowN-map-suc t xs)
