------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.FaithfulRb
--
-- Defines: faithful-rb
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.FaithfulRb where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyMany
open import Substrate.Lojban.Bridi



------------------------------------------------------------------------
-- ③ THE FAITHFUL rb, as the antilog of the arity. rb takes the generator and its
-- argument list (of length = arity) and builds the redex spine. The generator is
-- kept (the CF quotient); the arity determines the iteration depth. ONE rb — its
-- behaviour VARIES with arity because it iterates apply, the antilog/pow structure.
------------------------------------------------------------------------
faithful-rb : Gen-SKI → List Tm → Tm
faithful-rb g args = apply-many (gen→tm g) args
