------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.TotalCostIs3
--
-- Defines: total-cost-is-3
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.TotalCostIs3 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.ThreeSheds



-- the total grade of three-sheds IS 3 — the accumulated cost, carried by the type.
total-cost-is-3 : Chain 3
total-cost-is-3 = three-sheds
