------------------------------------------------------------------------
-- Substrate.Algebra.Q.Arithmetic
--
-- Q5 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- ℚ arithmetic: addition, negation, multiplication. Division is
-- deferred per [[feedback-coalgebraic-not-consumer-driven]]
-- (requires a NonZero numerator predicate on the divisor).
--
-- Results are NOT auto-reduced; Q4 supplies the reduction
-- predicate, and a future arc supplies the reduce function if
-- a consumer needs canonical form.
--
-- ℤ arithmetic helpers (-ℤ, +ℤ, *ℤ) are defined inline here
-- since they're scoped to the ℚ arc; if a downstream needs them
-- standalone, factor out to Substrate.Algebra.Z.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Arithmetic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)

------------------------------------------------------------------------
-- 1. ℤ addition.
--
-- Case split on signs. Uses ℕ subtraction (`_∸_`) at the
-- different-sign cases — substrate's basic Data.Nat operation.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (_∸_; _<?_)
open import Substrate.Foundation.Negation using (yes; no)

_+ℤ_ : ℤ → ℤ → ℤ
(+ m)    +ℤ (+ n)    = + (m + n)
(+ m)    +ℤ (-suc n) with m <? suc n
... | yes _ = -suc (n ∸ m)
... | no  _ = + (m ∸ suc n)
(-suc m) +ℤ (+ n)    with n <? suc m
... | yes _ = -suc (m ∸ n)
... | no  _ = + (n ∸ suc m)
(-suc m) +ℤ (-suc n) = -suc (suc (m + n))

------------------------------------------------------------------------
-- 2. ℤ multiplication.
------------------------------------------------------------------------

_*ℤ_ : ℤ → ℤ → ℤ
(+ m)    *ℤ (+ n)    = + (m * n)
(+ zero) *ℤ (-suc n) = + zero
(+ suc m) *ℤ (-suc n) = -suc (m + n + m * n)
  -- (suc m) * (suc n) = suc m + suc m * n = suc (m + suc m * n) = suc (m + n + m*n)
  -- Negated: -suc (m + n + m*n)
(-suc m) *ℤ (+ zero) = + zero
(-suc m) *ℤ (+ suc n) = -suc (m + n + m * n)
(-suc m) *ℤ (-suc n) = + (suc m * suc n)

------------------------------------------------------------------------
-- 3. ℚ negation.
------------------------------------------------------------------------

-ℚ_ : ℚ → ℚ
-ℚ q = mkℚ (-ℤ (num q)) (den-1 q)

------------------------------------------------------------------------
-- 4. ℚ addition.
--
-- a/b + c/d = (a*d + c*b) / (b*d). All in terms of stored den-1
-- with the actual denominators reconstructed via suc.
------------------------------------------------------------------------

_+ℚ_ : ℚ → ℚ → ℚ
p +ℚ q =
  let a  = num p
      b₋ = den-1 p
      c  = num q
      d₋ = den-1 q
      b  = suc b₋
      d  = suc d₋
      n  = (a *ℤ (+ d)) +ℤ (c *ℤ (+ b))
      -- new denominator: b * d = suc b₋ * suc d₋
      -- den-1-of-product = b * d ∸ 1 = pred (b * d)
      d' = b * d
  in mkℚ n (d' ∸ 1)

------------------------------------------------------------------------
-- 5. ℚ multiplication.
--
-- (a/b) * (c/d) = (a*c) / (b*d).
------------------------------------------------------------------------

_*ℚ_ : ℚ → ℚ → ℚ
p *ℚ q =
  let a  = num p
      b₋ = den-1 p
      c  = num q
      d₋ = den-1 q
      b  = suc b₋
      d  = suc d₋
      n  = a *ℤ c
      d' = b * d
  in mkℚ n (d' ∸ 1)

------------------------------------------------------------------------
-- 6. ℚ subtraction (via addition + negation).
------------------------------------------------------------------------

_-ℚ_ : ℚ → ℚ → ℚ
p -ℚ q = p +ℚ (-ℚ q)

------------------------------------------------------------------------
-- 7. Capstone for Q5.
--
-- ℚ +/−/* defined. Division is deferred (needs the divisor's
-- numerator to be NonZero). Q6 supplies ordering; results from
-- Q5 are in unreduced form (Q4's reduce can be applied if
-- canonical-form needed).
------------------------------------------------------------------------
