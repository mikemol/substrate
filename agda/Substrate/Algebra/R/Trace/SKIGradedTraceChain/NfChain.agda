------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.NfChain
--
-- Defines: nf-chain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.NfChain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.Chain



-- the empty chain (a normal form reached): total cost 0.
nf-chain : Chain 0
nf-chain = nil
