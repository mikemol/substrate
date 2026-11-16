------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.FailsOffPerm
--
-- Defines: fails-off-perm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.FailsOffPerm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Negation.Not
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.SignZ2Coordinates.InsertParityLaw
open import Substrate.WitnessTower.SignZ2Coordinates.Nonperm



fails-off-perm : ¬ insert-parity-law (suc zero) σ-nonperm
fails-off-perm ()
