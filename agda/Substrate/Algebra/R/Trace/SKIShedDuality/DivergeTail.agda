------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.DivergeTail
--
-- Defines: diverge-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.DivergeTail where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Foundation.Unit
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost
open import Substrate.Algebra.R.Trace.SKIShedDuality.Autochain
open import Substrate.Algebra.R.Trace.SKIShedDuality.DivergeCostStream



-- the tail is the same divergent stream — productive forever (the greatest fp).
diverge-tail : tail diverge-cost-stream ~ diverge-cost-stream
head~ diverge-tail = refl
tail~ diverge-tail = ~-refl (tail diverge-cost-stream)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the duality made explicit on ONE base): the SN
-- and Diverges sides are the INITIAL-algebra and TERMINAL-coalgebra reads of the
-- SAME (Tm, cost). autochain (fold side, WedgeTerm/trace-fold) accumulates the real
-- costs inductively; diverge-cost-stream (unfold side, RealTrace/ana) emits the real
-- costs coinductively. Both carry cost — neither collapses. The "SN vs Diverges"
-- and "the two mis-grounded modules" either/ors dissolve: ONE Tm, ONE cost, the
-- fold⊣unfold (ℚ⊣R) duality. The local-Tm duplication (ADD 147/148) is residue —
-- this shared base is the grounded form. ⟡ski-cost-autochain = the fold side wired;
-- ⟡ski-graded-diverges = the unfold side, both discharged here.
------------------------------------------------------------------------
