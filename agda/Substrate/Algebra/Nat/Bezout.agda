------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Bezout
--
-- Bezout's identity at ℕ: gcd(a, b) = s · a + t · b at ℤ; at ℕ
-- (without negatives), we reformulate as a balanced equation with
-- the sign captured via a sum type.
--
-- BezoutWitness a b g := Σ[ s, t : ℕ ] (s · a ≡ t · b + g  ⊎  t · b ≡ s · a + g)
--
-- The two sides of the sum capture which way the +g goes.
--
-- DEFINITION MODULE (per the def/proof separation policy,
-- scratch/def_proof_separation_policy.md): this file exports ONLY the
-- BezoutWitness datatype, so a consumer that merely needs the type pays
-- no proof closure.  The proof-bearing constructions (base-bezout,
-- the EEATrace fold) live in Substrate.Algebra.Nat.Bezout.Properties,
-- which is what drags Nat.Properties.  Keeping that import out of THIS
-- module is the whole point: def-consumers (e.g. PrimitiveInstances)
-- stop deserializing arithmetic proofs they never use.
--
-- Per [[project-composite-torsion-euler-substrate]]: Bezout
-- coefficients give CRT-style decomposition for coprime joint
-- structures. At the substrate level, BezoutWitness packages the
-- algorithmic content of Extended Euclidean Algorithm.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Bezout where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Sum using (_⊎_)
open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- N-1: BezoutWitness — the Bezout identity at ℕ.
--
-- Captures the "balanced" Bezout equation:
--   s · a ≡ t · b + g          (left case: s·a is the "bigger side")
--   OR
--   t · b ≡ s · a + g          (right case: t·b is the "bigger side")
--
-- At ℤ, these merge into s · a + t · b = g via signed coefficients.
-- At ℕ, the sign is captured by which inj of the sum type.
------------------------------------------------------------------------

record BezoutWitness (a b g : ℕ) : Set where
  field
    s : ℕ
    t : ℕ
    eq : (s * a ≡ t * b + g) ⊎ (t * b ≡ s * a + g)

open BezoutWitness public
