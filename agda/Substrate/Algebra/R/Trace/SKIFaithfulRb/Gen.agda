------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
--
-- Defines: Gen-SKI, gI, gK, gS
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- ① The combinator GENERATORS and their ARITIES. The generator is what the CF's
-- quotient records; the arity is its grade (the number of args it consumes).
------------------------------------------------------------------------
data Gen-SKI : Set where      -- ⟦shape:1e383a13 gI,gK,gS⟧
  gI gK gS : Gen-SKI
