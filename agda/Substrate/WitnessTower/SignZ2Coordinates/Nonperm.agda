------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.Nonperm
--
-- Defines: σ-nonperm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.Nonperm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Enumerate



-- CIRCUMSTANCE 2 — it FAILS off permutations: a concrete non-perm witness
-- (σ = zero ∷ zero ∷ [] ∉ IsPerm, p = suc zero): sign = false, oddB 1 xor false = true.
σ-nonperm : Perm 2
σ-nonperm = zero ∷ zero ∷ []
