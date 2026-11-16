------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.DivergeHeadIsCost
--
-- Defines: diverge-head-is-cost
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.DivergeHeadIsCost where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Product
open import Substrate.Foundation.Unit
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost
open import Substrate.Algebra.R.Trace.SKIShedDuality.DivergeCostStream



-- the head IS the shed cost at every step (1 for Ω) — carried, not collapsed.
diverge-head-is-cost : head diverge-cost-stream ≡ 1
diverge-head-is-cost = refl
