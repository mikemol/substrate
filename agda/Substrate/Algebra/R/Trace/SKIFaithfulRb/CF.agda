------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.CF
--
-- Defines: CF
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.CF where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity



------------------------------------------------------------------------
-- ④ THE CF NOW CARRIES THE REAL GENERATOR. A reduction step's quotient is the
-- contracted combinator's generator; the CF (the quotient sequence, ADD 153) is
-- the list of ACTUAL reduction generators, each with its arity as grade. Example:
-- a reduction contracting K then I has CF [gK, gI], arities [2, 1].
------------------------------------------------------------------------
CF : Set
CF = List Gen-SKI                          -- the reduction generators (the faithful shape)
