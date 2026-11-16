------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perms
--
-- Defines: perms
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perms where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.ConcatMapL
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.AllPositions



perms : (n : ℕ) → List (Perm n)
perms zero    = [] ∷ []                       -- the empty permutation
perms (suc n) =
  concatMapL (λ σ → mapL (λ p → insert-at p σ) (all-positions (suc n)))
             (perms n)
