------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.CountLessExact
--
-- Defines: countLess-exact
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.CountLessExact where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.CyclicGrounding
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.SignZ2Coordinates.G
open import Substrate.WitnessTower.SignZ2Coordinates.GMult
open import Substrate.WitnessTower.SignZ2Coordinates.CountLessId



-- the exact count-below: for a perm σ, #{tail entries < p} = toℕ p.
countLess-exact : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
                  countLess p (map (punchIn p) σ) ≡ toℕ p
countLess-exact {m} p σ pf =
  trans (cong (G p) (sym (compose-id-left σ)))
        (trans (G-mult p (id-perm m) (coxeter-complete σ pf)) (countLess-id p))
