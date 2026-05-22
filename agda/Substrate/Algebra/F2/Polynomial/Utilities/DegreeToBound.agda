------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities.DegreeToBound
--
-- degree→bound: convert a Maybe-ℕ degree to a ℕ length bound.
--   degree-bound p = nothing → 0;  just k → suc k.
-- Bridges the two encodings: degree (Maybe ℕ) for comparison vs
-- degree-bound (ℕ) for length arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities.DegreeToBound where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)

degree→bound : Maybe ℕ → ℕ
degree→bound nothing  = 0
degree→bound (just k) = suc k
