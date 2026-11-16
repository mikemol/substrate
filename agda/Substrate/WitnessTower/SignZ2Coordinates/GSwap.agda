------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.GSwap
--
-- Defines: G-swap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.GSwap where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.CountLessSwap
open import Substrate.WitnessTower.SignZ2Coordinates.G



-- G invariant under an adjacent swap of the base.
G-swap : {m : ℕ} (p : Fin (suc m)) {k : ℕ} (j : Fin k) (v : Vec (Fin m) (suc k)) →
         countLess p (map (punchIn p) (swapAdj j v)) ≡ countLess p (map (punchIn p) v)
G-swap p j v =
  trans (cong (countLess p) (map-swapAdj (punchIn p) j v))
        (countLess-swap p j (map (punchIn p) v))
