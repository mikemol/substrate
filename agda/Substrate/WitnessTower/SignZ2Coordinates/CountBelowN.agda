------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountBelowN
--
-- Defines: countBelowN
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountBelowN where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign



-- the ℕ count over id-perm, given the bound t ≤ m, is exactly t.
countBelowN : (t : ℕ) {m k : ℕ} → Vec (Fin m) k → ℕ
countBelowN t []       = 0
countBelowN t (x ∷ xs) = boolToℕ (toℕ x <ᵇ t) ℕ+ countBelowN t xs
