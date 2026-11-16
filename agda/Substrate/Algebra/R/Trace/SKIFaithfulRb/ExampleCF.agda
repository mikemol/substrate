------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.ExampleCF
--
-- Defines: exampleCF
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.ExampleCF where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.CF



-- a concrete faithful CF: contract K (arity 2) then I (arity 1).
exampleCF : CF
exampleCF = gK ∷ gI ∷ []
