------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountBelowNZero
--
-- Defines: countBelowN-zero
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountBelowNZero where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowN



countBelowN-zero : {m k : ℕ} (v : Vec (Fin m) k) → countBelowN zero v ≡ zero
countBelowN-zero []       = refl
countBelowN-zero (x ∷ xs) = countBelowN-zero xs
