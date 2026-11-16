------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountBelowNExact
--
-- Defines: countBelowN-exact
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountBelowNExact where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowN
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowNZero
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowNMapSuc



countBelowN-exact : (t m : ℕ) → t ≤ m → countBelowN t (id-perm m) ≡ t
countBelowN-exact zero    m       le       = countBelowN-zero (id-perm m)
countBelowN-exact (suc t) zero    ()
countBelowN-exact (suc t) (suc m) (s≤s le) =
  trans (cong (countBelowN (suc t) {suc m} {suc m}) id-perm-cons)
        (cong suc (trans (countBelowN-map-suc t (id-perm m)) (countBelowN-exact t m le)))
