------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Bezout.Properties
--
-- PROOF MODULE for Substrate.Algebra.Nat.Bezout (per the def/proof
-- separation policy, scratch/def_proof_separation_policy.md).
--
-- The proof-bearing Bezout constructions: the base-case witness and the
-- structural-fold TEMPLATE from an EEATrace.  These import the
-- arithmetic proof machinery (Nat.Properties); keeping them OUT of the
-- definition module Substrate.Algebra.Nat.Bezout means a consumer that
-- only needs the BezoutWitness type never deserializes this closure.
--
-- Per [[project-composite-torsion-euler-substrate]]: Bezout
-- coefficients give CRT-style decomposition for coprime joint
-- structures.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Bezout.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-identityˡ)
open import Substrate.Foundation.Nat.Properties.Mul using (*-zeroˡ; *-identityˡ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Algebra.Nat.Bezout using (BezoutWitness)

------------------------------------------------------------------------
-- N-2: Base-case Bezout — for the trivial gcd(a, 0) = a.
--
-- At gcd(a, 0) = a: take s = 1, t = 0. Then:
--   s · a = 1 · a = a
--   t · b + g = 0 · 0 + a = a
-- So s · a ≡ t · b + g (left case).
------------------------------------------------------------------------

base-bezout : (a : ℕ) → BezoutWitness a 0 a
base-bezout a = record
  { s  = 1
  ; t  = 0
  ; eq = inj₁ eq-proof
  }
  where
    eq-proof : 1 * a ≡ 0 * 0 + a
    eq-proof = trans (*-identityˡ a) (sym (+-identityˡ a))

------------------------------------------------------------------------
-- N-3: BezoutWitness from EEATrace — the structural fold (template).
--
-- Given an EEATrace a b g, fold over the trace to produce a
-- BezoutWitness a b g.
--
-- Base case: trace = base a → BezoutWitness a 0 a = base-bezout a.
--
-- Step case: trace = step b w sub-trace → use IH on sub-trace
-- (BezoutWitness (suc b) (remainder w) g), then derive
-- BezoutWitness a (suc b) g via:
--
--   From IH: s' · suc b = t' · remainder w + g  (or swapped)
--   From wedge: a ≡ quotient w · suc b + remainder w
--               ⟹ remainder w = a - quotient w · suc b
--
--   Substitution gives a new linear combination of (a, suc b) with g.
--   The sign of the new Bezout swaps relative to the sub-trace.
--
-- Full step-case proof is intricate (requires careful arithmetic
-- with ℕ subtraction handled via the sum type's sign). Sketched
-- below; the substantive derivation is deferred.
------------------------------------------------------------------------

-- bezout-from-trace : ∀ {a b g} → EEATrace a b g → BezoutWitness a b g
-- bezout-from-trace (base a) = base-bezout a
-- bezout-from-trace (step b w sub-trace) = ?
--   -- Sketch: use IH on sub-trace, apply the wedge equation,
--   -- rearrange to express g as a linear combination of (a, suc b).
--   -- Sign swaps; coefficients (s_new, t_new) computed from
--   -- (s_old, t_old, quotient w).
--
-- Deferred: the substantive arithmetic proof. Current slice provides
-- the type (in Bezout.agda) + base case + structural template.
