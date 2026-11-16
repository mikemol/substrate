------------------------------------------------------------------------
-- Substrate.Algebra.Z.ZeroInt
--
-- Defines: 0ℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.ZeroInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int



------------------------------------------------------------------------
-- 2. Named constants.
------------------------------------------------------------------------

0ℤ : ℤ
0ℤ = + 0
