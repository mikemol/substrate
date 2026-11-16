------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.AllPositions
--
-- Defines: all-positions
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.AllPositions where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.MapL



------------------------------------------------------------------------
-- 3. The iterative enumeration. perms (suc n) = for every smaller perm,
--    insert the new element at every one of the (suc n) positions.
------------------------------------------------------------------------

all-positions : (n : ℕ) → List (Fin n)
all-positions zero    = []
all-positions (suc n) = zero ∷ mapL suc (all-positions n)
