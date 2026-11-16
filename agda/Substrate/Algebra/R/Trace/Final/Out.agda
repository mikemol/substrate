------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.Out
--
-- Defines: out
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.Out where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace



------------------------------------------------------------------------
-- The structure map of RealTrace and its inverse — Lambek's lemma: the final
-- coalgebra is a FIXED POINT, RealTrace ≅ ℕ × RealTrace.
------------------------------------------------------------------------

out : RealTrace → ℕ × RealTrace
out x = head x , tail x
