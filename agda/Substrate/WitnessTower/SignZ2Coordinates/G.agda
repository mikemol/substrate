------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.G
--
-- Defines: G
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.G where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality



-- the punchIn-relabelled count G p — the ℕ twin of Route A's F p.
G : {m : ℕ} (p : Fin (suc m)) → Perm m → ℕ
G p v = countLess p (map (punchIn p) v)
