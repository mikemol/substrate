------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountLessBridge
--
-- Defines: countLess-bridge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountLessBridge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.CountBelowN



-- countLess p ∘ map (punchIn p) IS the ℕ count at bound toℕ p (via punchIn-lt).
countLess-bridge : {m k : ℕ} (p : Fin (suc m)) (v : Vec (Fin m) k) →
                   countLess p (map (punchIn p) v) ≡ countBelowN (toℕ p) v
countLess-bridge p []       = refl
countLess-bridge p (x ∷ xs) =
  cong₂ _ℕ+_ (cong boolToℕ (punchIn-lt p x)) (countLess-bridge p xs)
