------------------------------------------------------------------------
-- Substrate.Algebra.Q.Arithmetic
--
-- Q5 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- This module is now a RE-EXPORT BARREL: each canonical ℚ operator lives in
-- its own file (carrier-locality policy — a canonical operator is not buried
-- in a generic bucket; see scratch/carrier_locality_policy.md), and this
-- module aggregates them so the public interface
-- `Substrate.Algebra.Q.Arithmetic` (and its importers) is unchanged:
--
--   -ℚ_   →  Substrate.Algebra.Q.Neg
--   _+ℚ_  →  Substrate.Algebra.Q.Add
--   _*ℚ_  →  Substrate.Algebra.Q.Mul
--   _-ℚ_  →  Substrate.Algebra.Q.Sub
--
-- ℤ arithmetic (_+ℤ_, _*ℤ_) is the CANONICAL Substrate.Algebra.Z.Arithmetic
-- — imported, not re-defined — so the full ℤ ring laws
-- (Substrate.Algebra.Z.Properties.MulFull) apply directly to ℚ's numerator
-- arithmetic. Division is deferred (needs a NonZero numerator predicate);
-- results are unreduced (Q4's reduce can be applied if canonical form needed).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Arithmetic where

open import Substrate.Algebra.Q.Neg public using (-ℚ_)
open import Substrate.Algebra.Q.Add public using (_+ℚ_)
open import Substrate.Algebra.Q.Mul public using (_*ℚ_)
open import Substrate.Algebra.Q.Sub public using (_-ℚ_)
