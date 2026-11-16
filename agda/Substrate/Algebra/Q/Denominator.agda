------------------------------------------------------------------------
-- Substrate.Algebra.Q.Denominator
--
-- Defines: denominator
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Denominator where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Rat



------------------------------------------------------------------------
-- 2. Accessors.
------------------------------------------------------------------------

denominator : ℚ → ℕ
denominator q = suc (den-1 q)
