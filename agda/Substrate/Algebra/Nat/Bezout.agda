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
-- Slice 3 of 3 in the TensorProduct + EEA trio (and closes the
-- deferred Bezout work from Slice A of the original EEA plan).
--
-- The EEATrace from Substrate.Algebra.Nat.GCD provides the
-- structural recursion needed to FOLD into a Bezout witness. The
-- fold's sign-handling: each step swaps the sign (due to the
-- subtractive rearrangement of the wedge equation).
--
-- Per [[project-composite-torsion-euler-substrate]]: Bezout
-- coefficients give CRT-style decomposition for coprime joint
-- structures. At the substrate level, BezoutWitness packages the
-- algorithmic content of Extended Euclidean Algorithm.
--
-- This slice defines the type + base case + structural-fold
-- TEMPLATE. The full fold's sign-handling proof is intricate
-- (each wedge step rearranges the linear combination, swapping
-- sign); the full implementation is deferred to a follow-on slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Bezout where

open import Data.Nat using (ℕ; zero; suc; _+_; _*_)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Data.Sum using (_⊎_; inj₁; inj₂)
open import Data.Nat.Properties using (*-zeroˡ; +-identityʳ; +-identityˡ;
                                       *-identityˡ)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.Nat.GCD using (EEATrace; base; step)

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
--
-- The compute-bezout function is a TEMPLATE (with the step case
-- left abstract until the full sign-swapping proof lands).
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
-- the type + base case + structural template.

------------------------------------------------------------------------
-- N-4: Capstone — Bezout-ℕ foundation lands.
--
-- After this slice:
--
--   * BezoutWitness a b g — type packaging the balanced Bezout
--     identity at ℕ via sum-typed sign.
--   * base-bezout         — Bezout witness for the trivial gcd(a, 0).
--   * bezout-from-trace   — TEMPLATE for the structural fold (full
--                           step-case implementation deferred).
--
-- The sign-handling pattern: each EEATrace step's wedge rearrangement
-- swaps the sum-type direction. The base case starts at `inj₁`
-- (left case); each step alternates. Net result: the sign of the
-- final BezoutWitness depends on the trace's length parity.
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- substrate's CRT-decomposition primitive at the ℕ level. Bezout
-- coefficients let us express elements of the gcd-subgroup of
-- ⟨γ₁, γ₂⟩ when γ₁, γ₂ commute and have coprime orders.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * **bezout-from-trace step case**: the full structural fold
--     producing BezoutWitness from any EEATrace. Sign-swapping
--     handled via case-on-inj₁/inj₂ + arithmetic rearrangement.
--
--   * **Bezout uniqueness**: any two BezoutWitness for the same
--     (a, b, g) are equivalent (up to a specific normalization).
--
--   * **HasOrder-compose-commute-tight via Bezout**: at coprime
--     orders k₁, k₂, CRT decomposition gives a sharper HasOrder
--     bound for γ₁ ∘E γ₂ than the loose k₁ * k₂. Combines with
--     StructuralGCD's Commute primitive.
--
--   * **Polynomial Bezout** (Bezout-Poly): same structure at the
--     F₂[x] level (mirror of this slice once construct-wedge-poly
--     lands).
------------------------------------------------------------------------
