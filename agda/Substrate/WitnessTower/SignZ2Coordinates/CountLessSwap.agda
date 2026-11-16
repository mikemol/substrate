------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountLessSwap
--
-- Defines: countLess-swap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountLessSwap where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.PlusSwap



-- countLess is invariant under an adjacent swap (addition is commutative).
countLess-swap : {m k : ℕ} (x : Fin m) (j : Fin k) (v : Vec (Fin m) (suc k)) →
                 countLess x (swapAdj j v) ≡ countLess x v
countLess-swap x zero    (a ∷ b ∷ zs) =
  +-swap (boolToℕ (finLt b x)) (boolToℕ (finLt a x)) (countLess x zs)
countLess-swap x (suc j) (a ∷ xs)     =
  cong (boolToℕ (finLt a x) ℕ+_) (countLess-swap x j xs)
