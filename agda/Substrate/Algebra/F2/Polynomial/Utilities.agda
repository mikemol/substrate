------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities
--
-- Polynomial-level utilities preparing for polynomial division +
-- EEA over F₂[x]: zero-detection, leading-coefficient extraction,
-- precise-degree (via Maybe ℕ for zero polynomial), and helper
-- predicates.
--
-- Slice 2 of 3 in the polynomial-EEA arc:
--   Slice 1: outer + anti-diag-sum (polynomial multiplication)
--   Slice 2: utilities (THIS SLICE) — building blocks for division
--   Slice 3: Wedge-Poly + polynomial long division
--
-- At F₂, the leading coefficient of any nonzero polynomial is 𝟙
-- (since coefficients are in {𝟘, 𝟙} and the leading is the topmost
-- nonzero). This simplifies the polynomial division algorithm at F₂:
-- no "leading-coefficient ratio" arithmetic needed — every step
-- just subtracts a shifted q from p.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Data.Maybe using (Maybe; nothing; just)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)
open import Substrate.Foundation.Negation using (Dec; yes; no)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial

------------------------------------------------------------------------
-- N-1: is-zero-poly — decidable test for zero polynomial.
--
-- A polynomial is zero iff all coefficients are 𝟘. Decidable via
-- recursive check; constructive Yes/No witness.
------------------------------------------------------------------------

is-zero-poly : ∀ {n} → Polynomial n → Set
is-zero-poly []      = ⊤
  where open import Data.Unit using (⊤)
is-zero-poly (𝟘 ∷ p) = is-zero-poly p
is-zero-poly (𝟙 ∷ _) = ⊥
  where open import Data.Empty using (⊥)

is-zero-poly? : ∀ {n} (p : Polynomial n) → Dec (is-zero-poly p)
is-zero-poly? []        = yes _
  where open import Data.Unit using (tt)
is-zero-poly? (𝟘 ∷ p)   = is-zero-poly? p
is-zero-poly? (𝟙 ∷ _)   = no λ ()

------------------------------------------------------------------------
-- N-2: leading-position — find the position of the topmost nonzero
-- coefficient (or Nothing if zero polynomial).
--
-- For p : Polynomial n, scans coefficients to find the highest index
-- i where p[i] = 𝟙. Returns just i, or nothing if all coefficients
-- are zero.
--
-- Implementation: scan from the head, tracking the "best so far"
-- highest position with a nonzero coefficient.
------------------------------------------------------------------------

-- Helper: track best-seen leading position via accumulator.
leading-position-acc : ∀ {n} → Polynomial n → ℕ → Maybe ℕ → Maybe ℕ
leading-position-acc []        _   best = best
leading-position-acc (𝟘 ∷ p)   pos best = leading-position-acc p (suc pos) best
leading-position-acc (𝟙 ∷ p)   pos _    = leading-position-acc p (suc pos) (just pos)

leading-position : ∀ {n} → Polynomial n → Maybe ℕ
leading-position p = leading-position-acc p 0 nothing

------------------------------------------------------------------------
-- N-3: leading-coefficient — the coefficient at the leading position.
--
-- For a nonzero polynomial, this is always 𝟙 at F₂ (by definition of
-- "leading nonzero"). For the zero polynomial, returns 𝟘.
--
-- This convention makes leading-coefficient total. At F₂, the
-- distinction is just nonzero (= 𝟙) vs zero (= 𝟘).
------------------------------------------------------------------------

leading-coefficient : ∀ {n} → Polynomial n → F₂
leading-coefficient p with leading-position p
... | nothing  = 𝟘   -- zero polynomial
... | just _   = 𝟙   -- nonzero polynomial: leading coeff is 𝟙 at F₂

------------------------------------------------------------------------
-- N-4: degree — precise degree using Maybe ℕ.
--
-- degree p = nothing for the zero polynomial (degree -∞ convention);
-- degree p = just k for a nonzero polynomial with leading position k
-- (i.e., the polynomial = c₀ + c₁x + ... + c_k x^k with c_k = 𝟙).
--
-- For comparison purposes: nothing < just k for any k (zero is the
-- "smallest").
------------------------------------------------------------------------

degree : ∀ {n} → Polynomial n → Maybe ℕ
degree = leading-position

------------------------------------------------------------------------
-- N-5: degree-bound vs degree relationship.
--
-- degree-bound (from the base Polynomial file) gives "leading
-- position + 1" for nonzero polynomials, 0 for zero. degree (this
-- file) gives "leading position" wrapped in Just, or Nothing.
--
-- For a nonzero polynomial with leading at position k:
--   degree-bound p = suc k (= k + 1)
--   degree p       = just k
--
-- The relationship: degree-bound p = case degree p of
--                                       nothing → 0
--                                       just k  → suc k
--
-- Both encodings have their uses; degree (Maybe ℕ) is cleaner for
-- comparison; degree-bound (ℕ) is cleaner for length arithmetic.
------------------------------------------------------------------------

-- Convert degree (Maybe ℕ) to degree-bound (ℕ).
degree→bound : Maybe ℕ → ℕ
degree→bound nothing  = 0
degree→bound (just k) = suc k

------------------------------------------------------------------------
-- N-6: Capstone — polynomial utilities for slice 3.
--
-- After this slice:
--
--   * is-zero-poly  / is-zero-poly?   — decidable zero test
--   * leading-position                — Maybe ℕ for topmost nonzero
--   * leading-coefficient             — 𝟙 for nonzero, 𝟘 for zero
--   * degree                          — alias for leading-position
--   * degree-bound (existing)         — leading + 1, or 0 for zero
--   * degree→bound                    — convert Maybe ℕ to ℕ
--
-- Building blocks ready for slice 3 (Wedge-Poly + polynomial
-- division). The simplification at F₂: leading-coefficient is
-- always 𝟙 for nonzero polynomials, so polynomial long division
-- has no leading-coefficient-ratio step — each step is just
-- subtract (= XOR = +ⱽ) of a shifted q.
--
-- Per the structural conversation: zero-polynomial handling is the
-- main subtlety. The Maybe ℕ encoding for degree gives the right
-- structural distinction (Nothing for the zero polynomial = "the
-- additive identity has no degree").
--
-- Path to slice 3 (polynomial division):
--   * Wedge-Poly p q for q nonzero: packages
--     (quotient, remainder, p ≡ quotient *P q +P remainder,
--      degree remainder < degree q).
--   * construct-wedge-poly: long division algorithm. Termination
--     via well-founded recursion on `degree p - degree q` (decreasing
--     by 1 each subtraction step), or on degree p directly (when
--     degree p < degree q, return base case).
------------------------------------------------------------------------
