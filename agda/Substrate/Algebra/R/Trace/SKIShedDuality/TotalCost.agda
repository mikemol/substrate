------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.TotalCost
--
-- Defines: total-cost
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.TotalCost where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost



-- total-cost of a reduction sequence (list of shed terms): Σ cost.
total-cost : List Tm → ℕ
total-cost []       = 0
total-cost (t ∷ ts) = cost t ℕ+ total-cost ts
