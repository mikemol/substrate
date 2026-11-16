------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountLessPunchIn
--
-- Defines: countLess-punchIn
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountLessPunchIn where

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



-- the punchIn relabel preserves the ℕ inversion count.
countLess-punchIn : {m k : ℕ} (p : Fin (suc m)) (x : Fin m) (v : Vec (Fin m) k) →
                    countLess (punchIn p x) (map (punchIn p) v) ≡ countLess x v
countLess-punchIn p x []       = refl
countLess-punchIn p x (y ∷ ys) =
  cong₂ _ℕ+_ (cong boolToℕ (finLt-punchIn p y x)) (countLess-punchIn p x ys)
