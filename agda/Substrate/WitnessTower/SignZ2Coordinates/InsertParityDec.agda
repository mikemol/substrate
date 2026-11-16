------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.InsertParityDec
--
-- Defines: insert-parity-dec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.InsertParityDec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Negation.Dec
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.InsertParityLaw
open import Substrate.WitnessTower.SignZ2Coordinates.DecB



insert-parity-dec : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → Dec (insert-parity-law p σ)
insert-parity-dec p σ = sign (insert-at p σ) ≟B (oddB (toℕ p) xor sign σ)
