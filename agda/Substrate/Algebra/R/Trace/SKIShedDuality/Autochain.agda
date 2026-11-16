------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Autochain
--
-- Defines: autochain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Autochain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.List
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost
open import Substrate.Algebra.R.Trace.SKIShedDuality.Chain
open import Substrate.Algebra.R.Trace.SKIShedDuality.CostLeaf
open import Substrate.Algebra.R.Trace.SKIShedDuality.TotalCost



-- THE AUTOCHAIN: fold a reduction sequence into a cost chain, grades ACCUMULATING
-- the ACTUAL per-term costs automatically (no hand-specified grades). The total
-- grade is total-cost ts BY CONSTRUCTION — the cost is wired, not asserted.
autochain : (ts : List Tm) → Chain (total-cost ts)
autochain []       = nil
autochain (t ∷ ts) = cost-leaf t ⊗ autochain ts
