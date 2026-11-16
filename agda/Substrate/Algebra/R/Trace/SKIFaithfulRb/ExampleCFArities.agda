------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.ExampleCFArities
--
-- Defines: exampleCF-arities
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.ExampleCFArities where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.CF
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arities
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.ExampleCF



-- its generators are the REAL combinators, its arities the real grades [2, 1]:
exampleCF-arities : arities exampleCF ≡ (2 ∷ 1 ∷ [])
exampleCF-arities = refl
