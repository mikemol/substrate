------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain
--
-- Defines: Chain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.SkiProduct



------------------------------------------------------------------------
-- 3. THE COST-CARRYING REDUCTION SEQUENCE = a WedgeTerm over ski-product. Its
-- grade is the ACCUMULATED total cost (the sum of the leaf cost-grades) — KEPT by
-- construction (WedgeTerm keeps every factor). A concrete chain of three sheds of
-- costs 1, 1, 1 has total grade 1+(1+(1+0)) = 3 — the real total redex-cost.
------------------------------------------------------------------------
Chain : ℕ → Set                                       -- a SKI shedding chain of total cost n
Chain n = WedgeTerm ski-product n
