------------------------------------------------------------------------
-- Substrate.Algebra.Z.Arithmetic
--
-- ℤ arithmetic — the operand type for "changing the types" that EEA
-- operates on. This module is now a RE-EXPORT BARREL: each canonical
-- operator lives in its own file (carrier-locality policy — a canonical
-- operator is not buried in a generic bucket; see
-- scratch/carrier_locality_policy.md), and this module aggregates them so the
-- public interface `Substrate.Algebra.Z.Arithmetic` is unchanged: MEASURED
-- 2026-09-26, 4 importers remain (~200 before decomposition rewired consumers
-- to the leaves; most later moved off the barrel onto the leaves directly too):
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

-- ⚑ Ⓑ1a: the three `public` re-exports are STRIPPED (the ban).  Consumers are
-- rebound at the owning leaf by `scope_fix --seed`, which recovers the name→owner
-- map from this file AT HEAD — a stripped operator surfaces as
-- [NoParseForApplication], which names no owner, so the map cannot come from the
-- error text.  Once every consumer is rebound this module is dead surface and
-- `split_pipeline --retire` deletes it.
