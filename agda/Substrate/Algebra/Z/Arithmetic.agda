------------------------------------------------------------------------
-- Substrate.Algebra.Z.Arithmetic
--
-- ℤ arithmetic — the operand type for "changing the types" that EEA
-- operates on. This module is now a RE-EXPORT BARREL: each canonical
-- operator lives in its own file (carrier-locality policy — a canonical
-- operator is not buried in a generic bucket; see
-- scratch/carrier_locality_policy.md), and this module aggregates them so the
-- public interface `Substrate.Algebra.Z.Arithmetic` (and its ~200 importers)
-- is unchanged:
--
--   _⊖_ , _+ℤ_   →  Substrate.Algebra.Z.Add
--   _*ℤ_         →  Substrate.Algebra.Z.Mul
--   _-ℤ_         →  Substrate.Algebra.Z.Sub
--
-- Addition routes through the truncated difference _⊖_ : ℕ → ℕ → ℤ (the one
-- place sign appears); multiplication is sign-magnitude on the two-constructor
-- (+_ / -suc_) form. Definitions only (laws live in Z.Properties).
--
-- Why ℤ: the Bézout bridge s·a + t·b = gcd has SIGNED coefficients; over
-- ℤ the Euclidean back-substitution is clean ring algebra (no ℕ-balanced
-- sign-tag case-split). See [[project_center_free_universal_property]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Arithmetic where

open import Substrate.Algebra.Z.Add public using (_⊖_; _+ℤ_)
open import Substrate.Algebra.Z.Mul public using (_*ℤ_)
open import Substrate.Algebra.Z.Sub public using (_-ℤ_)
