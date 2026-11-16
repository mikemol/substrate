------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.ThreeSheds
--
-- Defines: three-sheds
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.ThreeSheds where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Shed1
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.NfChain
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- chaining accumulates the grade: three cost-1 sheds ⟹ total cost 3 (NOT collapsed).
three-sheds : Chain (1 ℕ+ (1 ℕ+ (1 ℕ+ 0)))
three-sheds = shed1 (I ∙ K) ⊗ (shed1 (I ∙ S) ⊗ (shed1 (K ∙ I) ⊗ nf-chain))
