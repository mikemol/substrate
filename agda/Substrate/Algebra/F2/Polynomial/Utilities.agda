------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities
--
-- Polynomial utilities for division + EEA over F₂[x]. File-per-lemma:
--
--   Utilities.IsZeroPoly          — predicate + decision procedure
--   Utilities.LeadingPosition     — topmost nonzero index (Maybe ℕ)
--   Utilities.LeadingCoefficient  — 𝟙 for nonzero, 𝟘 for zero (total)
--   Utilities.Degree              — Maybe-ℕ degree (alias of leading-position)
--   Utilities.DegreeToBound       — Maybe ℕ → ℕ length-bound conversion
--
-- Stdlib audit: Data.Maybe → Substrate.Foundation.Maybe;
-- Data.Empty/Data.Unit → Substrate.Foundation.Empty/Unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities where

open import Substrate.Algebra.F2.Polynomial.Utilities.IsZeroPoly         public
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition    public
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingCoefficient public
open import Substrate.Algebra.F2.Polynomial.Utilities.Degree             public
open import Substrate.Algebra.F2.Polynomial.Utilities.DegreeToBound      public
