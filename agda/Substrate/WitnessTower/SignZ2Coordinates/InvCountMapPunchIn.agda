------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.InvCountMapPunchIn
--
-- Defines: invCount-map-punchIn
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.InvCountMapPunchIn where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.CountLessPunchIn



invCount-map-punchIn : {m k : ℕ} (p : Fin (suc m)) (v : Vec (Fin m) k) →
                       invCount (map (punchIn p) v) ≡ invCount v
invCount-map-punchIn p []       = refl
invCount-map-punchIn p (x ∷ xs) =
  cong₂ _ℕ+_ (countLess-punchIn p x xs) (invCount-map-punchIn p xs)
