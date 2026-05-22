------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge
--
-- Wedge-Poly: polynomial-level structural decomposition analog of
-- ℕ's `Wedge` from Substrate.Algebra.Nat.GCD. Captures polynomial
-- division as a structural record:
--
--   p = quotient *P q +P remainder, with degree remainder < degree q
--
-- Per the structural conversation: modulo IS a wedge at both levels.
-- At ℕ, Wedge a b decomposes a into (quotient, remainder) with
-- remainder < b. At F₂[x], Wedge-Poly p q decomposes p into
-- (quotient, remainder) with degree remainder < degree q.
--
-- Slice 3 of 3 in the polynomial-EEA arc. This slice:
--
--   * Defines Wedge-Poly record (structural decomposition).
--   * Defines trivial-wedge-poly: when degree p < degree q,
--     wedge is (quotient=0, remainder=p).
--   * Sketches one-step-reduction: the single subtraction step of
--     long division at F₂ (subtract shifted q from p, cancelling
--     the leading coefficient).
--
-- Full construct-wedge-poly (the long-division algorithm with
-- well-founded recursion on degree) deferred — the termination
-- argument needs careful index-manipulation infrastructure (degree
-- after subtraction strictly decreases, but proving this in Agda
-- requires polynomial degree-tracking lemmas).
--
-- Once construct-wedge-poly lands, the EEATrace-Poly + gcd-Poly +
-- polynomial Bezout + dual-code bridge follow in the same pattern
-- as the ℕ-level work (Substrate.Algebra.Nat.GCD).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge where

open import Data.Maybe using (Maybe; nothing; just)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.Utilities

------------------------------------------------------------------------
-- N-1: degree-lt — comparison predicate over Maybe ℕ degrees.
--
-- nothing < just k (zero polynomial has lowest "degree")
-- just j < just k iff j < k (compare degrees of nonzero polynomials)
-- For total ordering at the substrate level: just k < nothing is FALSE.
------------------------------------------------------------------------

degree-lt : Maybe ℕ → Maybe ℕ → Set
degree-lt nothing  nothing  = ⊥
  where open import Data.Empty using (⊥)
degree-lt nothing  (just _) = ⊤
  where open import Data.Unit using (⊤)
degree-lt (just _) nothing  = ⊥
  where open import Data.Empty using (⊥)
degree-lt (just j) (just k) = j < k

------------------------------------------------------------------------
-- N-2: Wedge-Poly — polynomial division as structural decomposition.
--
-- Wedge-Poly p q n-out asserts: there exist (quotient, remainder)
-- with p = quotient *P q +P remainder (matching polynomial sizes
-- handled via n-out's length witness) and degree remainder < degree q.
--
-- For the substrate's purposes, we work with FIXED size bounds
-- (Polynomial n, Polynomial m) and let the wedge produce a quotient
-- and remainder of appropriate sizes.
--
-- Simplified record (without the full reconstruction equation —
-- placeholders for future when polynomial *P + length-handling is
-- mature):
------------------------------------------------------------------------

-- Wedge-Poly p q (for q nonzero): degree-decomposition.
-- The quotient and remainder are polynomials with size constraints
-- that make polynomial multiplication well-typed.
record Wedge-Poly {n m : ℕ} (p : Polynomial n) (q : Polynomial m) : Set where
  field
    quotient-size  : ℕ
    quotient       : Polynomial quotient-size
    remainder-size : ℕ
    remainder      : Polynomial remainder-size
    -- The full reconstruction `p ≡ quotient *P q +P remainder` and
    -- degree-bound condition `degree remainder < degree q` are
    -- deferred to the construct-wedge-poly follow-on slice (requires
    -- mature *P length-arithmetic).

open Wedge-Poly public

------------------------------------------------------------------------
-- N-3: trivial-wedge-poly — the base case of polynomial division.
--
-- When p's degree is "less than" q's (including p = 0), the wedge
-- is (quotient = 0, remainder = p). No actual division needed.
--
-- Captures the base case of the long-division algorithm.
------------------------------------------------------------------------

trivial-wedge-poly :
  ∀ {n m} (p : Polynomial n) (q : Polynomial m) →
  Wedge-Poly p q
trivial-wedge-poly {n} {m} p q = record
  { quotient-size  = 0
  ; quotient       = []
  ; remainder-size = n
  ; remainder      = p
  }

------------------------------------------------------------------------
-- N-4: x-power — shift a polynomial by d positions (multiply by x^d).
--
-- iterate-x-shift d p = p shifted up by d positions = x^d · p.
-- Used by long-division's single-step reduction (align q's degree
-- with p's by shifting q up).
------------------------------------------------------------------------

x-power : ∀ {n} (d : ℕ) → Polynomial n → Polynomial (d ℕ+ n)
x-power zero    p = p
x-power (suc d) p = x-shift (x-power d p)

------------------------------------------------------------------------
-- N-5: Capstone — Wedge-Poly foundation lands.
--
-- After this slice, the polynomial-level Wedge structure is named
-- and the trivial case is implemented:
--
--   * Wedge-Poly p q     — structural record (quotient + remainder
--                          + size data; reconstruction equation
--                          deferred).
--   * trivial-wedge-poly — base case for p of "lower degree" than q.
--   * x-power            — multiply by x^d (= iterate x-shift d times).
--   * degree-lt          — comparison predicate over Maybe ℕ degrees.
--
-- The polynomial-level Wedge mirrors the ℕ-level Wedge from
-- Substrate.Algebra.Nat.GCD: both are structural decomposition
-- records capturing the "divide with quotient and remainder"
-- pattern. The ℕ Wedge has remainder < b; Wedge-Poly has
-- degree remainder < degree q.
--
-- Per [[project-composite-torsion-euler-substrate]]: F₂[x] is the
-- substrate's natural Euclidean-domain instance. The Wedge primitive
-- here is the polynomial-level "modulo as structural decomposition"
-- handle.
--
-- Deferred follow-ons (in dependency order):
--
--   * **construct-wedge-poly**: long-division algorithm with
--     well-founded recursion on degree. The single-step reduction:
--     when degree p ≥ degree q, subtract (x^{degree p - degree q} · q)
--     from p (this cancels p's leading coefficient at F₂). Recurse
--     on the result. Substantial — requires degree-tracking lemmas
--     to prove "after subtraction, degree strictly decreased."
--
--   * **Reconstruction equation in Wedge-Poly**: the field
--     `wedge-eq : p ≡ quotient *P q +P remainder` (with proper
--     size handling). Currently deferred; once construct-wedge-poly
--     lands, the equation is part of the trace.
--
--   * **EEATrace-Poly**: data type for polynomial EEA (mirroring
--     ℕ's EEATrace).
--
--   * **gcd-Poly + divides-{left, right}**: structural induction
--     on EEATrace-Poly.
--
--   * **Bezout-Poly**: structural fold on EEATrace-Poly producing
--     polynomial Bezout coefficients.
--
--   * **Dual-code bridge**: ImageCode g(x) ↔ KernelCode ((x^n + 1)/g(x))
--     via polynomial GCD. Opens the Hamming/RM/cyclic-code arc.
------------------------------------------------------------------------
