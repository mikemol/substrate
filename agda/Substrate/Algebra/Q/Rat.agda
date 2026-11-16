------------------------------------------------------------------------
-- Substrate.Algebra.Q.Rat
--
-- Defines: den-1, mkℚ, num, ℚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Rat where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int



------------------------------------------------------------------------
-- 1. The ℚ record.
------------------------------------------------------------------------

record ℚ : Set where
  constructor mkℚ
  field
    num   : ℤ
    den-1 : ℕ

open ℚ public
