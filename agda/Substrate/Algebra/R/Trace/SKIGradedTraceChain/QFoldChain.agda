------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.QFoldChain
--
-- Defines: q-fold-chain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.QFoldChain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.SkiProduct
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain



------------------------------------------------------------------------
-- 4. THE ACCUMULATION IS REAL (not zero-collapsed): a q-fold chain of a fixed
-- cost-1 shed has total grade q — pow-term gives it, and eval factors through
-- (eval-pow), so the chained value is the q-fold ∧ of the shed. The grade q is
-- the accumulated cost, tracked in the type, recoverable by construction.
------------------------------------------------------------------------
q-fold-chain : (b : Shed 1) (q : ℕ) → Chain (q * 1)
q-fold-chain b q = pow-term {P = ski-product} b q
