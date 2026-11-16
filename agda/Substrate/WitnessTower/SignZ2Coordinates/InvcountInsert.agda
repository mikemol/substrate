------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.InvcountInsert
--
-- Defines: invcount-insert
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.InvcountInsert where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.CountLessExact
open import Substrate.WitnessTower.SignZ2Coordinates.InvCountMapPunchIn



-- THE RECURRENCE: inserting value p at the front adds exactly toℕ p inversions.
invcount-insert : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
                  invCount (insert-at p σ) ≡ toℕ p ℕ+ invCount σ
invcount-insert p σ pf =
  cong₂ _ℕ+_ (countLess-exact p σ pf) (invCount-map-punchIn p σ)
