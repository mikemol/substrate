------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.ReduceRecovers
--
-- Defines: reduce-recovers
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.ReduceRecovers where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.Cost
open import Substrate.Algebra.R.Trace.SKITermToShedding.ShedStep
open import Substrate.Algebra.R.Trace.SKITermToShedding.ShedReduce



------------------------------------------------------------------------
-- 4. THE COSTS ARE CARRIED, NOT COLLAPSED — the operator's weakness, fixed. The
-- reduce read rebuilds the real parent (cost recoverable); the peel read keeps the
-- real subterm. Neither is zero. Witnessed: the two reads recover the actual term
-- data, and the grade carries the actual cost.
------------------------------------------------------------------------
-- the reduce read recovers the parent EXACTLY (gforget-correct — the invertibility).
reduce-recovers : (n : ℕ) (f a : Tm) → shed-reduce n f a ≡ (f ∙ a)
reduce-recovers n f a = gforget-correct (shed-step n f a)
