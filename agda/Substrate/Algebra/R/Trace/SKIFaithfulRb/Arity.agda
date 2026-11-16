------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
--
-- Defines: arity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen



-- the arity of each generator = its GRADE (I:1, K:2, S:3).
arity : Gen-SKI → ℕ
arity gI = 1
arity gK = 2
arity gS = 3
