------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.Shed1
--
-- Defines: shed1
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.Shed1 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed



-- a single shed of cost 1 (an I/K/S head-redex contraction), as a grade-1 leaf.
shed1 : Tm → Chain 1
shed1 t = leaf (shed⟨ t ⟩)
