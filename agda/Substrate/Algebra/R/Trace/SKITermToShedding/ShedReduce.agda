------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.ShedReduce
--
-- Defines: shed-reduce
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.ShedReduce where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.ShedStep



-- the two SPPF reads of a shed, BOTH carrying real data (neither collapsed):
--   gforget = the REDUCE read: rebuild the parent (f∙a) — the cost-bearing whole.
--   gcell   = the PEEL read: keep the remainder = the peeled subterm a — the structure.
shed-reduce : (n : ℕ) (f a : Tm) → Tm
shed-reduce n f a = gforget (shed-step n f a)             -- = f ∙ a (the parent)
