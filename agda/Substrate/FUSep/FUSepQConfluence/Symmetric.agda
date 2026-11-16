------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Symmetric
--
-- Defines: σ-symmetric
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Symmetric where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Iso
open import Substrate.FUSep.FUSepQConfluence.RIdx
open import Substrate.FUSep.FUSepQConfluence.PIdx
open import Substrate.FUSep.FUSepQConfluence.Op



------------------------------------------------------------------------
-- THE HEXAGON / SYMMETRY: σ is its OWN inverse (σ ∘ σ = id) — the symmetric-
-- monoidal law, and here the sharpest form of confluence: swapping the two
-- indexes twice returns exactly the original. reduce∘peel∘(reorder)∘(reorder) =
-- reduce∘peel — the two orders CONVERGE (the diamond closes).
------------------------------------------------------------------------
σ-symmetric : (b : RIdx × PIdx) → bwd σ (fwd σ b) ≡ b
σ-symmetric b = refl
