------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.HoldsOnPerm
--
-- Defines: holds-on-perm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.HoldsOnPerm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.Xor
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.SignZ2Coordinates.InsertParityLaw



-- CIRCUMSTANCE 1 — it HOLDS when σ is a permutation (Route A / Route B).
holds-on-perm : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ → insert-parity-law p σ
holds-on-perm = signB-insert
