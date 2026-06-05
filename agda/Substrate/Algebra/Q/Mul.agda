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
-- ℤ arithmetic (_+ℤ_, _*ℤ_) is the CANONICAL Substrate.Algebra.Z.Arithmetic
-- — imported, not re-defined. (Carrier-locality: a ℤ operator lives in the
-- ℤ home directory; the ℚ folder must not fork it. The full ℤ ring laws
-- proven about these ops, Substrate.Algebra.Z.Properties.MulFull, therefore
-- apply directly to ℚ's numerator arithmetic.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Arithmetic where

open import Substrate.Foundation.Nat using (suc; _*_; _∸_)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)

------------------------------------------------------------------------
-- 1. ℚ negation.
------------------------------------------------------------------------

-ℚ_ : ℚ → ℚ
-ℚ q = mkℚ (-ℤ (num q)) (den-1 q)

------------------------------------------------------------------------
-- 2. ℚ addition.
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
      d' = b * d
  in mkℚ n (d' ∸ 1)

------------------------------------------------------------------------
-- 3. ℚ multiplication.
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
-- 4. ℚ subtraction (via addition + negation).
------------------------------------------------------------------------

_-ℚ_ : ℚ → ℚ → ℚ
p -ℚ q = p +ℚ (-ℚ q)

------------------------------------------------------------------------
-- 5. Capstone for Q5.
--
-- ℚ +/−/* defined over the canonical ℤ ops. Division is deferred
-- (needs the divisor's numerator NonZero). Q6 supplies ordering;
-- results are unreduced (Q4's reduce can be applied if canonical
-- form is needed).
------------------------------------------------------------------------
