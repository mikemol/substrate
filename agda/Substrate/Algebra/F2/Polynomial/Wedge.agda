------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge
--
-- Wedge-Poly: polynomial-level structural decomposition analog of
-- ℕ's `Wedge` from Substrate.Algebra.Nat.GCD. File-per-lemma:
--
--   Wedge.WedgePoly          — the Wedge-Poly record (quotient + remainder)
--   Wedge.DegreeLt           — Maybe-ℕ degree comparison
--   Wedge.TrivialWedgePoly   — base case (p of lower degree)
--   Wedge.XPower             — iterated x-shift (multiply by xᵈ)
--
-- Stdlib audit: Data.Maybe → Substrate.Foundation.Maybe;
-- Data.Empty/Data.Unit → Substrate.Foundation.Empty/Unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge where

open import Substrate.Algebra.F2.Polynomial.Wedge.WedgePoly         public
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt          public
open import Substrate.Algebra.F2.Polynomial.Wedge.TrivialWedgePoly  public
open import Substrate.Algebra.F2.Polynomial.Wedge.XPower            public
