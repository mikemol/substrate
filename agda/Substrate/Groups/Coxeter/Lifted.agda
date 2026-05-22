------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Lifted
--
-- L-arc capstone — the "expose generator, not orbit" toolkit for
-- Coxeter group instances.
--
-- ===================================================================
-- TWO COMPLEMENTARY LIFTERS
-- ===================================================================
--
-- 1. `Substrate.Groups.Coxeter.SameCanonical` — generic decidable
--    equality on Words from decidable equality on Gen. Collapses
--    the n² Cayley table that each ZN-Coxeter file had for
--    `same-canonical`.
--
-- 2. `Substrate.Groups.Coxeter.CanonicalCover` — polymorphic
--    n-refls tuples (2-refls through 24-refls). The "named Cayley-
--    table refl payload" primitive that each per-group module's
--    Axioms/Lifted file aliases for UNIFORM-OUTPUT proofs (where
--    every Cayley case reduces to the same `X ≡ X`).
--
-- ===================================================================
-- WHEN THE PATTERNS APPLY
-- ===================================================================
--
-- SameCanonical lifter — applies WHENEVER deciding `Canonical w₁ →
-- Canonical w₂ → Dec (w₁ ≡ w₂)`. The canonical witnesses are unused
-- in the decision (which depends only on the Word equality), so the
-- n²-case enumeration collapses to one `Word-≡-Dec gen-≟` call.
-- Used by: Z2, Z3, Z4, V4-Coxeter (so far).
--
-- CanonicalCover (n-refls) — applies WHEN every Cayley case reduces
-- to the SAME `X ≡ X` shape. Example: V₄'s `·-self-inverse-Word`
-- because every canonical c has c · c ≡ [] (all 4 cases share
-- output []). Each Coxeter group's Axioms/Lifted module supplies
-- its own per-group canonical-cover-Group combinator.
--
-- NOT applicable when each Cayley case has a DIFFERENT propositional
-- output. Examples: bivector-to-tensor-symmetric (each (i,j) cell
-- depends on different free variables a,b,c,d,e,f); Cardinality
-- bijection round-trips (each constructor has its own LHS=RHS pair);
-- S3-on-V4 homomorphism proofs (each V₄ × V₄ position has its own
-- result). For these, the explicit enumeration remains the
-- substrate-honest surface.
--
-- ===================================================================
-- L-ARC SAVINGS TABLE
-- ===================================================================
--
--   File                    Was       Now            Δ
--   Z2-Coxeter              4 refl    1 line lifter  -3
--   Z3-Coxeter              9 refl    1 line lifter  -8
--   Z4-Coxeter             16 refl    1 line lifter  -15
--   V4-Coxeter             16 refl    1 line lifter  -15
--                                                    -----
--                                                    -41 lines
--
-- Plus the polymorphic n-refls library (used by V4's
-- `·-self-inverse-Word` via the canonical-cover combinator).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Lifted where

open import Substrate.Groups.Coxeter.SameCanonical  public
open import Substrate.Groups.Coxeter.CanonicalCover public
