------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountLessId
--
-- Defines: countLess-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountLessId where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowNExact
open import Substrate.WitnessTower.SignZ2Coordinates.CountLessBridge



countLess-id : {m : ℕ} (p : Fin (suc m)) →
               countLess p (map (punchIn p) (id-perm m)) ≡ toℕ p
countLess-id {m} p =
  trans (countLess-bridge p (id-perm m)) (countBelowN-exact (toℕ p) m (toℕ≤m p))
